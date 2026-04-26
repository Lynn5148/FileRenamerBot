import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = [1893428612,2117537421,8607152118]

STICKER_ID = "CAACAgUAAxkBAAEDFxhp066Jt1ctY6DWotJo-dtv1Y4CKAAC0RoAAmSv8FfeFY0gJCkIIDsE"

CHANNELS = {
    "1": {"name": "OnlyFans", "id": -1003358300432},
    "2": {"name": "CornHub", "id": -1003624513206},
    "3": {"name": "International Corn", "id": -1003339318325},
    "4": {"name": "Milfy", "id": -1003668604630},
    "5": {"name": "Indian", "id": -1003840146959},
    "6": {"name": "Cornhwa", "id": -1003376886471},
    "7": {"name": "Doujinshi", "id": -1003853835138},
    "8": {"name": "Anime Hindi Dub", "id": -1001502396648}
}

MODES = {
    "onlyfans": {
        "caption": "🌸 {name}\n\n💠 Exclusive VIP Content\nCarefully curated premium drop\n\n━━━━━━━━━━━━━━\nTap the button below to access\n━━━━━━━━━━━━━━\n\n#OnlyFans\n@HeavenFallNetwork 🔞"
    },
    "adult": {
        "caption": "🎬 {company}\n\n👤 Featuring: {name}\n\n━━━━━━━━━━━━━━\n💠 Premium Release\nAccess via button below\n━━━━━━━━━━━━━━\n\n#Adult\n@HeavenFallNetwork 🔞"
    },
    "indian": {
        "caption": "{description} 😋 🔥\n\n➪ Videos: {duration} min Duration\n➪ Rating: 100/10\n\n💦💦 Must watch👁👅👁\nHighly Recommended Stuffs 🐶🥵\n\n@HeavenFallNetwork 🔞"
    },
    "cornhwa": {
        "caption": "**{name} | HeavenFall Cornhwa |**\n\n┏━━━━━━━━━━━━━━━┓\n\n‣ Type : CORNHWA\n‣ Average Rating : 99\n‣ Status : {status}\n‣ No of chapters : {chapters}\n‣ Genres : Drama, Hentai, Romance\n\n┗━━━━━━━━━━━━━━━┛\n**❖ CLICK ON READ NOW BUTTON ❖**\n▬▬▬▬▬▬▬▬▬▬▬▬▬\n﻿\nProvided by @HeavenFallNetwork\n\n[#MustRead #recommended]"
    },
    "doujinshi": {
        "caption": "**{name} | HeavenFallNetwork |**\n\n» Nᴏ.ᴏғ Pᴀɢᴇs: {pages}\n» Tʏᴘᴇ: #doujinshi\n» Lᴀɴɢᴜᴀɢᴇ: #english \n» Tᴀɢs: #heavenfallnetwork #mature #adult #doujinshi \n\n════════════════════\nProvided by @HeavenFallNetwork\n════════════════════"
    },
    "publicchannel": {
        "caption": "🌸 {description}\n\n💠 Exclusive VIP Content\nCarefully curated premium drop\n\n━━━━━━━━━━━━━━\nTap the button below to access\n━━━━━━━━━━━━━━\n\n#corn #free\n@HeavenFallNetwork"
    }
}
