import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔁 Interval in seconds (4 hours)
INTERVAL = 4 * 60 * 60

# 🔥 MODES
MODES = {
    "onlyfan": {
        "channels": [-1003358300432],
        "caption": """🌸 #{name}
leaked 💠 vip

⬇️ Download file
{link}
{link}
{link}
                   
#{name}

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

🔗 Download media
{link}
{link}
{link}

@heavenfallnetwork""",
        "sticker": "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE"
    }
}
