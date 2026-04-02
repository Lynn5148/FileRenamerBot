import asyncio
from datetime import datetime

from pyrogram import Client, filters
from config import *
import database as db

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_state = {}
last_channel_index = 0  # for alternating channels


# 🎯 MODE COMMANDS

@app.on_message(filters.command("onlyfan"))
async def onlyfan(client, message):
    user_state[message.from_user.id] = {"mode": "onlyfan", "step": "link"}
    await message.reply("Send link")


@app.on_message(filters.command("adult"))
async def adult(client, message):
    user_state[message.from_user.id] = {"mode": "adult", "step": "link"}
    await message.reply("Send link")


# 🔗 LINK + NAME + COMPANY

@app.on_message(filters.text & ~filters.command(["onlyfan", "adult", "interval", "queue", "clearqueue"]))
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
            save_post_and_queue(message, state)

    elif state["step"] == "company":
        state["company"] = message.text
        save_post_and_queue(message, state)


# 🧠 SAVE FUNCTION

def save_post_and_queue(message, state):
    user_id = message.from_user.id

    last_time = db.get_last_time()

    if last_time:
        post_time = last_time + INTERVAL
    else:
        post_time = datetime.now().timestamp()

    db.add_post((
        state["mode"],
        "",  # video removed
        state["link"],
        state["name"],
        state.get("company", ""),
        "",  # thumb removed
        post_time,
        "pending"
    ))

    asyncio.create_task(message.reply("Queued ✅"))

    user_state.pop(user_id, None)


# ⏱️ SET INTERVAL

@app.on_message(filters.command("interval"))
async def set_interval(client, message):
    global INTERVAL

    try:
        text = message.text.split()[1]

        if "h" in text:
            INTERVAL = int(text.replace("h", "")) * 3600
        elif "m" in text:
            INTERVAL = int(text.replace("m", "")) * 60

        await message.reply(f"Interval set to {text}")

    except:
        await message.reply("Use like: /interval 4h or /interval 30m")


# 📊 CHECK QUEUE

@app.on_message(filters.command("queue"))
async def check_queue(client, message):
    posts = db.get_pending()
    await message.reply(f"Queued posts: {len(posts)}")


# 🗑️ CLEAR QUEUE

@app.on_message(filters.command("clearqueue"))
async def clear_queue(client, message):
    db.cur.execute("DELETE FROM posts WHERE status='pending'")
    db.conn.commit()
    await message.reply("Queue cleared ✅")


# 🔄 SCHEDULER

async def scheduler():
    global last_channel_index

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

                channels = mode_data["channels"]

                # 🔁 ALTERNATING LOGIC (only for multiple channels)
                if len(channels) > 1:
                    ch = channels[last_channel_index % len(channels)]
                    last_channel_index += 1
                else:
                    ch = channels[0]

                await app.send_message(
                    chat_id=ch,
                    text=caption
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
