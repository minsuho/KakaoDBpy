from datetime import datetime
import aiosqlite
import json
import ast
from typing import Optional, List, Any, Dict

from .send import AsyncMsgSender
from .types import User, Chat, Channel, Attachments
from .KakaoDecrypt import KakaoDecrypt

import logging
logger = logging.getLogger(__name__)

class KakaoDB(KakaoDecrypt):
    def __init__(self, prefix: str, DB_PATH: str, BOT_ID: int, BOT_NAME: str, BOT_IP: str, BOT_PORT: int, router_dic: Dict, event_handlers: Dict) -> None:
        super().__init__()
        if len(prefix) != 1:
            logger.error("Invalid prefix length: %d", len(prefix))
            raise ValueError("prefix should be a single character")
        self.__prefix = prefix
        self.lastID = 0
        self.DB_PATH = DB_PATH.replace('\\', '/')
        self.BOT_ID = BOT_ID
        self.BOT_NAME = BOT_NAME
        self.BOT_IP = BOT_IP
        self.BOT_PORT = BOT_PORT
        self.router_dic = router_dic
        self.event_handlers = event_handlers
        self.names = {}
        self.db = None
        self.cur = None
        self.is_connected = False

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List[tuple]]:
        try:
            async with aiosqlite.connect(f"{self.DB_PATH}/KakaoTalk.db") as db:
                await db.execute(f"ATTACH DATABASE ? AS db2", (f"{self.DB_PATH}/KakaoTalk2.db",))
                async with db.execute(query, params or ()) as cursor:
                    if query.strip().upper().startswith('SELECT'):
                        return await cursor.fetchall()
                    await db.commit()
                    return cursor.rowcount
        except aiosqlite.OperationalError as e:
            logger.error(f"Operational error occurred: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None

    async def handle_message(self, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        text = chat_data.text.split()
        if text and text[0]:
            prefix = text[0][0]
            command = text[0][1:]
            if prefix in self.router_dic and command in self.router_dic[prefix]:
                command_info = self.router_dic[prefix][command]
                if command_info["room"] is None or channel_data.name in command_info["room"]:
                    await command_info["func"](user_data, chat_data, channel_data)
        if self.event_handlers.get('on_message'):
            await self.event_handlers['on_message'](user_data, chat_data, channel_data)

    async def handle_delete(self, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        if self.event_handlers.get('on_delete'):
            await self.event_handlers['on_delete'](user_data, chat_data, channel_data)

    async def handle_hide(self, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        if self.event_handlers.get('on_hide'):
            await self.event_handlers['on_hide'](user_data, chat_data, channel_data)

    async def handle_join(self, v: dict, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        first_member = v.get('member', v.get('members', [None])[0])
        if first_member:
            user_data.name = first_member['nickName']
            user_data.id = first_member['userId']
        if self.event_handlers.get('on_join'):
            await self.event_handlers['on_join'](user_data, chat_data, channel_data)

    async def handle_kick(self, v: dict, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        first_member = v.get('member', v.get('members', [None])[0])
        if first_member:
            user_data.name = first_member['nickName']
            user_data.id = first_member['userId']
        if self.event_handlers.get('on_kick'):
            await self.event_handlers['on_kick'](user_data, chat_data, channel_data)

    async def handle_leave(self, v: dict, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        first_member = v.get('member', v.get('members', [None])[0])
        if first_member:
            user_data.name = first_member['nickName']
            user_data.id = first_member['userId']
        if self.event_handlers.get('on_leave'):
            await self.event_handlers['on_leave'](user_data, chat_data, channel_data)

    async def handle_open_profile_change(self, after_user: User, before_user: User, channel_data: Channel) -> None:
        if self.event_handlers.get('on_open_profile_change'):
            await self.event_handlers['on_open_profile_change'](after_user, before_user, channel_data)

    async def handle_member_type_change(self, v: dict, user_data: User, channel_data: Channel) -> None:
        first_member = v.get('member', v.get('members', [None])[0])
        if first_member:
            user_data.name = first_member['nickName']
            user_data.id = first_member['userId']
        if self.event_handlers.get('on_member_type_change'):
            await self.event_handlers['on_member_type_change'](user_data, channel_data)

    async def handle_invite(self, v: dict, user_data: User, chat_data: Chat, channel_data: Channel) -> None:
        first_member = v.get('member', v.get('members', [None])[0])
        if first_member:
            user_data.name = first_member['nickName']
            user_data.id = first_member['userId']
        if self.event_handlers.get('on_invite'):
            await self.event_handlers['on_invite'](user_data, chat_data, channel_data)

    async def chat_check(self) -> None:
        limit = 1 if self.lastID == 0 else 5
        query = 'SELECT * FROM chat_logs ORDER BY id DESC LIMIT ?'
        res = await self.execute_query(query, (limit,))
        if res:
            res.reverse()
            for data in res:
                await self.process_message(data)

    async def process_message(self, data: tuple) -> None:
        if self.lastID < int(data[0]):
            self.lastID = int(data[0])
            user_data = await self.get_user(data[4])
            channel_data = await self.get_channel(data[3])
            chat_data = await self.get_chat(data[1])
            channel_data.send = AsyncMsgSender(channel_data.name, self.BOT_IP, self.BOT_PORT).send

            if data[2] == 0:
                v = json.loads(self.decrypt(data[4], json.loads(data[13])['enc'], data[5]))
                if v['feedType'] == 2:
                    await self.handle_leave(v, user_data, chat_data, channel_data)
                elif v['feedType'] == 4:
                    await self.handle_join(v, user_data, chat_data, channel_data)
                elif v['feedType'] == 6:
                    await self.handle_kick(v, user_data, chat_data, channel_data)
                elif v['feedType'] == 13:
                    await self.handle_hide(user_data, chat_data, channel_data)
                elif v['feedType'] == 14:
                    await self.handle_delete(user_data, chat_data, channel_data)
            elif data[2] in {1, 26}:
                await self.handle_message(user_data, chat_data, channel_data)

    async def update_names(self) -> None:
        query = "SELECT id, name, involved_chat_ids FROM db2.friends"
        data = await self.execute_query(query)

        if data:
            for id, name, involved_chat_ids in data:
                user_data = await self.get_user(id)
                if not self.names.get(id):
                    self.names[id] = [user_data]
                elif self.names[id][-1].name != name:
                    before_user = self.names[id][-1]
                    self.names[id].append(user_data)
                    channel_ids = ast.literal_eval(involved_chat_ids) if involved_chat_ids else []
                    channel_data = await self.get_channel(channel_ids[0]) if channel_ids else None
                    await self.handle_open_profile_change(user_data, before_user, channel_data)

    async def get_user(self, userid: int) -> User:
        if userid == self.BOT_ID:
            return User(name=self.BOT_NAME, id=self.BOT_ID, my=True)

        query = "SELECT * FROM db2.friends WHERE id = ?"
        user_db = await self.execute_query(query, (userid,))
        if not user_db:
            return User()

        user_db = user_db[0]
        id = user_db[2]
        name = self.decrypt(self.BOT_ID, user_db[-6], user_db[7])
        profile_image_url = (self.decrypt(self.BOT_ID, user_db[-6], user_db[9])
                            if user_db[9] != 'None' else None)
        full_profile_image_url = (self.decrypt(self.BOT_ID, user_db[-6], user_db[10])
                                if user_db[10] != 'None' else None)
        original_profile_image_url = (self.decrypt(self.BOT_ID, user_db[-6], user_db[11])
                                    if user_db[11] != 'None' else None)
        chat_id = user_db[-8].replace('[', '').replace(']', '').split(',')[0]
        v = json.loads(self.decrypt(self.BOT_ID, user_db[-6], user_db[18]))
        isHost = v.get('openlink', {}).get('mt') == 1
        isManager = v.get('openlink', {}).get('mt') == 2
        isOpenUser = v.get('openlink', {}).get('mt') == 4
        membertype = v.get('openlink', {}).get('mt', 0)

        return User(id=id, name=name, profile_image_url=profile_image_url,
                    full_profile_image_url=full_profile_image_url,
                    original_profile_image_url=original_profile_image_url,
                    membertype=membertype, chat_id=chat_id, isHost=isHost,
                    isManager=isManager, isOpenUser=isOpenUser)

    async def get_chat(self, logid: int) -> Chat:
        query = "SELECT * FROM chat_logs WHERE id = ?"
        chat_db = await self.execute_query(query, (logid,))
        if not chat_db:
            return Chat(None, None, None, None, None, None)

        chat_db = chat_db[0]
        v = json.loads(chat_db[13])
        enc = v['enc']
        chat_id = chat_db[1]
        text = self.decrypt(chat_db[4], enc, chat_db[5])
        sendTime = datetime.fromtimestamp(chat_db[7])
        chat_type = chat_db[2]

        att = None
        mentions = None
        if chat_db[6] not in {'', '{}', None, 'None'}:
            att_ = json.loads(self.decrypt(chat_db[4], enc, chat_db[6]))
            if chat_db[2] == 26 and 'src_logId' in att_:
                atta_chat = await self.get_chat(att_['src_logId'])
                atta_user = await self.get_user(att_['src_userId'])
                att = Attachments(atta_user, atta_chat)
            if chat_db[2] == 1 and 'mentions' in att_:
                mentions = [await self.get_user(i['user_id']) for i in att_['mentions']]

        return Chat(id=chat_id, text=text, sendTime=sendTime, chat_type=chat_type, attachment=att, mentions=mentions)

    async def get_channel(self, chat_id: int) -> Channel:
        query = "SELECT * FROM chat_rooms WHERE id = ?"
        channel_db = await self.execute_query(query, (chat_id,))
        if not channel_db:
            return Channel(None, None, None, None, None, None)

        channel_db = channel_db[0]
        id = channel_db[1]
        members = [await self.get_user(i) for i in channel_db[4].replace('[', '').replace(']', '').split(',')]
        v = json.loads(channel_db[11])
        enc = v['enc']
        lastChat = self.decrypt(self.BOT_ID, enc, channel_db[6])
        channel_type = channel_db[2]

        query = "SELECT name, user_id FROM db2.open_link WHERE id = (SELECT link_id FROM chat_rooms WHERE id = ?)"
        _data = await self.execute_query(query, (chat_id,))

        name = None
        host = None
        if _data:
            _data = _data[0]
            name = _data[0]
            host = await self.get_user(_data[1])

        return Channel(host=host, id=id, lastChat=lastChat, members=members, name=name, channel_type=channel_type)
