import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ðŸ” Interval in seconds (4 hours)
INTERVAL = 4 * 60 * 60

# ðŸ”¥ MODES
MODES = {
    "onlyfans": {
        "channels": [-1003358300432],
        "caption": """ðŸŒ¸ {name}
leaked ðŸ’  vip

â¬‡ï¸ <a href="{link}">Download file</a>
â¬‡ï¸ <a href="{link}">Download file</a>
â¬‡ï¸ <a href="{link}">Download file</a>
                   
ã…¤ã…¤ã…¤ã…¤ã…¤ã…¤{name}

#OnlyFans 
@HeavenFallNetwork ðŸ”ž""",
        "sticker": "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE"
    },

    "adult": {
        "channels": [
            -1003624513206,
            -1003339318325
        ],
        "caption": """ðŸ‘¤ {name}
ðŸŽ¥ {company}

ðŸ—“ 2025 ðŸ”¥

#HardCore #adult

ðŸ”— <a href="{link}">Download file</a>
ðŸ”— <a href="{link}">Download file</a>
ðŸ”— <a href="{link}">Download file</a>

@heavenfallnetwork""",
        "sticker": "CAACAgQAAxkBAAEDDD5pzuhUXslvg8etKdXgFXl4mky8jQACuRkAAsMKoFEPcfteoU-9zDoE"
    }
}
