import os
import re
import asyncio
from pytesseract import image_to_string
from PIL import Image
from telethon import TelegramClient, events, Button
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Environment Configurations
API_ID = int(os.environ.get("API_ID", 39002147))
API_HASH = os.environ.get("API_HASH", "cab2974c1f00eb3d40a3794da7b6d43b")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8867508657:AAGfL66RdqDJnAR36FokvdU-ah3o_m1SUY0")
SOURCE_CHANNEL = int(os.environ.get("SOURCE_CHANNEL", -1003973061596))
CHANNEL_TARGET = int(os.environ.get("CHANNEL_TARGET", -1004414227077))
WEBSITE_LINK = os.environ.get("WEBSITE_LINK", "https://income-pro-ng.lovable.app/")

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

KEYWORDS = ["credit alert", "credit", "alert", "withdrawal", "successful", "congrats", "🎉", "🥳", "💯", "🎊", "👏"]

# 1. Welcome New Channel Members
@bot.on(events.ChatAction(chats=CHANNEL_TARGET))
async def welcome_new_member(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        name = user.first_name if user else "Member"
        welcome_text = f"""Welcome {name} to the group! 🎉

Get started by visiting our official website:
{WEBSITE_LINK}"""
        await event.reply(welcome_text)

# 2. Channel Reposter & Link Stripper
@bot.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def repost_channel_post(event):
    text = event.text or ""
    if any(keyword in text.lower() for keyword in KEYWORDS):
        # Strip URLs
        cleaned_text = re.sub(r'https?://\S+|www\.\S+', '', text)
        await bot.send_message(CHANNEL_TARGET, cleaned_text, file=event.media)

# 3. Private DM Auto-Responder & Link Request Handler
@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def private_dm_handler(event):
    text = event.text.lower().strip() if event.text else ""

    # Link Requests, /start, Greetings
    if any(k in text for k in ["/start", "hi", "hello", "link", "website", "site", "url"]):
        msg = f"""Hello! 👋 Welcome to Income Pro.

Click the button below or use our official link to access the website:
{WEBSITE_LINK}"""
        buttons = [[Button.url("Visit Website 🚀", WEBSITE_LINK)]]
        await event.reply(msg, buttons=buttons)
        return

    # Registration & Tutorial Queries
    if any(k in text for k in ["registered", "tutorial", "video"]):
        msg = f"""Have you watched the full registration tutorial video?

If NOT, click the link to register and get started:
{WEBSITE_LINK}

If YES and you made payment, send your payment receipt screenshot here."""
        await event.reply(msg)
        return

    # Payment Confirmation
    if any(k in text for k in ["i paid", "made payment", "payment"]):
        await event.reply("Please send the screenshot of your payment receipt for verification.")
        return

    # Legitimacy Check
    if any(k in text for k in ["legit", "is it real", "real"]):
        msg = f"""Yes, Income Pro is 100% verified and legitimate! 💯

You can access the portal directly here:
{WEBSITE_LINK}"""
        await event.reply(msg)
        return

    # Loan Requests
    if "borrow" in text:
        await event.reply("Notice: We do not offer loans or borrowing services.")
        return

    # OCR Processing for Screenshots
    if event.photo:
        photo_path = await event.download_media()
        try:
            extracted_text = image_to_string(Image.open(photo_path)).lower()
            if "payout key" in extracted_text:
                await asyncio.sleep(2)
                await event.reply("Couldn't find your payment. Please you have to remake the payment.")
            else:
                fail_msg = f"""Payment Verification Failed ❌

Your transaction narrative was missing the required reference details.

Please retry or visit the portal to complete verification:
{WEBSITE_LINK}"""
                await event.reply(fail_msg)
        finally:
            if os.path.exists(photo_path):
                os.remove(photo_path)

# 4. Admin Menu Controls
@bot.on(events.NewMessage(pattern=r"^/(setadmin|admin1211)$"))
async def admin_panel(event):
    admin_msg = f"""<b>Admin Dashboard</b>

Morning Slot: Active
Evening Slot: Active

System Link: {WEBSITE_LINK}"""
    await event.reply(admin_msg, parse_mode="html")

async def main():
    scheduler.start()
    print("Bot started successfully...")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
                               
