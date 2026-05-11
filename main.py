import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from config import *

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ADMIN_FILTER = filters.user(ADMINS)
user_state = {}
scheduler_task = None
DB_FILE = "queue_db.json"
IST = timezone(timedelta(hours=5, minutes=30))
MULTI_SUPPORT = ["indian", "cornhwa", "japanese", "hanime"]

def load_queue():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_queue(queue):
    with open(DB_FILE, "w") as f:
        json.dump(queue, f, indent=4)

def add_to_queue(channel_key, post):
    queue = load_queue()
    if channel_key not in queue:
        queue[channel_key] = []
    queue[channel_key].append(post)
    save_queue(queue)

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

async def send_post(client, post, notify_chat_id=None):
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
        return True

    except Exception as e:
        if notify_chat_id:
            await client.send_message(notify_chat_id, f"❌ Error sending post: {e}")
        return False

async def show_preview(client, chat_id, post):
    media_list = post.get("media", [])
    caption = build_caption(post)
    item = media_list[0]

    preview_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data="preview_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="preview_cancel")
        ]
    ])

    if item["type"] == "video":
        await client.send_video(
            chat_id=chat_id, video=item["file_id"],
            caption=f"👀 Preview:\n\n{caption}",
            reply_markup=preview_buttons,
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await client.send_photo(
            chat_id=chat_id, photo=item["file_id"],
            caption=f"👀 Preview:\n\n{caption}",
            reply_markup=preview_buttons,
            parse_mode=enums.ParseMode.HTML
        )

async def scheduler_loop(client, notify_chat_id):
    global scheduler_task
    try:
        while True:
            now_ist = datetime.now(IST)
            for channel_key, (utc_hour, utc_minute) in CHANNEL_SCHEDULE.items():
                scheduled_ist_hour = (utc_hour + 5) % 24
                scheduled_ist_minute = (utc_minute + 30) % 60
                if utc_minute + 30 >= 60:
                    scheduled_ist_hour = (utc_hour + 6) % 24

                if now_ist.hour == scheduled_ist_hour and now_ist.minute == scheduled_ist_minute:
                    queue = load_queue()
                    channel_queue = queue.get(channel_key, [])
                    if channel_queue:
                        post = channel_queue.pop(0)
                        queue[channel_key] = channel_queue
                        save_queue(queue)
                        success = await send_post(client, post, notify_chat_id)
                        if success:
                            ch_name = CHANNELS[channel_key]["name"]
                            remaining = len(queue.get(channel_key, []))
                            await client.send_message(
                                notify_chat_id,
                                f"✅ Posted to **{ch_name}**\nRemaining in queue: {remaining}"
                            )
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        scheduler_task = None

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

    entry = {
        "chat_id": target["id"],
        "media": state["media"],
        "link": state["link"],
        "mode": m,
        "channel_key": channel_key
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

    state["pending_entry"] = entry
    state["pending_channel_key"] = channel_key
    state["pending_channel_name"] = target["name"]

    await callback_query.message.edit_text("⏳ Generating preview...")
    await show_preview(client, callback_query.message.chat.id, entry)

@app.on_callback_query(filters.regex(r"^preview_confirm$"))
async def preview_confirm(client, callback_query):
    user_id = callback_query.from_user.id
    state = user_state.get(user_id)
    if not state or "pending_entry" not in state:
        await callback_query.answer("Session expired."); return

    entry = state["pending_entry"]
    channel_key = state["pending_channel_key"]
    channel_name = state["pending_channel_name"]

    add_to_queue(channel_key, entry)
    queue = load_queue()
    remaining = len(queue.get(channel_key, []))

    await callback_query.message.edit_caption(
        f"✅ Added to **{channel_name}** queue!\nTotal in this channel: {remaining}"
    )
    user_state.pop(user_id, None)

@app.on_callback_query(filters.regex(r"^preview_cancel$"))
async def preview_cancel(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_caption("❌ Cancelled. Start again with the mode command.")
    user_state.pop(user_id, None)

@app.on_message(filters.command("post") & ADMIN_FILTER)
async def start_post(client, message):
    global scheduler_task
    if scheduler_task:
        await message.reply("⏳ Scheduler already running."); return
    await message.reply("🚀 Scheduler started! Posts will be sent daily at their scheduled times.")
    scheduler_task = asyncio.create_task(scheduler_loop(client, message.chat.id))

@app.on_message(filters.command("stop") & ADMIN_FILTER)
async def stop_post(client, message):
    global scheduler_task
    if scheduler_task:
        scheduler_task.cancel()
        scheduler_task = None
        await message.reply("🛑 Scheduler stopped.")
    else:
        await message.reply("⚪ Scheduler is not running.")

@app.on_message(filters.command("sendnow") & ADMIN_FILTER)
async def send_now(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 All queues are empty."); return

    btns = []
    for channel_key, posts in queue.items():
        if posts:
            ch_name = CHANNELS[channel_key]["name"]
            btns.append([InlineKeyboardButton(
                f"{ch_name} ({len(posts)})",
                callback_data=f"sendnow_{channel_key}"
            )])

    if not btns:
        await message.reply("📭 All queues are empty."); return

    await message.reply(
        "📡 Select channel to send now:",
        reply_markup=InlineKeyboardMarkup(btns)
    )

@app.on_callback_query(filters.regex(r"^sendnow_"))
async def sendnow_channel(client, callback_query):
    channel_key = callback_query.data.split("_")[1]
    queue = load_queue()
    channel_queue = queue.get(channel_key, [])

    if not channel_queue:
        await callback_query.answer("Queue empty for this channel."); return

    post = channel_queue.pop(0)
    queue[channel_key] = channel_queue
    save_queue(queue)

    await callback_query.message.edit_text(f"⏳ Sending to {CHANNELS[channel_key]['name']}...")
    success = await send_post(client, post, callback_query.message.chat.id)
    if success:
        await callback_query.message.edit_text(
            f"✅ Sent to **{CHANNELS[channel_key]['name']}**!\nRemaining: {len(channel_queue)}"
        )

@app.on_message(filters.command("clearall") & ADMIN_FILTER)
async def clear_all_queue(client, message):
    global scheduler_task
    if scheduler_task: scheduler_task.cancel(); scheduler_task = None
    save_queue({})
    user_state.clear()
    await message.reply("💥 **SYSTEM RESET COMPLETE**")

@app.on_message(filters.command("view") & ADMIN_FILTER)
async def view_queue(client, message):
    queue = load_queue()
    if not queue:
        await message.reply("📭 All queues empty."); return

    text = "📂 **Queue Status:**\n\n"
    has_posts = False
    for channel_key, posts in queue.items():
        if posts:
            has_posts = True
            ch_name = CHANNELS[channel_key]["name"]
            utc_h, utc_m = CHANNEL_SCHEDULE.get(channel_key, (0, 0))
            ist_h = (utc_h + 5) % 24
            ist_m = (utc_m + 30) % 60
            if utc_m + 30 >= 60:
                ist_h = (utc_h + 6) % 24
            text += f"📌 {ch_name}: {len(posts)} posts | ⏰ {ist_h:02d}:{ist_m:02d} IST\n"

    if not has_posts:
        await message.reply("📭 All queues empty."); return

    btns = []
    for channel_key, posts in queue.items():
        if posts:
            btns.append([InlineKeyboardButton(
                f"❌ Clear {CHANNELS[channel_key]['name']}",
                callback_data=f"clearq_{channel_key}"
            )])

    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns))

@app.on_callback_query(filters.regex(r"^clearq_"))
async def clear_channel_queue(client, callback_query):
    channel_key = callback_query.data.split("_")[1]
    queue = load_queue()
    queue[channel_key] = []
    save_queue(queue)
    ch_name = CHANNELS[channel_key]["name"]
    await callback_query.answer(f"✅ {ch_name} queue cleared!")
    await view_queue(client, callback_query.message)

@app.on_message(filters.command("status") & ADMIN_FILTER)
async def status_cmd(client, message):
    queue = load_queue()
    status = "RUNNING 🟢" if scheduler_task else "IDLE ⚪"
    total = sum(len(v) for v in queue.values())
    now_ist = datetime.now(IST)

    text = f"📊 **Bot Status**\n\n"
    text += f"Scheduler: {status}\n"
    text += f"Total queued posts: {total}\n"
    text += f"Current IST time: {now_ist.strftime('%I:%M %p')}\n\n"
    text += "**Per channel:**\n"

    for channel_key, (utc_h, utc_m) in CHANNEL_SCHEDULE.items():
        ist_h = (utc_h + 5) % 24
        ist_m = (utc_m + 30) % 60
        if utc_m + 30 >= 60:
            ist_h = (utc_h + 6) % 24
        ch_name = CHANNELS[channel_key]["name"]
        count = len(queue.get(channel_key, []))
        text += f"• {ch_name}: {count} posts | {ist_h:02d}:{ist_m:02d} IST\n"

    await message.reply(text)

print("Bot is Alive...")
app.run()
