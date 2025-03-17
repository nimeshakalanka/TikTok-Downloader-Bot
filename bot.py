from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, \
    InputTextMessageContent, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
import requests
import asyncio
import os
from bs4 import BeautifulSoup as bs
from configs import cfg
from pyromod import listen
from db import add_user, add_group, all_users, all_groups, users, remove_user

app = Client(
    "app",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

active_list = []
queue = []

# buttons
START_BUTTON = [
    [
        InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
        InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON")
    ]]

G_BUTTON = [
    [
        InlineKeyboardButton("👨‍💻 Developer", callback_data="DEV_BUTTON"),
        InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")
    ]]

DEV_BUTTON = [
    [
        InlineKeyboardButton("🧑🏻‍💻Contact Developer", url="http://t.me/akalankanime2")
    ],
    [InlineKeyboardButton("Use This Bot 🤖", url="https://t.me/AIl_Save_Bot?start=start")]]

SHARE_BUTTON = [[InlineKeyboardButton("Share ☘️", url="https://t.me/share/url?url=Check%20out%20this%20awesome%20bot%20for%20downloading%20videos%21%20%F0%9F%94%A5%0A%0AAll%20Save%20Bot%20%E2%98%98%EF%B8%8F%20%3A%20%20%40AIl_Save_Bot")]]

GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]

CMD_TEXT = """Here Is Bot Commands👇\n\n/start : Start Bot🤖\n/help : Get some help about how to use me🎊\n/stats : Get Bot Users stats(<code>Only for admins</code>)"""

START_TEXT = """Hello there, I am **Tiktok Downloader Bot**.\nI can download TikTok video for you without watermark."""

ABOUT_TEXT = """Hello👋👋 I am **TikTok Downloader Bot** and I can also Download and send videos to your Telegram Channel. If you want that features Contact Developer.\n\nNote:- Only add that feature to your If owner approve that."""

DEV_TEXT = """**NIMESH AKALANKA 🇱🇰 **is Professsional Telegram Bot Developer👨‍💻 with over 2 year experiance. If you want any Telegram Bot contact him, He will do your job as you desire for low budget."""



# start.
0
@app.on_message(filters.command('start'))
async def start(_, message):
    add_user(message.from_user.id)
    await app.send_message(message.from_user.id, text="👋👋 Hello " + message.from_user.mention + ", I am **Lexie Tiktok Bot**.\nI can download TikTok video for you without watermark.",
                         reply_markup=InlineKeyboardMarkup(START_BUTTON))


# stats
@app.on_message(filters.command("stats") & filters.user(cfg.SUDO))
async def dbtool(_, message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await message.reply_text(text=f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users : `{xx}`
👥 Groups : `{x}`
🚧 Total users & groups : `{tot}` """)


# broadcast
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m):
    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(userid))
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(e)
            failed += 1

    await lel.edit(
        f"✅Successfull to `{success}` users.\n❌ Faild to `{failed}` users.\n👾 Found `{blocked}` Blocked users \n👻 Found `{deactivated}` Deactivated users.")


# callback
@app.on_callback_query(filters.regex("_BUTTON"))
async def botCallbacks(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id

    if CallbackQuery.data == "START_BUTTON":
        await CallbackQuery.edit_message_text(START_TEXT, reply_markup=InlineKeyboardMarkup(START_BUTTON))

    elif CallbackQuery.data == "COMMAND_BUTTON":
        await CallbackQuery.edit_message_text(CMD_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON))

    elif CallbackQuery.data == "ABOUT_BUTTON":
        await CallbackQuery.edit_message_text(ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(G_BUTTON))

    elif CallbackQuery.data == "DEV_BUTTON":
        await app.send_sticker(user_id, "CAACAgIAAxkBAAEJPjlkgIzrYlsmoZ3gWRJmTuXuLFOAMQAC1BEAA8CgSXknAeKPK_QMLwQ")
        await app.send_message(user_id, DEV_TEXT, reply_markup=InlineKeyboardMarkup(DEV_BUTTON))


# help
@app.on_message(filters.command('help'))
async def help(_, message):
    await app.send_message(message.from_user.id,
                           text=f"Hello " + message.from_user.mention + ", I am **Tiktok Downloader Bot**.\nI can download any TikTok video from a given link.\nlink must like this:- <code>https://www.tiktok.com/@primemusix/video/7110443094918712602</code>\n\n"
                                                                        "__Send me a TikTok video link__")

# tiktok_download
@app.on_message(
    (filters.regex("http://") | filters.regex("https://")) & (filters.regex('tiktok') | filters.regex('douyin')))
async def tiktok_downloader(_, message):
    ran = await message.reply_text("<code>Processing.....</code>")
    link = message.text

    url = "https://tiktok-dl.akalankanime11.workers.dev/?url="+link

    response = requests.get(url)
    if response.status_code == 200:
        data_response = response.json()

    try:
        cap = data_response["video_title"]
        nwm_url = data_response["non_watermarked_url"]

    except:
        pass

    await ran.edit_text("<code>Downloading Video.....</code>")
    req = requests.get(nwm_url)
    send_video_path = id + ".mp4"
    with open(send_video_path, "wb") as f:
        f.write(req.content)
    await ran.edit_text("<code>Uploading Video.....</code>")
    await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
    await app.send_video(message.chat.id, video=send_video_path, reply_to_message_id=message.id,
                         caption=f"{cap}\n\n🚀 Bot by: @akalankanime2",
                         reply_markup=InlineKeyboardMarkup(SHARE_BUTTON))
    await ran.delete()
    os.remove(send_video_path)


print("Bot is Working Now!")
app.run()
