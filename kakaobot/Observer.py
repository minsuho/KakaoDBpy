from hachiko.hachiko import AIOWatchdog, AIOEventHandler
import asyncio
from .kakaoDB import KakaoDB
import traceback
import time
import os

import logging
logger = logging.getLogger(__name__)

class MyEventHandler(AIOEventHandler):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.DB_PATH = bot.DB_PATH.replace('\\', '/')
        self.db = KakaoDB(
            self.bot.prefix, self.bot.DB_PATH, self.bot.BOT_ID, self.bot.BOT_NAME,
            self.bot.BOT_IP, self.bot.BOT_PORT, self.bot.commands, self.bot.events
        )
        self.last_run = 0
        self.run_interval = 0.5

    async def on_modified(self, event):
        current_time = time.time()
        if (current_time - self.last_run) < self.run_interval:
            return  # 설정된 간격보다 짧으면 무시
        self.last_run = current_time

        try:
            src_path = event.src_path.replace('\\', '/')
            if src_path in {f"{self.DB_PATH}/KakaoTalk.db", f"{self.DB_PATH}/KakaoTalk.db-wal"}:
                # logger.info("KakaoTalk DB1 modified")
                await self.db.chat_check()
            elif src_path in {f"{self.DB_PATH}/KakaoTalk2.db", f"{self.DB_PATH}/KakaoTalk2.db-wal"}:
                # logger.info("KakaoTalk DB2 modified")
                await self.db.update_names()
        except Exception as e:
            traceback.print_exc()
            logger.error(f"An error occurred: {e}")

    async def on_opened(self, event):
        pass

async def file_check(DB_PATH):
    if not os.path.isfile(f"{DB_PATH}/KakaoTalk.db" or f"{DB_PATH}/KakaoTalk2.db"):
        logger.error(f"There is no database file in the directory: {DB_PATH}")
        raise FileNotFoundError(f"No database file found in the directory: {DB_PATH}")
    if not os.access(f"{DB_PATH}/KakaoTalk.db", os.R_OK):
        logger.error(f"{DB_PATH}/KakaoTalk.db: The file does not have read permissions."
)
        raise PermissionError(f"{DB_PATH}/KakaoTalk.db: The file does not have read permissions.")

    if not os.access(f"{DB_PATH}/KakaoTalk2.db", os.R_OK):
        logger.error(f"{DB_PATH}/KakaoTalk2.db: The file does not have read permissions."
)
        raise PermissionError(f"{DB_PATH}/KakaoTalk2.db: The file does not have read permissions.")
    return


async def start(bot):
    await file_check(bot.DB_PATH)

    evh = MyEventHandler(bot)
    watch = AIOWatchdog(bot.DB_PATH, event_handler=evh)
    watch.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping AIOWatchdog...')
    finally:
        watch.stop()
        logger.info('AIOWatchdog stopped.')
