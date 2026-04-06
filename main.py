import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMIN_FILTER = filters.user(ADMINS)
user_state = {}
is_posting = False
stop_posting = False
DB_FILE = "queue_db.json"

# 🛠️ Database Helpers
def load_queue():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_queue(queue):
    with open(DB_FILE, "w") as f:
        json.dump(queue, f, indent=4)

# 🎯 START COMMANDS
@app.on_message(filters.command(["onlyfans", "adult"]) & ADMIN_FILTER)
async def start_creation(client, message):
    mode = message.command[0]
    user_state[message.from_user.id] = {"mode": mode, "step": "photo"}
    await message.reply(f"🚀 **{mode.upper()} Mode**\n📸 Send the photo now.")

# 🖼️ PHOTO HANDLER
@app.on_message(filters.photo & ADMIN_FILTER)
async def photo_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state or state["step"] != "photo": return
    
    state["photo"] = message.photo.file_id
    state["step"] = "name"
    await message.reply("🏷️ Send Name:")

# 🔤 TEXT HANDLER
@app.on_message(filters.text & ~filters.command(["onlyfans", "adult", "post", "stop", "view", "status", "sendnow", "clearall"]) & ADMIN_FILTER)
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state: return

    if state["step"] == "name":
        state["name"] = message.text
        if state["mode"] == "adult":
            state["step"] = "company"
            await message.reply("🏢 Send Company Name:")
        else:
            state["step"] = "link"
            await message.reply("🔗 Send Link:")

    elif state["step"] == "company":
        state["company"] = message.text
        state["step"] = "link"
        await message.reply("🔗 Send Link:")

    elif state["step"] == "link":
        state["link"] = message.text
        state["step"] = "channel"
        btn_list = [[InlineKeyboardButton(v["name"], callback_data=f"sel_{k}")] for k, v in CHANNELS.items()]
        await message.reply("📡 Select target channel:", reply_markup=InlineKeyboardMarkup(btn_list))

# 🔘 CALLBACK (Channel Select & Save to Queue)
@app.on_callback_query(filters.regex(r"^sel_"))
async def select_channel(client, callback_query):
    user_id = callback_query.from_user.id
    state = user_state.get(user_id)
    if not state: return

    channel_key = callback_query.data.split("_")[1]
    target = CHANNELS[channel_key]
    mode_data = MODES[state["mode"]]
    
    caption = mode_data["caption"].format(
        name=state["name"],
        company=state.get("company", "Premium")
    )

    queue = load_queue()
    queue.append({
        "chat_id": target["id"],
        "photo": state["photo"],
        "caption": caption,
        "link": state["link"]
    })
    save_queue(queue)

    await callback_query.message.edit_text(f"✅ Added to Queue for **{target['name']}**.\nTotal posts in queue: {len(queue)}")
    user_state.pop(user_id, None)

# ⚡ SEND NOW (Manual Push)
@app.on_message(filters.command("sendnow") & ADMIN_FILTER)
async def send_now(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 Queue is empty.")
        return
    btn_list = [[InlineKeyboardButton(v["name"], callback_data=f"push_{k}")] for k, v in CHANNELS.items()]
    await message.reply("🚀 **Manual Push:** Send the oldest queued post to which channel?", 
                       reply_markup=InlineKeyboardMarkup(btn_list))

@app.on_callback_query(filters.regex(r"^push_"))
async def push_callback(client, callback_query):
    queue = load_queue()
    if not queue:
        await callback_query.answer("Queue is empty!", show_alert=True)
        return

    channel_key = callback_query.data.split("_")[1]
    target_id = CHANNELS[channel_key]["id"]
    post = queue.pop(0)
    save_queue(queue)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛", url=post["link"])],
        [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]
    ])

    try:
        await client.send_photo(chat_id=target_id, photo=post["photo"], caption=post["caption"], reply_markup=buttons)
        await client.send_sticker(chat_id=target_id, sticker=STICKER_ID)
        await callback_query.message.edit_text(f"✅ Post pushed manually to **{CHANNELS[channel_key]['name']}**!")
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Error: {e}")

# 🚀 PROCESS QUEUE (Auto-Loop)
@app.on_message(filters.command("post") & ADMIN_FILTER)
async def process_queue(client, message):
    global stop_posting, is_posting
    queue = load_queue()
    if not queue:
        await message.reply("📭 Queue khali hai!")
        return
    if is_posting:
        await message.reply("⏳ Ek session pehle se chal raha hai.")
        return

    is_posting = True
    stop_posting = False
    await message.reply(f"🚀 Auto-Posting started! (Interval: 4 Hours)\nUse `/stop` to halt.")
    
    while queue:
        if stop_posting: break
        post = queue.pop(0)
        save_queue(queue)
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛", url=post["link"])], [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]])

        try:
            await client.send_photo(chat_id=post["chat_id"], photo=post["photo"], caption=post["caption"], reply_markup=buttons)
            await client.send_sticker(chat_id=post["chat_id"], sticker=STICKER_ID)
        except Exception as e:
            await message.reply(f"❌ Error in posting: {e}")

        if queue and not stop_posting:
            await asyncio.sleep(4 * 3600)

    is_posting = False
    await message.reply("🏁 Batch process complete.")

# 📋 VIEW/STATUS/STOP
@app.on_message(filters.command("view") & ADMIN_FILTER)
async def view_queue(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 Queue is empty.")
        return
    text = "📂 **Queue List (Tap to Delete):**\n\n"
    btns = [[InlineKeyboardButton(f"❌ Delete {i+1}", callback_data=f"del_{i}")] for i, item in enumerate(queue)]
    for i, item in enumerate(queue):
        text += f"{i+1}. {item['caption'][:25]}...\n"
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query(filters.regex(r"^del_"))
async def delete_item(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    queue = load_queue()
    if idx < len(queue):
        queue.pop(idx); save_queue(queue)
        await callback_query.answer("🗑️ Deleted!"); await view_queue(client, callback_query.message)

@app.on_message(filters.command("stop") & ADMIN_FILTER)
async def stop_cmd(client, message):
    global stop_posting
    stop_posting = True
    await message.reply("🛑 Stop signal received.")

@app.on_message(filters.command("status") & ADMIN_FILTER)
async def status_cmd(client, message):
    queue = load_queue()
    await message.reply(f"📊 Queue Size: {len(queue)} posts.")

# 💥 CLEAR ALL COMMAND
@app.on_message(filters.command("clearall") & ADMIN_FILTER)
async def clear_all_queue(client, message):
    global stop_posting, is_posting
    stop_posting = True
    is_posting = False
    try:
        save_queue([]) 
        await message.reply("💥 **Queue Fully Purged!**\n\n- All pending posts deleted.\n- Active posting cycle stopped.")
    except Exception as e:
        await message.reply(f"❌ Error clearing queue: {e}")

print("Bot is Alive...")
app.run()
