from typing import Optional, List
from datetime import datetime

class User:
        def __init__(self, 
                        id: Optional[int] = None, 
                        my: bool = False, 
                        name: Optional[str] = None, 
                        profile_image_url: Optional[str] = None, 
                        full_profile_image_url: Optional[str] = None, 
                        original_profile_image_url: Optional[str] = None, 
                        membertype: Optional[str] = None, 
                        chat_id: Optional[int] = None, 
                        isHost: bool = False, 
                        isManager: bool = False, 
                        isOpenUser: bool = False):
                self.id = id
                self.my = my
                self.name = name
                self.profile_image_url = profile_image_url
                self.full_profile_image_url = full_profile_image_url
                self.original_profile_image_url = original_profile_image_url
                self.membertype = membertype
                self.chat_id = chat_id
                self.isHost = isHost
                self.isManager = isManager
                self.isOpenUser = isOpenUser

class Chat:
        def __init__(self, 
                        id: Optional[int] = None, 
                        text: Optional[str] = None, 
                        sendTime: Optional[datetime] = None, 
                        chat_type: Optional[str] = None, 
                        attachment: Optional['Attachments'] = None, 
                        mentions: Optional[List[User]] = None, 
                        file: Optional['File'] = None):
                self.id = id
                self.text = text
                self.sendTime = sendTime
                self.chat_type = chat_type
                self.attachment = attachment
                self.mentions = mentions
                self.file = file

class Channel:
        def __init__(self, 
                        host: Optional[str] = None, 
                        id: Optional[int] = None, 
                        lastChat: Optional[Chat] = None, 
                        members: Optional[List[User]] = None, 
                        name: Optional[str] = None, 
                        channel_type: Optional[str] = None, 
                        send=None):
                self.host = host
                self.id = id
                self.lastChat = lastChat
                self.members = members
                self.name = name
                self.channel_type = channel_type
                self.send = send

class Attachments:
        def __init__(self, 
                        user: Optional[User] = None, 
                        chat: Optional[Chat] = None):
                self.user = user
                self.chat = chat

class File:
        def __init__(self, 
                        url: Optional[str] = None, 
                        name: Optional[str] = None, 
                        type: Optional[str] = None):
                self.url = url
                self.name = name
                self.type = type
