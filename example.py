import json
import asyncio
from kakaobot.bot import Bot

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

bot = Bot(**config)

bot.load_events("./events")
bot.load_commands("./commands")

asyncio.run(bot.run())
