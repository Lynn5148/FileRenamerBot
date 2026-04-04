import asyncio
from pyrogram import Client, filters
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_state = {}

# 🎯 MODE SELECT

@app.on_message(filters.command("onlyfans"))
async def onlyfan(client, message):
    user_state[message.from_user.id] = {"mode": "onlyfans", "step": "photo"}
    await message.reply("Send photo")

@app.on_message(filters.command("adult"))
async def adult(client, message):
    user_state[message.from_user.id] = {"mode": "adult", "step": "photo"}
    await message.reply("Send photo")

# ✅ NEW MODE (DOUJINSHI)
@app.on_message(filters.command("doujinshi"))
async def doujinshi(client, message):
    user_state[message.from_user.id] = {"mode": "doujinshi", "step": "photo"}
    await message.reply("Send photo")


# 🖼️ PHOTO

@app.on_message(filters.photo)
async def photo_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or state["step"] != "photo":
        return

    state["photo"] = message.photo.file_id
    state["step"] = "name"
    await message.reply("Send name")


# 🔤 TEXT HANDLER

@app.on_message(filters.text & ~filters.command(["onlyfans", "adult", "doujinshi"]))
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        return

    if state["step"] == "name":
        state["name"] = message.text

        if state["mode"] == "adult":
            state["step"] = "company"
            await message.reply("Send company")

        elif state["mode"] == "doujinshi":
            state["step"] = "pages"
            await message.reply("Send number of pages")

        else:
            state["step"] = "link"
            await message.reply("Send link")

    elif state["step"] == "company":
        state["company"] = message.text
        state["step"] = "link"
        await message.reply("Send link")

    # ✅ NEW STEP (PAGES)
    elif state["step"] == "pages":
        state["pages"] = message.text
        state["step"] = "link"
        await message.reply("Send link")

    elif state["step"] == "link":
        state["link"] = message.text

        mode_data = MODES[state["mode"]]

        caption = mode_data["caption"].format(
            name=state["name"],
            link=state["link"],
            company=state.get("company", ""),
            pages=state.get("pages", "")
        )

        await message.reply_photo(
            photo=state["photo"],
            caption=caption,
            parse_mode="html"
        )

        user_state.pop(user_id, None)


print("Bot Started...")
app.run()
