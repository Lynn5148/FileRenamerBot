import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = [1893428612, 2117537421]

# 📢 Sticker ID jo har post ke baad jayega
STICKER_ID = "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE" # <-- Yahan apna Sticker File ID dalo

# 📡 Target Channels
CHANNELS = {
    "1": {"name": "OnlyFans Main", "id": -1003358300432},
    "2": {"name": "Adult Main 1", "id": -1003624513206},
    "3": {"name": "Adult Main 2", "id": -1003339318325}
}

# 🔥 Caption Templates
MODES = {
    "onlyfans": {
        "caption": """🌸 {name}\n\n💠 Exclusive VIP Content\nCarefully curated premium drop\n\n━━━━━━━━━━━━━━\nTap the button below to access\n━━━━━━━━━━━━━━\n\n#OnlyFans\n@HeavenFallNetwork 🔞"""
    },
    "adult": {
        "caption": """🎬 {company}\n\n👤 Featuring: {name}\n\n━━━━━━━━━━━━━━\n💠 Premium Release\nAccess via button below\n━━━━━━━━━━━━━━\n\n#Adult\n@HeavenFallNetwork 🔞"""
    }
}
