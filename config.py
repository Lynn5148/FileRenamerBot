import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔁 Interval in seconds (4 hours)
INTERVAL = 4 * 60 * 60

# 🔥 MODES
MODES = {
    "onlyfan": {
        "channels": [-1001111111111],
        "caption": """🌸 #{name}
leaked 💠 vip

⬇️ Download file
{link}
{link}
{link}
                   
#{name}

#OnlyFans 
@HeavenFallNetwork 🔞""",
        "sticker": "STICKER_ID_1"
    },

    "adult": {
        "channels": [
            -1002222222222,
            -1003333333333,
            -1004444444444
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
        "sticker": "STICKER_ID_2"
    }
}
