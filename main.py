import asyncio
from datetime import datetime

from pyrogram import Client, filters
from config import *
import database as db

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_state = {}

# 🎯 COMMANDS

@app.on_message(filters.command("onlyfan"))
async def onlyfan(client, message):
    user_state[message.from_user.id] = {"mode": "onlyfan", "step": "video"}
    await message.reply("Send video")

@app.on_message(filters.command("adult"))
async def adult(client, message):
    user_state[message.from_user.id] = {"mode": "adult", "step": "video"}
    await message.reply("Send video")

# 📥 VIDEO
@app.on_message(filters.video)
async def video_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or state["step"] != "video":
        return

    state["video"] = message.video.file_id
    state["step"] = "link"
    await message.reply("Send link")

# 🔗 LINK + NAME + COMPANY
@app.on_message(filters.text)
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        return

    if state["step"] == "link":
        state["link"] = message.text
        state["step"] = "name"
        await message.reply("Send name")

    elif state["step"] == "name":
        state["name"] = message.text

        if state["mode"] == "adult":
            state["step"] = "company"
            await message.reply("Send company")
        else:
            state["step"] = "thumb"
            await message.reply("Send thumbnail")

    elif state["step"] == "company":
        state["company"] = message.text
        state["step"] = "thumb"
        await message.reply("Send thumbnail")

# 🖼️ THUMBNAIL → SAVE QUEUE
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or state["step"] != "thumb":
        return

    state["thumb"] = message.photo.file_id

    # ⏱️ SCHEDULING
    last_time = db.get_last_time()

    if last_time:
        post_time = last_time + INTERVAL
    else:
        post_time = datetime.now().timestamp()

    db.add_post((
        state["mode"],
        state["video"],
        state["link"],
        state["name"],
        state.get("company", ""),
        state["thumb"],
        post_time,
        "pending"
    ))

    await message.reply(f"Queued ✅")

    user_state.pop(user_id, None)

# 🔄 SCHEDULER
async def scheduler():
    while True:
        now = datetime.now().timestamp()
        posts = db.get_pending()

        for post in posts:
            post_id, mode, video, link, name, company, thumb, post_time, status = post

            if post_time <= now:
                mode_data = MODES[mode]

                caption = mode_data["caption"].format(
                    name=name,
                    link=link,
                    company=company
                )

                for ch in mode_data["channels"]:
                    await app.send_video(
                        chat_id=ch,
                        video=video,
                        caption=caption,
                        thumb=thumb
                    )

                    await asyncio.sleep(1)

                    await app.send_sticker(
                        chat_id=ch,
                        sticker=mode_data["sticker"]
                    )

                db.mark_done(post_id)

        await asyncio.sleep(10)

# ▶️ START
async def main():
    await app.start()
    asyncio.create_task(scheduler())
    print("Bot Running...")
    await asyncio.Event().wait()

app.run(main())
