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
    "8": {"name": "Cosplay", "id": -1003631816627},
    "9": {"name": "Japanese", "id": -1003546961611},
    "10": {"name": "Hanime", "id": -1003877610680}
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
    "cosplay": {
        "caption": "🌸 {description}\n\n💠 Exclusive COSPLAY Content\nCarefully curated premium drop\n\n━━━━━━━━━━━━━━\nTap the button below to access\n━━━━━━━━━━━━━━\n\n#corn #cosplay\n@HeavenFallNetwork"
    },
    "japanese": {
        "caption": "━━━━━━━━━━━━━━\n➪ Episode:- {code}\n➪ Subtitle:- English ✅\n➪ Rating:- 100/10 [#recommended]\n{link_section}\n{description}\n\n@HeavenFallNetwork\n\nSubtitles Are Attached, Use Them"
    },
    "hanime": {
        "caption": "{description}\n\n➪ No. Of Episodes: {episodes} [ 20+min ]\n➪ Rating: 100/10 [Must Watch]\n{link_section}\n\n𝟭𝟴+ 𝗡𝗲𝘁𝘄𝗼𝗿𝗸: @HeavenFallNetwork"
    }
}
