import asyncio
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMIN_FILTER = filters.user(ADMINS)
user_state = {}
posting_task = None  
DB_FILE = "queue_db.json"

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

@app.on_message(filters.command(list(MODES.keys())) & ADMIN_FILTER)
async def start_creation(client, message):
    mode = message.command[0].lower()
    user_state[message.from_user.id] = {"mode": mode, "step": "photo"}
    await message.reply(f"🚀 **{mode.upper()} Mode Activated**\n📸 Send the photo now.")

@app.on_message(filters.photo & ADMIN_FILTER)
async def photo_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state or state["step"] != "photo": return
    
    state["photo"] = message.photo.file_id
    
    if state["mode"] == "indian":
        state["step"] = "description"
        await message.reply("📝 Send Description:")
    elif state["mode"] == "publicchannel":
        state["step"] = "name"
        await message.reply("🏷️ Send Name/Description:")
    else:
        state["step"] = "name"
        await message.reply("🏷️ Send Name:")

@app.on_message(filters.text & ~filters.command(list(MODES.keys()) + ["post", "stop", "view", "status", "sendnow", "clearall"]) & ADMIN_FILTER)
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state: return

    m = state["mode"]
    s = state["step"]

    if m == "indian":
        if s == "description":
            state["description"] = message.text; state["step"] = "duration"
            await message.reply("⏱️ Send Video Duration (in mins):")
        elif s == "duration":
            state["duration"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Indian", callback_data="sel_5")]]))

    elif m == "publicchannel":
        if s == "name":
            state["description"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Anime Hindi Dub", callback_data="sel_8")]]))

    elif m == "cornhwa":
        if s == "name":
            state["name"] = message.text; state["step"] = "status"
            await message.reply("📖 Status (Finished/Ongoing?):")
        elif s == "status":
            state["status"] = message.text; state["step"] = "chapters"
            await message.reply("🔢 No. of Chapters:")
        elif s == "chapters":
            state["chapters"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cornhwa", callback_data="sel_6")]]))

    elif m == "doujinshi":
        if s == "name":
            state["name"] = message.text; state["step"] = "pages"
            await message.reply("📄 No. of Pages:")
        elif s == "pages":
            state["pages"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Doujinshi", callback_data="sel_7")]]))

    else:
        if s == "name":
            state["name"] = message.text
            if m == "adult":
                state["step"] = "company"; await message.reply("🏢 Send Company Name:")
            else:
                state["step"] = "link"; await message.reply("🔗 Send Link:")
        elif s == "company":
            state["company"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            if m == "adult":
                btns = [[InlineKeyboardButton(CHANNELS[i]["name"], callback_data=f"sel_{i}")] for i in ["2", "3", "4"]]
            elif m == "onlyfans":
                btns = [[InlineKeyboardButton("OnlyFans", callback_data="sel_1")]]
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query(filters.regex(r"^sel_"))
async def select_channel(client, callback_query):
    user_id = callback_query.from_user.id
    state = user_state.get(user_id)
    if not state: return

    channel_key = callback_query.data.split("_")[1]
    target = CHANNELS[channel_key]
    m = state["mode"]
    
    if m == "indian":
        caption = MODES["indian"]["caption"].format(description=state["description"], duration=state["duration"])
    elif m == "publicchannel":
        caption = MODES["publicchannel"]["caption"].format(description=state["description"])
    elif m == "cornhwa":
        caption = MODES["cornhwa"]["caption"].format(name=state["name"], status=state["status"], chapters=state["chapters"])
    elif m == "doujinshi":
        caption = MODES["doujinshi"]["caption"].format(name=state["name"], pages=state["pages"])
    else:
        caption = MODES[m]["caption"].format(name=state["name"], company=state.get("company", "Premium"))

    queue = load_queue()
    queue.append({
        "chat_id": target["id"],
        "photo": state["photo"],
        "caption": caption,
        "link": state["link"],
        "mode": m
    })
    save_queue(queue)

    await callback_query.message.edit_text(f"✅ Added to Queue for **{target['name']}**.\nTotal posts: {len(queue)}")
    user_state.pop(user_id, None)

async def posting_logic(client, message):
    try:
        while True:
            queue = load_queue()
            if not queue: break
            post = queue.pop(0)
            save_queue(queue)
            
            btn_text = "📖 𝗥𝗘𝗔𝗗 𝗡𝗢𝗪" if post.get("mode") in ["cornhwa", "doujinshi"] else "🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛"
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn_text, url=post["link"])], 
                [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]
            ])

            try:
                await client.send_photo(chat_id=post["chat_id"], photo=post["photo"], caption=post["caption"], reply_markup=buttons)
                await client.send_sticker(chat_id=post["chat_id"], sticker=STICKER_ID)
            except Exception as e:
                await message.reply(f"❌ Error: {e}")

            if load_queue():
                await asyncio.sleep(1 * 3600)
            else:
                break
        await message.reply("🏁 All posts sent.")
    except asyncio.CancelledError:
        await message.reply("🛑 Posting stopped.")
    finally:
        global posting_task
        posting_task = None

@app.on_message(filters.command("post") & ADMIN_FILTER)
async def start_post(client, message):
    global posting_task
    if posting_task:
        await message.reply("⏳ Already running."); return
    if not load_queue():
        await message.reply("📭 Empty."); return
    await message.reply("🚀 Starting Auto-Post...")
    posting_task = asyncio.create_task(posting_logic(client, message))

@app.on_message(filters.command("clearall") & ADMIN_FILTER)
async def clear_all_queue(client, message):
    global posting_task
    if posting_task: posting_task.cancel(); posting_task = None
    save_queue([]); user_state.clear()
    await message.reply("💥 **SYSTEM RESET COMPLETE**")

@app.on_message(filters.command("sendnow") & ADMIN_FILTER)
async def send_now(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 Queue is empty.")
        return
    
    post = queue.pop(0)
    save_queue(queue)
    
    btn_text = "📖 𝗥𝗘𝗔𝗗 𝗡𝗢𝗪" if post.get("mode") in ["cornhwa", "doujinshi"] else "🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_text, url=post["link"])], 
        [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]
    ])

    try:
        await client.send_photo(chat_id=post["chat_id"], photo=post["photo"], caption=post["caption"], reply_markup=buttons)
        await client.send_sticker(chat_id=post["chat_id"], sticker=STICKER_ID)
        await message.reply("✅ **Sent Now!** Seedha channel pe bhej diya gaya.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("view") & ADMIN_FILTER)
async def view_queue(client, message):
    queue = load_queue()
    if not queue: await message.reply("📭 Empty."); return
    text = "📂 **Queue:**\n\n"; btns = [[InlineKeyboardButton(f"❌ Del {i+1}", callback_data=f"del_{i}")] for i in range(len(queue))]
    for i, item in enumerate(queue): text += f"{i+1}. {item['caption'][:25]}...\n"
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query(filters.regex(r"^del_"))
async def delete_item(client, callback_query):
    idx = int(callback_query.data.split("_")[1]); queue = load_queue()
    if idx < len(queue):
        queue.pop(idx); save_queue(queue)
        await callback_query.answer("🗑️ Deleted!"); await view_queue(client, callback_query.message)

@app.on_message(filters.command("status") & ADMIN_FILTER)
async def status_cmd(client, message):
    queue = load_queue()
    status = "RUNNING 🟢" if posting_task else "IDLE ⚪"
    await message.reply(f"📊 Queue: {len(queue)}\nStatus: {status}")

print("Bot is Alive...")
app.run()
