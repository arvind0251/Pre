"""
Storage backend using a private Telegram group/channel instead of MongoDB.

How it works:
  - All data lives in memory (self.data) while the bot is running, for
    fast access — same as before, just no external database round-trips.
  - Every AUTOSAVE_INTERVAL seconds (and once more on shutdown), the whole
    in-memory dataset is serialized to JSON and uploaded as a document to
    config.STORAGE_CHAT_ID, replacing the previous backup message there.
  - On startup, connect() looks for that pinned backup document in the
    storage chat and loads it back into memory. If none exists yet
    (first run), it starts with an empty dataset.

Public method names/signatures match the previous MongoDB-backed class
exactly, so no other file in the codebase needs to change.
"""
import json
import os
import asyncio
from time import time

from Elevenyts import config, logger, app, userbot


AUTOSAVE_INTERVAL = 120  # seconds
BACKUP_FILENAME = "database_backup.json"
BACKUP_CAPTION = "📦 Database Backup — do not delete or unpin"


class Storage:
    def __init__(self):
        self.data = {
            "auth": {},              # str(chat_id) -> list[user_id]
            "assistant": {},         # str(chat_id) -> assistant num
            "chats": [],
            "lang": {},              # str(chat_id) -> lang code
            "blacklist_chats": [],
            "blacklist_users": [],
            "maintenance": False,
            "vplay_enabled": config.VIDEO_PLAY,
            "gbanned_users": [],
            "logger": False,
            "cplay": {},             # str(chat_id) -> channel_id
            "autoleave": {},         # str(chat_id) -> bool
            "loop": {},              # str(chat_id) -> mode int
            "play_mode": [],
            "force_mode": [],
            "sudoers": [],
            "users": [],
        }

        # Mirror the same in-memory attributes the old MongoDB class exposed,
        # so any code checking e.g. `db.chats` directly still works.
        self.admin_list = {}
        self.admin_cache_time = {}
        self.active_calls = {}

        self._backup_msg_id: int | None = None
        self._autosave_task: asyncio.Task | None = None
        self._dirty = False

    # ===================== Connection lifecycle =====================
    async def connect(self) -> None:
        """Load the last backup from the storage chat, then start autosaving."""
        if not config.STORAGE_CHAT_ID:
            raise SystemExit(
                "STORAGE_CHAT_ID is not set — this bot stores its data in a "
                "Telegram group instead of MongoDB. Add the bot to a private "
                "group, make it admin, and set STORAGE_CHAT_ID in .env."
            )

        try:
            start = time()
            await self._load_backup()
            logger.info(f"✅ Storage loaded from Telegram group. ({time() - start:.2f}s)")
        except Exception as e:
            logger.warning(f"No existing backup found or failed to load ({type(e).__name__}: {e}) — starting fresh.")

        self._autosave_task = asyncio.create_task(self._autosave_loop())
        logger.info(f"📦 Data cached: {len(self.data['chats'])} chats, {len(self.data['users'])} users.")

    async def close(self) -> None:
        """Save one last time, then stop autosaving."""
        if self._autosave_task:
            self._autosave_task.cancel()
            try:
                await self._autosave_task
            except asyncio.CancelledError:
                pass
        try:
            await self._save()
        except Exception as e:
            logger.error(f"Final storage save failed: {e}")
        logger.info("Storage connection closed.")

    async def _autosave_loop(self) -> None:
        while True:
            await asyncio.sleep(AUTOSAVE_INTERVAL)
            if self._dirty:
                try:
                    await self._save()
                except Exception as e:
                    logger.error(f"Autosave to Telegram group failed: {e}")

    def _mark_dirty(self) -> None:
        self._dirty = True

    async def _load_backup(self) -> None:
        chat = await app.get_chat(config.STORAGE_CHAT_ID)
        pinned = chat.pinned_message
        if not pinned or not pinned.document:
            return  # no backup yet, start fresh

        path = await app.download_media(pinned.document, file_name=f"/tmp/{BACKUP_FILENAME}")
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        for key in self.data:
            if key in loaded:
                self.data[key] = loaded[key]
        self._backup_msg_id = pinned.id
        try:
            os.remove(path)
        except Exception:
            pass

    async def _save(self) -> None:
        tmp_path = f"/tmp/{BACKUP_FILENAME}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

        try:
            msg = await app.send_document(
                config.STORAGE_CHAT_ID,
                tmp_path,
                file_name=BACKUP_FILENAME,
                caption=BACKUP_CAPTION,
                disable_notification=True,
            )
            await app.pin_chat_message(config.STORAGE_CHAT_ID, msg.id, disable_notification=True)

            # Clean up the previous backup message so the chat doesn't fill up
            if self._backup_msg_id and self._backup_msg_id != msg.id:
                try:
                    await app.delete_messages(config.STORAGE_CHAT_ID, self._backup_msg_id)
                except Exception:
                    pass

            self._backup_msg_id = msg.id
            self._dirty = False
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    # CACHE (kept in-memory only, not persisted — same as before)
    async def get_call(self, chat_id: int) -> bool:
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int) -> None:
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int) -> None:
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None) -> bool | None:
        if paused is not None:
            self.active_calls[chat_id] = int(not paused)
        return bool(self.active_calls[chat_id])

    async def get_admins(self, chat_id: int, reload: bool = False) -> list[int]:
        from Elevenyts.helpers._admins import reload_admins

        current_time = time()
        cache_age = current_time - self.admin_cache_time.get(chat_id, 0)

        if chat_id not in self.admin_list or reload or cache_age > 900:
            self.admin_list[chat_id] = await reload_admins(chat_id)
            self.admin_cache_time[chat_id] = current_time
        return self.admin_list[chat_id]

    # AUTH METHODS
    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        return user_id in self.data["auth"].get(str(chat_id), [])

    async def add_auth(self, chat_id: int, user_id: int) -> None:
        users = self.data["auth"].setdefault(str(chat_id), [])
        if user_id not in users:
            users.append(user_id)
            self._mark_dirty()

    async def rm_auth(self, chat_id: int, user_id: int) -> None:
        users = self.data["auth"].get(str(chat_id), [])
        if user_id in users:
            users.remove(user_id)
            self._mark_dirty()

    # ASSISTANT METHODS
    async def set_assistant(self, chat_id: int) -> int:
        from random import randint
        num = randint(1, len(userbot.clients))
        self.data["assistant"][str(chat_id)] = num
        self._mark_dirty()
        return num

    async def get_assistant(self, chat_id: int):
        from Elevenyts import tune

        num = self.data["assistant"].get(str(chat_id))
        if num is None:
            num = await self.set_assistant(chat_id)

        if num > len(userbot.clients):
            num = await self.set_assistant(chat_id)

        return tune.clients[num - 1]

    async def get_client(self, chat_id: int):
        num = self.data["assistant"].get(str(chat_id))
        if num is None:
            await self.get_assistant(chat_id)
            num = self.data["assistant"].get(str(chat_id))

        if num > len(userbot.clients):
            await self.set_assistant(chat_id)
            num = self.data["assistant"].get(str(chat_id))

        available_clients = {}
        if hasattr(userbot, 'one') and userbot.one in userbot.clients:
            available_clients[1] = userbot.one
        if hasattr(userbot, 'two') and userbot.two in userbot.clients:
            available_clients[2] = userbot.two
        if hasattr(userbot, 'three') and userbot.three in userbot.clients:
            available_clients[3] = userbot.three

        return available_clients.get(num)

    # BLACKLIST METHODS
    async def add_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            if chat_id not in self.data["blacklist_chats"]:
                self.data["blacklist_chats"].append(chat_id)
        else:
            if chat_id not in self.data["blacklist_users"]:
                self.data["blacklist_users"].append(chat_id)
        self._mark_dirty()

    async def del_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            if chat_id in self.data["blacklist_chats"]:
                self.data["blacklist_chats"].remove(chat_id)
        else:
            if chat_id in self.data["blacklist_users"]:
                self.data["blacklist_users"].remove(chat_id)
        self._mark_dirty()

    async def get_blacklisted(self, chat: bool = False) -> list[int]:
        return self.data["blacklist_chats"] if chat else self.data["blacklist_users"]

    # CHAT METHODS
    async def is_chat(self, chat_id: int) -> bool:
        return chat_id in self.data["chats"]

    async def add_chat(self, chat_id: int) -> None:
        if not await self.is_chat(chat_id):
            self.data["chats"].append(chat_id)
            self._mark_dirty()

    async def rm_chat(self, chat_id: int) -> None:
        if await self.is_chat(chat_id):
            self.data["chats"].remove(chat_id)
            self._mark_dirty()

    async def get_chats(self) -> list:
        return self.data["chats"]

    # LANGUAGE METHODS
    async def set_lang(self, chat_id: int, lang_code: str):
        self.data["lang"][str(chat_id)] = lang_code
        self._mark_dirty()

    async def get_lang(self, chat_id: int) -> str:
        return self.data["lang"].get(str(chat_id), "en")

    # MAINTENANCE MODE METHODS
    async def set_maintenance(self, status: bool) -> None:
        self.data["maintenance"] = status
        self._mark_dirty()

    async def get_maintenance(self) -> bool:
        return self.data["maintenance"]

    # VPLAY TOGGLE METHODS
    async def get_vplay_enabled(self) -> bool:
        return self.data["vplay_enabled"]

    async def set_vplay_enabled(self, enabled: bool) -> None:
        self.data["vplay_enabled"] = enabled
        self._mark_dirty()

    # GLOBAL BAN METHODS
    async def add_gban(self, user_id: int) -> None:
        if user_id not in self.data["gbanned_users"]:
            self.data["gbanned_users"].append(user_id)
            self._mark_dirty()

    async def del_gban(self, user_id: int) -> None:
        if user_id in self.data["gbanned_users"]:
            self.data["gbanned_users"].remove(user_id)
            self._mark_dirty()

    async def get_gbanned(self) -> list[int]:
        return self.data["gbanned_users"]

    async def is_gbanned(self, user_id: int) -> bool:
        return user_id in self.data["gbanned_users"]

    # LOGGER METHODS
    async def is_logger(self) -> bool:
        return self.data["logger"]

    async def get_logger(self) -> bool:
        return self.data["logger"]

    async def set_logger(self, status: bool) -> None:
        self.data["logger"] = status
        self._mark_dirty()

    # CHANNEL PLAY METHODS
    async def get_cmode(self, chat_id: int) -> int | None:
        return self.data["cplay"].get(str(chat_id))

    async def set_cmode(self, chat_id: int, channel_id: int | None) -> None:
        if channel_id is None:
            self.data["cplay"].pop(str(chat_id), None)
        else:
            self.data["cplay"][str(chat_id)] = channel_id
        self._mark_dirty()

    async def get_group_for_channel(self, channel_id: int) -> int | None:
        for chat_id_str, ch_id in self.data["cplay"].items():
            if ch_id == channel_id:
                try:
                    return int(chat_id_str)
                except ValueError:
                    return None
        return None

    # AUTO LEAVE METHODS
    async def get_autoleave(self, chat_id: int) -> bool:
        return self.data["autoleave"].get(str(chat_id), False)

    async def set_autoleave(self, chat_id: int, enabled: bool) -> None:
        self.data["autoleave"][str(chat_id)] = enabled
        self._mark_dirty()

    # LOOP MODE METHODS
    async def get_loop(self, chat_id: int) -> int:
        return self.data["loop"].get(str(chat_id), 0)

    async def set_loop(self, chat_id: int, mode: int) -> None:
        if mode == 0:
            self.data["loop"].pop(str(chat_id), None)
        else:
            self.data["loop"][str(chat_id)] = mode
        self._mark_dirty()

    # PLAY MODE METHODS
    async def get_play_mode(self, chat_id: int) -> bool:
        return chat_id in self.data["play_mode"]

    async def set_play_mode(self, chat_id: int, remove: bool = False) -> None:
        if remove:
            if chat_id in self.data["play_mode"]:
                self.data["play_mode"].remove(chat_id)
        else:
            if chat_id not in self.data["play_mode"]:
                self.data["play_mode"].append(chat_id)
        self._mark_dirty()

    # FORCE MODE METHODS
    async def get_force_mode(self, chat_id: int) -> bool:
        return chat_id in self.data["force_mode"]

    async def set_force_mode(self, chat_id: int, remove: bool = False) -> None:
        if remove:
            if chat_id in self.data["force_mode"]:
                self.data["force_mode"].remove(chat_id)
        else:
            if chat_id not in self.data["force_mode"]:
                self.data["force_mode"].append(chat_id)
        self._mark_dirty()

    # SUDO METHODS
    async def add_sudo(self, user_id: int) -> None:
        if user_id not in self.data["sudoers"]:
            self.data["sudoers"].append(user_id)
            self._mark_dirty()

    async def del_sudo(self, user_id: int) -> None:
        if user_id in self.data["sudoers"]:
            self.data["sudoers"].remove(user_id)
            self._mark_dirty()

    async def get_sudoers(self) -> list[int]:
        return self.data["sudoers"]

    # USER METHODS
    async def is_user(self, user_id: int) -> bool:
        return user_id in self.data["users"]

    async def add_user(self, user_id: int) -> None:
        if not await self.is_user(user_id):
            self.data["users"].append(user_id)
            self._mark_dirty()

    async def rm_user(self, user_id: int) -> None:
        if await self.is_user(user_id):
            self.data["users"].remove(user_id)
            self._mark_dirty()

    async def get_users(self) -> list:
        return self.data["users"]

    async def load_cache(self) -> None:
        """No-op kept for backward compatibility — connect() already loads everything."""
        pass
