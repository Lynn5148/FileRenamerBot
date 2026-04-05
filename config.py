import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔥 MODES
MODES = {
    "onlyfans": {
        "channels": [-1003358300432],
        "caption": """🌸 {name}
leaked 💠 vip

{name}

#OnlyFans 
@HeavenFallNetwork 🔞"""
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

@heavenfallnetwork"""
    }
}
