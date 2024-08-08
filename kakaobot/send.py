import asyncio
import json
import base64

import logging
logger = logging.getLogger(__name__)

class AsyncMsgSender:
    def __init__(self, room: str, bot_ip: str, bot_socket_port: int):
        self.ip = bot_ip
        self.port = bot_socket_port
        self.room = room
        self.queue = asyncio.Queue()
        self.writer = None
        self._processing_queue = False

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)

    async def send_message(self, is_success: bool, type: str, data: str, room: str) -> None:
        message = {
            "isSuccess": is_success,
            "type": type,
            "data": base64.b64encode(data.encode()).decode(),
            "room": base64.b64encode(room.encode()).decode(),
        }
        if not self.writer or self.writer.is_closing():
            await self.connect()
        try:
            self.writer.write(json.dumps(message).encode("utf-8"))
            await self.writer.drain()
        except (asyncio.CancelledError, OSError, ConnectionResetError) as e:
            logger.error(f"Error sending message: {e}")
            await self.connect()  # Reconnect on error

    async def send(self, msg: str, room: str = None) -> None:
        room = room if room is not None else self.room
        await self.queue.put((True, "normal", msg, room))
        if not self._processing_queue:
            self._processing_queue = True
            asyncio.create_task(self.__process_queue())

    async def __process_queue(self) -> None:
        while not self.queue.empty():
            message = await self.queue.get()
            await self.send_message(*message)
            await asyncio.sleep(0.1)
        self._processing_queue = False

    async def close(self) -> None:
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
