# KakaoDBpy

## Redroid, 데이터베이스, 봇 애플리케이션 기반의 챗봇

### 초기 설정

1. **레포지토리 클론**

   ```bash
   git clone https://github.com/suhomin/kakaoDBBotpy.git
   cd PyKakaoDBBot
   ```

2. **Docker 설치**

   Docker 설치 방법은 [Docker 공식 설치 가이드](https://docs.docker.com/engine/install/)를 참고하세요.

3. **Redroid 설치 및 실행**

   ```bash
   docker run -itd --privileged \
       -v ~/data:/data \
       -p 5555:5555 \
       -p 3000:3000 \
       redroid/redroid:11.0.0-latest \
       ro.product.model=SM-T970 \
       ro.product.brand=Samsung
   ```

4. **ADB, scrcpy, 봇 앱, 카카오톡 설치**

   ```bash
   sudo apt install android-sdk-platform-tools scrcpy
   adb connect localhost:5555
   adb install YOUR_APP.apk
   scrcpy -s localhost:5555
   ```

5. **필요한 패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```

### 사용법

#### 기본 사용법

```python
import json
from kakaobot.bot import Bot

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

bot = Bot(**config)

@bot.on_command("!ping")
async def ping(user, chat, channel):
    await channel.send("Pong!")

@bot.on_message
async def message(user, chat, channel):
    print(chat.text)

bot.run()
```

#### 파일 분리 예시

```python
# main.py
import json
from kakaobot.bot import Bot

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

bot = Bot(**config)
bot.load_events("./events")
bot.load_commands("./commands")
bot.run()
```

```python
# events/on_message.py
from kakaobot.bot import Bot

def setup_events(bot: Bot):
    @bot.on_message
    async def greet(user, chat, channel):
        print(chat.text)
```

```python
# commands/ping.py
from kakaobot.bot import Bot

def setup_commands(bot: Bot):
    @bot.on_command("!ping")
    async def ping(user, chat, channel):
        await channel.send("Pong!")
```

### 이벤트 리스너들

1. **on_command(command)**: 특정 명령어가 입력될 때 호출됩니다.

   ```python
   @bot.on_command("!ping")
   async def ping(user, chat, channel):
   ```

2. **on_message**: 메시지가 수신될 때 호출됩니다.

   ```python
   @bot.on_message
   async def message(user, chat, channel):
   ```

3. **on_delete**: 메시지가 삭제될 때 호출됩니다.

   ```python
   @bot.on_delete
   async def delete(user, chat, channel):
   ```

4. **on_join**: 누군가 오픈 채팅방에 참여할 때 호출됩니다.

   ```python
   @bot.on_join
   async def join(user, chat, channel):
   ```

5. **on_leave**: 누군가 그룹 채팅방을 떠날 때 호출됩니다. 강퇴될 때도 호출됩니다.

   ```python
   @bot.on_leave
   async def leave(user, chat, channel):
   ```

6. **on_kick**: 누군가 오픈 채팅방에서 강퇴당할 때 호출됩니다.

   ```python
   @bot.on_kick
   async def kick(user, chat, channel):
   ```

7. **on_invite**: 그룹 채팅방에 초대될 때 호출됩니다.

   ```python
   @bot.on_invite
   async def invite(user, chat, channel):
   ```

8. **on_open_profile_change**: 프로필이 변경될 때 호출됩니다.

   ```python
   @bot.on_open_profile_change
   async def open_profile_change(user, chat, channel):
   ```

9. **on_member_type_change**: 방장이나 부방장이 변경될 때 호출됩니다.

   ```python
   @bot.on_member_type_change
   async def member_type_change(user, chat, channel):
   ```

### 객체 속성

#### 사용자(User)

- **user.id**: 유저의 고유 번호를 반환합니다.
- **user.my**: 유저가 자기 자신인지 여부를 반환합니다.
- **user.profile_image_url**: 유저의 프로필 사진 URL을 반환합니다.
- **user.full_profile_image_url**: 유저의 전체 프로필 사진 URL을 반환합니다.
- **user.original_profile_image_url**: 유저의 원본 프로필 사진 URL을 반환합니다.
- **user.membertype**: 오픈채팅방에서 유저의 멤버 타입을 반환합니다.
- **user.chat_id**: 유저의 채팅방 ID를 반환합니다.
- **user.isHost**: 유저가 방장인지 여부를 반환합니다.
- **user.isManager**: 유저가 부방장인지 여부를 반환합니다.
- **user.isOpenUser**: 유저가 오픈채팅 유저인지 여부를 반환합니다.

#### 채팅(Chat)

- **chat.id**: 채팅의 고유 번호를 반환합니다.
- **chat.text**: 채팅 내용을 반환합니다.
- **chat.sendTime**: 채팅 보낸 시간을 반환합니다.
- **chat.chat_type**: 채팅 타입을 반환합니다.
- **chat.attachment**: 답장한 메시지 정보를 반환합니다.
- **chat.mentions**: 맨션한 유저 정보를 반환합니다.
- **chat.file**: 파일 정보를 반환합니다.

#### 채팅방(Channel)

- **channel.host**: 채팅방의 반장 정보를 반환합니다.
- **channel.id**: 채팅방의 고유 번호를 반환합니다.
- **channel.lastChat**: 채팅방의 마지막 채팅을 반환합니다.
- **channel.members**: 채팅방 멤버들을 반환합니다.
- **channel.name**: 채팅방 이름을 반환합니다.
- **channel.channel_type**: 채팅방 타입을 반환합니다.
- **channel.send(text)**: 채팅방에 메시지를 보냅니다.

#### 첨부파일(Attachments)

- **attachments.user**: 유저 정보를 반환합니다.
- **attachments.chat**: 채팅 정보를 반환합니다.

#### 파일(File)

- **file.url**: 파일의 URL을 반환합니다.
- **file.name**: 파일 이름을 반환합니다.
- **file.type**: 파일 타입을 반환합니다.
