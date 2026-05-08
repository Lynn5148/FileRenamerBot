import asyncio
import json
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMIN_FILTER = filters.user(ADMINS)
user_state = {}
posting_task = None
DB_FILE = "queue_db.json"

MULTI_SUPPORT = ["indian", "cornhwa", "japanese", "hanime"]

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

def build_caption(post):
    m = post["mode"]
    link = post["link"]
    media = post.get("media", [])
    is_multi = len(media) > 1

    if m == "indian":
        if is_multi:
            return MODES["indian"]["multi"].format(
                description=post["description"],
                duration=post["duration"],
                link=link
            )
        return MODES["indian"]["single"].format(
            description=post["description"],
            duration=post["duration"]
        )

    elif m == "cornhwa":
        if is_multi:
            return MODES["cornhwa"]["multi"].format(
                name=post["name"],
                status=post["status"],
                chapters=post["chapters"],
                link=link
            )
        return MODES["cornhwa"]["single"].format(
            name=post["name"],
            status=post["status"],
            chapters=post["chapters"]
        )

    elif m == "japanese":
        if is_multi:
            return MODES["japanese"]["multi"].format(
                code=post["code"],
                description=post["description"],
                link=link
            )
        return MODES["japanese"]["single"].format(
            code=post["code"],
            description=post["description"]
        )

    elif m == "hanime":
        if is_multi:
            return MODES["hanime"]["multi"].format(
                description=post["description"],
                episodes=post["episodes"],
                link=link
            )
        return MODES["hanime"]["single"].format(
            description=post["description"],
            episodes=post["episodes"]
        )

    elif m == "doujinshi":
        return MODES["doujinshi"]["caption"].format(
            name=post["name"], pages=post["pages"]
        )

    elif m == "cosplay":
        return MODES["cosplay"]["caption"].format(description=post["description"])

    elif m == "adult":
        return MODES["adult"]["caption"].format(
            name=post["name"], company=post.get("company", "Premium")
        )

    elif m == "onlyfans":
        return MODES["onlyfans"]["caption"].format(name=post["name"])

    elif m == "gb":
        return MODES["gb"]["caption"].format(
            description=post["description"],
            studio=post["studio"],
            names=post["names"]
        )

    else:
        return MODES[m]["caption"].format(
            name=post.get("name", ""),
            company=post.get("company", "Premium")
        )

def build_buttons(post):
    m = post["mode"]
    link = post["link"]
    btn_text = "📖 𝗥𝗘𝗔𝗗 𝗡𝗢𝗪" if m in ["cornhwa", "doujinshi"] else "🔗 𝗖𝗟𝗜𝗖𝗞 𝗧𝗢 𝗪𝗔𝗧𝗖𝗛"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_text, url=link)],
        [InlineKeyboardButton("📢 𝗠𝗔𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/HeavenFallNetwork")]
    ])

async def send_post(client, post, message=None):
    media_list = post.get("media", [])
    caption = build_caption(post)
    buttons = build_buttons(post)
    chat_id = post["chat_id"]
    m = post["mode"]
    is_multi = len(media_list) > 1 and m in MULTI_SUPPORT

    try:
        if not is_multi:
            item = media_list[0]
            if item["type"] == "video":
                await client.send_video(
                    chat_id=chat_id, video=item["file_id"],
                    caption=caption, reply_markup=buttons,
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await client.send_photo(
                    chat_id=chat_id, photo=item["file_id"],
                    caption=caption, reply_markup=buttons,
                    parse_mode=enums.ParseMode.HTML
                )
        else:
            media_group = []
            for i, item in enumerate(media_list):
                cap = caption if i == len(media_list) - 1 else ""
                if item["type"] == "video":
                    media_group.append(InputMediaVideo(
                        item["file_id"], caption=cap,
                        parse_mode=enums.ParseMode.HTML
                    ))
                else:
                    media_group.append(InputMediaPhoto(
                        item["file_id"], caption=cap,
                        parse_mode=enums.ParseMode.HTML
                    ))
            await client.send_media_group(chat_id=chat_id, media=media_group)

        await client.send_sticker(chat_id=chat_id, sticker=STICKER_ID)

    except Exception as e:
        if message:
            await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command(list(MODES.keys())) & ADMIN_FILTER)
async def start_creation(client, message):
    mode = message.command[0].lower()
    user_state[message.from_user.id] = {"mode": mode, "step": "media", "media": []}
    if mode in MULTI_SUPPORT:
        await message.reply(f"🚀 **{mode.upper()} Mode Activated**\n📸 Send photos/videos (up to 10). Send /done when finished.")
    else:
        await message.reply(f"🚀 **{mode.upper()} Mode Activated**\n📸 Send the photo or video.")

@app.on_message((filters.photo | filters.video) & ADMIN_FILTER)
async def media_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state or state["step"] != "media": return

    if message.photo:
        state["media"].append({"type": "photo", "file_id": message.photo.file_id})
    elif message.video:
        state["media"].append({"type": "video", "file_id": message.video.file_id})

    m = state["mode"]
    count = len(state["media"])

    if m not in MULTI_SUPPORT:
        await proceed_after_media(message, state)
    elif count >= 10:
        await message.reply(f"✅ {count} files collected. Max reached, proceeding...")
        await proceed_after_media(message, state)
    else:
        await message.reply(f"📸 File {count} saved. Send more or /done to proceed.")

@app.on_message(filters.command("done") & ADMIN_FILTER)
async def done_media(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state or state["step"] != "media": return
    if not state["media"]:
        await message.reply("⚠️ Send at least one photo or video first."); return
    await proceed_after_media(message, state)

async def proceed_after_media(message, state):
    m = state["mode"]
    if m == "indian":
        state["step"] = "description"
        await message.reply("📝 Send Description:")
    elif m == "japanese":
        state["step"] = "code"
        await message.reply("🔢 Send Episode Code:")
    elif m == "hanime":
        state["step"] = "description"
        await message.reply("📝 Send Description:")
    elif m == "cosplay":
        state["step"] = "name"
        await message.reply("🏷️ Send Name/Description:")
    elif m == "gb":
        state["step"] = "description"
        await message.reply("💡 Send Title/Description:")
    else:
        state["step"] = "name"
        await message.reply("🏷️ Send Name:")

@app.on_message(filters.text & ~filters.command(list(MODES.keys()) + ["post", "stop", "view", "status", "sendnow", "clearall", "done"]) & ADMIN_FILTER)
async def text_handler(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id)
    if not state: return

    m = state["mode"]
    s = state["step"]

    if m == "japanese":
        if s == "code":
            state["code"] = message.text; state["step"] = "description"
            await message.reply("📝 Send Description:")
        elif s == "description":
            state["description"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Japanese", callback_data="sel_9")]]))

    elif m == "hanime":
        if s == "description":
            state["description"] = message.text; state["step"] = "episodes"
            await message.reply("🔢 No. of Episodes:")
        elif s == "episodes":
            state["episodes"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Hanime", callback_data="sel_10")]]))

    elif m == "gb":
        if s == "description":
            state["description"] = message.text; state["step"] = "studio"
            await message.reply("🎬 Send Studio Name:")
        elif s == "studio":
            state["studio"] = message.text; state["step"] = "names"
            await message.reply("👩🏻 Send Actress Names:")
        elif s == "names":
            state["names"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("GB", callback_data="sel_11")]]))

    elif m == "indian":
        if s == "description":
            state["description"] = message.text; state["step"] = "duration"
            await message.reply("⏱️ Send Video Duration (in mins):")
        elif s == "duration":
            state["duration"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Indian", callback_data="sel_5")]]))

    elif m == "cosplay":
        if s == "name":
            state["description"] = message.text; state["step"] = "link"
            await message.reply("🔗 Send Link:")
        elif s == "link":
            state["link"] = message.text; state["step"] = "channel"
            await message.reply("📡 Select channel:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cosplay", callback_data="sel_8")]]))

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

    queue = load_queue()
    entry = {
        "chat_id": target["id"],
        "media": state["media"],
        "link": state["link"],
        "mode": m
    }

    if m == "japanese":
        entry["code"] = state["code"]
        entry["description"] = state["description"]
    elif m == "hanime":
        entry["description"] = state["description"]
        entry["episodes"] = state["episodes"]
    elif m == "gb":
        entry["description"] = state["description"]
        entry["studio"] = state["studio"]
        entry["names"] = state["names"]
    elif m == "indian":
        entry["description"] = state["description"]
        entry["duration"] = state["duration"]
    elif m == "cosplay":
        entry["description"] = state["description"]
    elif m == "cornhwa":
        entry["name"] = state["name"]
        entry["status"] = state["status"]
        entry["chapters"] = state["chapters"]
    elif m == "doujinshi":
        entry["name"] = state["name"]
        entry["pages"] = state["pages"]
    else:
        entry["name"] = state["name"]
        entry["company"] = state.get("company", "Premium")

    queue.append(entry)
    save_queue(queue)

    await callback_query.message.edit_text(f"✅ Added to Queue for **{target['name']}**.\nFiles: {len(state['media'])} | Total posts: {len(queue)}")
    user_state.pop(user_id, None)

async def posting_logic(client, message):
    try:
        count = 0
        while count < 10:
            queue = load_queue()
            if not queue: break
            post = queue.pop(0)
            save_queue(queue)
            await send_post(client, post, message)
            count += 1
            if load_queue() and count < 10:
                await asyncio.sleep(1 * 3600)
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
    await send_post(client, post, message)
    await message.reply("✅ **Sent Now!**")

@app.on_message(filters.command("view") & ADMIN_FILTER)
async def view_queue(client, message):
    queue = load_queue()
    if not queue: await message.reply("📭 Empty."); return
    text = "📂 **Queue:**\n\n"
    btns = [[InlineKeyboardButton(f"❌ Del {i+1}", callback_data=f"del_{i}")] for i in range(len(queue))]
    for i, item in enumerate(queue): text += f"{i+1}. {item['mode'].upper()} | Files: {len(item.get('media', []))}\n"
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query(filters.regex(r"^del_"))
async def delete_item(client, callback_query):
    idx = int(callback_query.data.split("_")[1])
    queue = load_queue()
    if idx < len(queue):
        queue.pop(idx); save_queue(queue)
        await callback_query.answer("🗑️ Deleted!")
        await view_queue(client, callback_query.message)

@app.on_message(filters.command("status") & ADMIN_FILTER)
async def status_cmd(client, message):
    queue = load_queue()
    status = "RUNNING 🟢" if posting_task else "IDLE ⚪"
    await message.reply(f"📊 Queue: {len(queue)}\nStatus: {status}")

print("Bot is Alive...")
app.run()
