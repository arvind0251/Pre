# ==========================================================
# Copyright (c) 2026 ArtistBots
# All Rights Reserved.
#
# Project      : ArtistBots API Telegram Music Bot
# Powered By   : Artist
# Type         : API Based Telegram Music Bot
#
# Bot          : @ArtistApibot 
# Channel      : https://t.me/artistbots
# GitHub       : https://github.com/elevenyts
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================
from pyrogram import types
from pyrogram.enums import ButtonStyle

from Elevenyts import app, config, lang


# ── Custom Emoji IDs (premium emoji) ─────────────────────────
# Apne asli custom_emoji_id yaha replace kar dena.
# ID nikalne ke liye pichle message wala /getemoji trick use karo.
class EMOJI:
    CANCEL      = "5215932040955975173"
    STATUS      = "5231234567891234567"
    TIMER       = "5231234567891234568"
    PAUSE       = "5231234567891234569"
    RESUME      = "5231234567891234570"
    REPLAY      = "5231234567891234571"
    SKIP        = "5231234567891234572"
    STOP        = "5231234567891234573"
    CLOSE       = "5288423978120842847"
    BACK        = "5231234567891234574"
    ADMINS      = "5231234567891234575"
    AUTH        = "5231234567891234576"
    BROADCAST   = "5231234567891234577"
    BLCHAT      = "5231234567891234578"
    BLUSER      = "5231234567891234579"
    GBAN        = "5231234567891234580"
    LOOP        = "5231234567891234581"
    PLAY        = "5231234567891234582"
    QUEUE       = "5231234567891234583"
    SEEK        = "5231234567891234584"
    SHUFFLE     = "5231234567891234585"
    PING        = "5231234567891234586"
    STATS       = "5231234567891234587"
    SUDO        = "5231234567891234588"
    MAINTENANCE = "5231234567891234589"
    LANGS       = "5231234567891234590"
    CHANNEL     = "5375464966372779094"
    SUPPORT     = "5424818574295313533"
    ADD_ME      = "6321049518670352133"
    SOURCE      = "6321049518670352133"
    HELP        = "6321049518670352133"
    COPY        = "5231234567891234593"
    OPEN_YT     = "5231234567891234594"


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[
            self.ikb(
                text=f"✗  {text}",
                callback_data="cancel_dl",
                style=ButtonStyle.DANGER,
                icon_custom_emoji_id=EMOJI.CANCEL,
            )
        ]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []

        if status:
            keyboard.append(
                [self.ikb(
                    text=f"◈  {status}",
                    callback_data=f"controls status {chat_id}",
                    style=ButtonStyle.PRIMARY,
                    icon_custom_emoji_id=EMOJI.STATUS,
                )]
            )
        elif timer:
            keyboard.append(
                [self.ikb(
                    text=f"  {timer}",
                    callback_data=f"controls status {chat_id}",
                    style=ButtonStyle.PRIMARY,
                    icon_custom_emoji_id=EMOJI.TIMER,
                )]
            )

        if not remove:
            # ── Main controls row ─────────────────────────────────
            keyboard.append(
                [
                    self.ikb(text="II", callback_data=f"controls pause {chat_id}", icon_custom_emoji_id=EMOJI.PAUSE),
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}", icon_custom_emoji_id=EMOJI.RESUME),
                    self.ikb(text="↻", callback_data=f"controls replay {chat_id}", icon_custom_emoji_id=EMOJI.REPLAY),
                    self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}", icon_custom_emoji_id=EMOJI.SKIP),
                    self.ikb(text="▢", callback_data=f"controls stop {chat_id}", icon_custom_emoji_id=EMOJI.STOP),
                ]
            )
            # ── Bottom row ────────────────────────────────────────
            keyboard.append(
                [
                    self.ikb(
                        text="🗑  ᴄʟᴏꜱᴇ",
                        callback_data=f"controls close {chat_id}",
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id=EMOJI.CLOSE,
                    ),
                ]
            )

        return self.ikm(keyboard)

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [self.ikb(
                    text="‹  ʙᴀᴄᴋ",
                    callback_data="help_main",
                    style=ButtonStyle.SUCCESS,
                    icon_custom_emoji_id=EMOJI.BACK,
                )]
            ]
        else:
            rows = [
                [
                    self.ikb(text="🛡  ᴀᴅᴍɪɴꜱ",     callback_data="help_admins",       style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.ADMINS),
                    self.ikb(text="🔐  ᴀᴜᴛʜ",        callback_data="help_auth",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.AUTH),
                    self.ikb(text="📢  ʙʀᴏᴀᴅᴄᴀꜱᴛ",  callback_data="help_broadcast",    style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.BROADCAST),
                ],
                [
                    self.ikb(text="🚫  ʙʟ-ᴄʜᴀᴛ",    callback_data="help_blchat",       style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.BLCHAT),
                    self.ikb(text="🚷  ʙʟ-ᴜꜱᴇʀ",    callback_data="help_bluser",       style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.BLUSER),
                    self.ikb(text="⚡  ɢ-ʙᴀɴ",       callback_data="help_gban",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.GBAN),
                ],
                [
                    self.ikb(text="🔁  ʟᴏᴏᴘ",        callback_data="help_loop",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.LOOP),
                    self.ikb(text="🎵  ᴘʟᴀʏ",        callback_data="help_play",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.PLAY),
                    self.ikb(text="📋  ǫᴜᴇᴜᴇ",       callback_data="help_queue",        style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.QUEUE),
                ],
                [
                    self.ikb(text="⏩  ꜱᴇᴇᴋ",        callback_data="help_seek",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SEEK),
                    self.ikb(text="🔀  ꜱʜᴜꜰꜰʟᴇ",    callback_data="help_shuffle",      style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SHUFFLE),
                    self.ikb(text="📡  ᴘɪɴɢ",        callback_data="help_ping",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.PING),
                ],
                [
                    self.ikb(text="📊  ꜱᴛᴀᴛꜱ",       callback_data="help_stats",        style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.STATS),
                    self.ikb(text="👑  ꜱᴜᴅᴏ",        callback_data="help_sudo",         style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SUDO),
                    self.ikb(text="🔧  ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="help_maintenance", style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.MAINTENANCE),
                ],
                [
                    self.ikb(text="‹  ʙᴀᴄᴋ",         callback_data="start",             style=ButtonStyle.SUCCESS, icon_custom_emoji_id=EMOJI.BACK),
                    self.ikb(text="🌐  ʟᴀɴɢꜱ",       callback_data="help_langs",        style=ButtonStyle.DANGER, icon_custom_emoji_id=EMOJI.LANGS),
                ],
            ]
        return self.ikm(rows)

    def langs_markup(self) -> types.InlineKeyboardMarkup:
        langs = [
            ("🇬🇧 English",    "en"), ("🇮🇳 Hindi",      "hi"),
            ("🇮🇳 Telugu",     "te"), ("🇰🇷 Korean",     "ko"),
            ("🇲🇲 Myanmar",    "my"), ("🇮🇩 Indonesian", "id"),
            ("🇧🇷 Portuguese", "pt"), ("🇸🇦 Arabic",     "ar"),
            ("🇪🇸 Spanish",    "es"), ("🇫🇷 French",     "fr"),
            ("🇷🇺 Russian",    "ru"), ("🇩🇪 German",     "de"),
            ("🇹🇷 Turkish",    "tr"), ("🇧🇩 Bengali",    "bn"),
            ("🇹🇭 Thai",       "th"), ("🇻🇳 Vietnamese", "vi"),
            ("🇯🇵 Japanese",   "ja"), ("🇨🇳 Chinese",    "zh"),
            ("🇵🇰 Urdu",       "ur"), ("🇮🇷 Persian",    "fa"),
        ]
        rows = []
        for i in range(0, len(langs), 2):
            row = [self.ikb(text=langs[i][0], callback_data=f"setlang_{langs[i][1]}", style=ButtonStyle.PRIMARY)]
            if i + 1 < len(langs):
                row.append(self.ikb(text=langs[i + 1][0], callback_data=f"setlang_{langs[i + 1][1]}", style=ButtonStyle.PRIMARY))
            rows.append(row)
        rows.append([self.ikb(
            text="‹  ʙᴀᴄᴋ",
            callback_data="help",
            style=ButtonStyle.SUCCESS,
            icon_custom_emoji_id=EMOJI.BACK,
        )])
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([
            [
                self.ikb(text="  ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL, style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.CHANNEL),
                self.ikb(text="  ꜱᴜᴘᴘᴏʀᴛ",  url=config.SUPPORT_CHAT,    style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SUPPORT),
            ],
            [
                self.ikb(
                    text="  ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                    icon_custom_emoji_id=EMOJI.ADD_ME,
                ),
            ],
        ])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm([
            [
                self.ikb(text="▷",  callback_data=f"controls resume {chat_id}", style=ButtonStyle.SUCCESS, icon_custom_emoji_id=EMOJI.RESUME),
                self.ikb(text="II",  callback_data=f"controls pause {chat_id}",  style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.PAUSE),
                self.ikb(text="‣‣I",  callback_data=f"controls skip {chat_id}",   style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SKIP),
                self.ikb(text="▢",  callback_data=f"controls stop {chat_id}",   style=ButtonStyle.DANGER, icon_custom_emoji_id=EMOJI.STOP),
            ],
            [
                self.ikb(
                    text="🗑  ᴄʟᴏꜱᴇ",
                    callback_data=f"controls close {chat_id}",
                    style=ButtonStyle.DANGER,
                    icon_custom_emoji_id=EMOJI.CLOSE,
                ),
            ],
        ])

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [[self.ikb(
                text=_text,
                callback_data=f"controls {_action} {chat_id} q",
                style=ButtonStyle.SUCCESS,
                icon_custom_emoji_id=EMOJI.PAUSE if playing else EMOJI.RESUME,
            )]]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, force_admin: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        play_mode_txt  = lang["admin_only_txt"] if admin_only  else lang["everyone"]
        force_mode_txt = lang["admin_only_txt"] if force_admin else lang["everyone"]
        return self.ikm([
            [
                self.ikb(text="  " + lang["play_mode"],  callback_data=f"controls status {chat_id}", style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.STATUS),
                self.ikb(text=play_mode_txt,               callback_data="playmode",                   style=ButtonStyle.SUCCESS),
            ],
            [
                self.ikb(text="  " + lang["force_mode"], callback_data=f"controls status {chat_id}", style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.STATUS),
                self.ikb(text=force_mode_txt,              callback_data="forcemode",                  style=ButtonStyle.SUCCESS),
            ],
        ])

    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
                    text="  " + lang["add_me"],
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.PRIMARY,
                    icon_custom_emoji_id=EMOJI.ADD_ME,
                )
            ],
            [
                self.ikb(text="  " + lang["help"],  callback_data="help",                                    style=ButtonStyle.SUCCESS, icon_custom_emoji_id=EMOJI.HELP),
                self.ikb(text="  ʟᴀɴɢꜱ",           callback_data="help_langs",                              style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.LANGS),
                self.ikb(text="  ꜱᴏᴜʀᴄᴇ",          url="https://github.com/elevenyts",          style=ButtonStyle.DANGER, icon_custom_emoji_id=EMOJI.SOURCE),
            ],
            [
                self.ikb(text="  " + lang["support"], url=config.SUPPORT_CHAT,    style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.SUPPORT),
                self.ikb(text=" " + lang["channel"], url=config.SUPPORT_CHANNEL, style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.CHANNEL),
            ],
        ]
        return self.ikm(rows)

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        return self.ikm([
            [
                self.ikb(text="📋  ᴄᴏᴘʏ ʟɪɴᴋ",     copy_text=link, style=ButtonStyle.PRIMARY, icon_custom_emoji_id=EMOJI.COPY),
                self.ikb(text="▶  ᴏᴘᴇɴ ɪɴ ʏᴛ", url=link,       style=ButtonStyle.DANGER, icon_custom_emoji_id=EMOJI.OPEN_YT),
            ],
        ])
