import asyncio
from pyrogram import Client, filters
from config import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_state = {}

# ðŸŽ¯ MODE SELECT

@app.on_message(filters.command("onlyfans"))
async def onlyfan(client, message):
    user_state[message.from_user.id] = {"mode": "onlyfans", "step": "photo"}
    await message.reply("Send photo")

@app.on_message(filters.command("adult"))
async def adult(client, message):
    user_state[message.from_user.id] = {"mode": "adult", "step": "photo"}
    await message.reply("Send photo")


# ðŸ–¼ï¸ PHOTO

@app.on_message(filters.photo)
async def photo_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state or state["step"] != "photo":
        return

    state["photo"] = message.photo.file_id
    state["step"] = "name"
    await message.reply("Send name")


# ðŸ”¤ TEXT HANDLER

@app.on_message(filters.text & ~filters.command(["onlyfans", "adult"]))
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
        else:
            state["step"] = "link"
            await message.reply("Send link")

    elif state["step"] == "company":
        state["company"] = message.text
        state["step"] = "link"
        await message.reply("Send link")

    elif state["step"] == "link":
        state["link"] = message.text

        mode_data = MODES[state["mode"]]

        caption = mode_data["caption"].format(
            name=state["name"],
            link=state["link"],
            company=state.get("company", "")
        )

        buttons = InlineKeyboardMarkup(
        [
                [InlineKeyboardButton("🔥 Click To Watch", url=state["link"])],
                [InlineKeyboardButton("📢 Main Channel", url="https://t.me/HeavenFallNetwork")]
            ]
        )

        await message.reply_photo(
    photo=state["photo"],
    caption=caption,
    parse_mode="html",
    reply_markup=buttons
    )
        user_state.pop(user_id, None)

print("Bot Started...")
app.run()
