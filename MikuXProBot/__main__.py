import importlib
import time
import re
import random
from sys import argv
from typing import Optional

import MikuXProBot.modules.sql.users_sql as sql

from MikuXProBot import (ALLOW_EXCL, CERT_PATH, DONATION_LINK, LOGGER,
                          OWNER_ID, PORT, SUPPORT_CHAT, TOKEN, URL, WEBHOOK,
                          SUPPORT_CHAT, dispatcher, StartTime, telethn, updater)
# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from MikuXProBot.modules import ALL_MODULES
from MikuXProBot.modules.helper_funcs.chat_status import is_user_admin
from MikuXProBot.modules.helper_funcs.misc import paginate_modules
from MikuXProBot.script import PM_START_TEXT, MIKU_DISPACHER_PIC, PM_PHOTO, MIKU_N_IMG, TEXXT, MIKU_IMG
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.error import (BadRequest, ChatMigrated, NetworkError,
                            TelegramError, TimedOut, Unauthorized)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          Filters, MessageHandler)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown, mention_html

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

buttons = [
    [
                        InlineKeyboardButton(
                             text="🏹 Summon Me",
                             url="https://t.me/MikuXProBot?startgroup=true"),
                        InlineKeyboardButton(
                             text="🗞️ Repo",
                             url="https://github.com/h0daka/Miku-Nakano"),
                    ],
                   [                  
                       InlineKeyboardButton(
                             text="🔐 Help",
                             callback_data="help_back"),
                        InlineKeyboardButton(
                             text=" 💫 About Me",
                             callback_data="miku_"),
                    ], 
    ]


HELP_STRINGS = """
*Hey your {} is here!  
*Main* commands available :
 • /help: PM's you this message.
 • /help <module name>: PM's you info about that module.
 • /settings:
   • in PM: will send you your settings for all supported modules.
   • in a group: will redirect you to pm, with all that chat's settings.
For all command use /* [or](https://telegra.ph/file/85a404cf9edbd797c829f.jpg) *!*
""".format(
    dispatcher.bot.first_name,""
    if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\nKindly use ! for commands if / is not working\n")

DONATE_STRING = """ Adding Me To Your Groups Is Donation For Me """

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MikuXProBot.modules." +
                                              module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception(
            "Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard)


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)

