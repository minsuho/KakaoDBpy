import typing as t
from . import Observer
import asyncio

import glob
import importlib.util
from typing import Callable, Dict

import logging
logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, prefix: str, DB_PATH: str, BOT_ID: int, BOT_NAME: str, BOT_IP: str, BOT_PORT: int):
        '''
        :param func:
        :param prefix: 명렁어 접두사 (필수)
        :param DB_PATH: DB 위치 (필수)
        :param BOT_ID: BOT ID
        :param BOT_NAME: BOT 이름
        '''
        if len(prefix) > 1:
            logger.error("Invalid prefix length: %d", len(prefix))
            raise ValueError("prefix should be a single character")
        self.__prefix = prefix
        self.prefix = prefix
        self.DB_PATH = DB_PATH
        self.BOT_ID = BOT_ID
        self.BOT_NAME = BOT_NAME
        self.BOT_IP = BOT_IP
        self.BOT_PORT = BOT_PORT

        self.commands: Dict[str, Callable] = {}
        self.events = {
            'on_message': None,
            'on_delete': None,
            'on_hide': None,
            'on_join': None,
            'on_kick': None,
            'on_leave': None,
            'on_open_profile_change': None,
            'on_member_type_change': None,
            'on_invite': None,
        }

        self.on_message = self.event_decorator('on_message') #메시지가 왔을 때 반응을 합니다
        self.on_delete = self.event_decorator('on_delete') #누군가 메시지를 지우면 반응합니다
        self.on_hide = self.event_decorator('on_hide') #누군가 메시지를 가리면 반응합니다
        self.on_join = self.event_decorator('on_join') #누군가 오픈챗에 들어오면 반응합니다
        self.on_invite = self.event_decorator('on_invite') #누군가 단체방에서 초대하면 반응합니다
        self.on_leave = self.event_decorator('on_leave') #누군가 단체방(오픈챗 포함)을 나갈 때 반응합니다 팀챗에서 강퇴당해도 leave로 전달해줍니다
        self.on_kick = self.event_decorator('on_kick') #누군가 오픈채팅방에서 강퇴당하면 반응합니다
        self.on_open_profile_change = self.event_decorator('on_open_profile_change') #프로필이 바뀌면 반응해요
        self.on_member_type_change = self.event_decorator('on_member_type_change') #방장 부방장이 바뀌면 반응해요


    def load_commands(self, dir):
        modules_path = f"{dir}/*.py"
        for filename in glob.glob(modules_path):
            spec = importlib.util.spec_from_file_location("module.name", filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'setup_commands'):
                logger.info(f"{filename} 명령어 등록")
                module.setup_commands(self)

    def load_events(self, dir):
        modules_path = f"{dir}/*.py"
        for filename in glob.glob(modules_path):
            spec = importlib.util.spec_from_file_location("module.name", filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'setup_events'):
                logger.info(f"{filename} 이벤트 등록")
                module.setup_events(self)

    async def async_run(self):
        logger.info("BOT RUN")
        # DB 파일 감시 시작
        await Observer.start(self)

    def on_command(self,
            cmd: str,
            prefix: t.Optional[str] = None,
            room: t.Optional[t.Iterable[str]] = None):
        '''
        :param func:
        :param cmd: 명령어
        :param prefix: 명렁어 접두사(default: 봇 접두사)
        :param room: 작동할 방 목록(방 이름)
        '''
        def wrapper(f: t.Callable[[], None]):
            pfx = self.__prefix
            if prefix:
                pfx = prefix
            if len(pfx) > 1:
                logger.error("Invalid prefix length: %d", len(pfx))
                raise ValueError("prefix should be a single character")
            if pfx in self.commands:
                self.commands[pfx][cmd] = {"func": f, "room": room}
            else:
                self.commands[pfx] = {cmd: {"func": f, "room": room}}
        return wrapper
    
    def event_decorator(self, event_name: str):
        def decorator(f: t.Callable[..., None]) -> t.Callable[..., None]:
            if event_name not in self.events:
                logger.error(f"No handler found for event: {event_name}")
                raise KeyError(f"No handler for event {event_name}")
            self.events[event_name] = f
        return decorator
    
    def run(self):
        asyncio.run(self.async_run())