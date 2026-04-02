from pyrogram import Client, filters
from pyrogram.types import Message
import os

from config import *
import database as db

app = Client("rename-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔁 USER STATE
user_state = {}


# 🔒 FORCE JOIN
async def check_join(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        return True
    except:
        return False


# 🏁 START
@app.on_message(filters.command("start"))
async def start(client, message):
    joined = await check_join(client, message.from_user.id)

    if not joined:
        return await message.reply("Join channel first to use bot.")

    await message.reply("Send /rename or /renameall")


# 🖼️ SET THUMBNAIL
@app.on_message(filters.command("setthumb") & filters.photo)
async def set_thumb(client, message):
    file_id = message.photo.file_id
    db.set_thumb(message.from_user.id, file_id)
    await message.reply("Thumbnail saved!")


# 🔁 SINGLE MODE
@app.on_message(filters.command("rename"))
async def rename_cmd(client, message):
    user_state[message.from_user.id] = {"mode": "single", "expected": "file"}
    await message.reply("Send file to rename")


# 📦 BATCH MODE
@app.on_message(filters.command("renameall"))
async def rename_all(client, message):
    user_state[message.from_user.id] = {
        "mode": "batch",
        "files": [],
        "expected": "files"
    }
    await message.reply("Send multiple files, then type /done")


# 🛑 DONE (Batch)
@app.on_message(filters.command("done"))
async def done(client, message):
    state = user_state.get(message.from_user.id)

    if not state or state["mode"] != "batch":
        return

    if not state["files"]:
        return await message.reply("No files added")

    state["expected"] = "name"
    await message.reply("Send base name")


# 📥 FILE HANDLER
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        return

    # SINGLE
    if state["mode"] == "single":
        state["file"] = message
        state["expected"] = "name"
        await message.reply("Send new name")

    # BATCH
    elif state["mode"] == "batch" and state["expected"] == "files":
        state["files"].append(message)
        await message.reply(f"Added {len(state['files'])} file(s)")


# 🏷️ TEXT HANDLER
@app.on_message(filters.text & ~filters.command(["start","rename","renameall","done"]))
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        return

    # SINGLE NAME
    if state["mode"] == "single" and state["expected"] == "name":

        if not db.can_rename(user_id, 1, DAILY_LIMIT):
            return await message.reply("Daily limit reached.")

        file = state["file"]
        ext = file.document.file_name.split(".")[-1]

        new_name = f"{message.text}.{ext}"

        thumb = db.get_thumb(user_id)

        file_path = await client.download_media(file)

ext = file.document.file_name.split(".")[-1]
new_file = f"{message.text}.{ext}"

os.rename(file_path, new_file)

await client.send_document(
        chat_id=user_id,
        document=new_path
    )

    os.remove(new_path)

    db.update_count(user_id)

except Exception as e:
    print(e)
    await message.reply(f"Error: {e}")

finally:
    user_state.pop(user_id, None)

    # BATCH NAME
    elif state["mode"] == "batch" and state["expected"] == "name":
        state["base"] = message.text
        state["expected"] = "rename"

        files = state["files"]

        if not db.can_rename(user_id, len(files), DAILY_LIMIT):
            return await message.reply("Limit exceeded.")

        thumb = db.get_thumb(user_id)

        for i, file in enumerate(files, start=1):
    file_path = await client.download_media(file)

    ext = file.document.file_name.split(".")[-1]
    new_file = f"[CH{i}] {state['base']}.{ext}"

    os.rename(file_path, new_file)

    await client.send_document(
        chat_id=user_id,
        document=new_file,
        thumb=thumb
    )

    os.remove(new_file)

            db.update_count(user_id)

        await message.reply("Done ✅")
        user_state.pop(user_id)


app.run()
