import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMIN_FILTER = filters.user(ADMINS)
user_state = {}
DB_FILE = "queue_db.json"

# 🛠️ Database Helpers
def load_queue():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_queue(queue):
    with open(DB_FILE, "w") as f:
        json.dump(queue, f, indent=4)

# 🎯 START COMMANDS
@app.on_message(filters.command("onlyfans") & ADMIN_FILTER)
async def onlyfan(client, message):
    user_state[message.from_user.id] = {"mode": "onlyfans", "step": "photo"}
    await message.reply("📸 Send photo")

@app.on_message(filters.command("adult") & ADMIN_FILTER)
async def adult(client, message):
    user_state[message.from_user.id] = {"mode": "adult", "step": "photo"}
    await message.reply("📸 Send photo")

# 🖼️ PHOTO HANDLER
@app.on_message(filters.photo & ADMIN_FILTER)
async def photo_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state or state["step"] != "photo": return
    
    state["photo"] = message.photo.file_id
    state["step"] = "name"
    await message.reply("🏷️ Send Name")

# 🔤 TEXT & QUEUE LOGIC
@app.on_message(filters.text & ~filters.command(["onlyfans", "adult", "post", "status"]) & ADMIN_FILTER)
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state: return

    if state["step"] == "name":
        state["name"] = message.text
        if state["mode"] == "adult":
            state["step"] = "company"
            await message.reply("🏢 Send Company Name")
        else:
            state["step"] = "link"
            await message.reply("🔗 Send Link")

    elif state["step"] == "company":
        state["company"] = message.text
        state["step"] = "link"
        await message.reply("🔗 Send Link")

    elif state["step"] == "link":
        state["link"] = message.text
        state["step"] = "channel"
        # Channel Selection Menu
        btn_list = []
        for k, v in CHANNELS.items():
            btn_list.append([InlineKeyboardButton(v["name"], callback_data=f"sel_{k}")])
        
        await message.reply("📡 Select target channel for this post:", 
                           reply_markup=InlineKeyboardMarkup(btn_list))

# 🔘 CALLBACK HANDLER (Channel Selection)
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

    # Prepare Queue Data
    queue_item = {
        "chat_id": target["id"],
        "photo": state["photo"],
        "caption": caption,
        "link": state["link"]
    }

    queue = load_queue()
    queue.append(queue_item)
    save_queue(queue)

    await callback_query.message.edit_text(f"✅ Added to Queue for: **{target['name']}**\nTotal in queue: {len(queue)}")
    user_state.pop(user_id, None)

# 🚀 QUEUE EXECUTION
@app.on_message(filters.command("post") & ADMIN_FILTER)
async def process_queue(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 Queue is empty.")
        return

    await message.reply(f"⏳ Starting sequence: 4 posts, 4-hour intervals.")
    
    count = 0
    while queue and count < 4:
        post = queue.pop(0)
        save_queue(queue) # Remove from DB immediately before sending
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛", url=post["link"])],
            [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]
        ])

        try:
            await client.send_photo(
                chat_id=post["chat_id"],
                photo=post["photo"],
                caption=post["caption"],
                reply_markup=buttons
            )
            count += 1
        except Exception as e:
            await message.reply(f"❌ Failed to post: {e}")

        if count < 4 and queue:
            await asyncio.sleep(4 * 3600) # 4 Hours

    await message.reply("🏁 Batch Posting Complete.")

@app.on_message(filters.command("status") & ADMIN_FILTER)
async def status(client, message):
    queue = load_queue()
    await message.reply(f"📊 Current Queue Size: {len(queue)} posts.")

print("Bot Started...")
app.run()
