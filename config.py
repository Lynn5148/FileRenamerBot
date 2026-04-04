import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔁 Interval in seconds (4 hours)
INTERVAL = 4 * 60 * 60

# 🔥 MODES
MODES = {
    "onlyfans": {
        "channels": [-1003358300432],
        "caption": """🌸 {name}
leaked 💠 vip

⬇️ <a href="{link}">Download file</a>
⬇️ <a href="{link}">Download file</a>
⬇️ <a href="{link}">Download file</a>
                   
ㅤㅤㅤㅤㅤㅤ{name}

#OnlyFans 
@HeavenFallNetwork 🔞""",
        "sticker": "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE"
    },

    "adult": {
        "channels": [
            -1003624513206,
            -1003339318325
        ],
        "caption": """👤 {name}
🎥 {company}

🗓 2025 🔥

#HardCore #adult

🔗 <a href="{link}">Download file</a>
🔗 <a href="{link}">Download file</a>
🔗 <a href="{link}">Download file</a>

@heavenfallnetwork""",
        "sticker": "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE"
    }
}
