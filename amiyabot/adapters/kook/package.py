import json

from typing import List
from amiyabot.builtin.message import Event, Message, File
from amiyabot.adapters import BotAdapterProtocol

from ..common import text_convert


async def package_kook_message(instance: BotAdapterProtocol,
                               event: str,
                               message: dict):
    print(json.dumps(message, ensure_ascii=False))

    if message['type'] == 255:
        return Event(instance, event, message)

    extra: dict = message['extra']
    user: dict = extra['author']

    if user['bot']:
        return None

    t: int = extra['type']

    data = Message(instance, message)

    data.message_id = message['msg_id']
    data.message_type = message['channel_type']

    data.is_at = instance.appid in extra['mention']
    data.is_direct = message['channel_type'] == 'PERSON'
    data.is_at_all = extra['mention_all'] or extra['mention_here']

    data.user_id = user['id']
    data.guild_id = extra['guild_id']
    data.channel_id = message['target_id']
    data.nickname = user['nickname']
    data.avatar = user['vip_avatar'] or user['avatar']

    for user_id in extra['mention']:
        data.at_target.append(user_id)

    text = ''

    if t == 2:
        data.image.append(message['content'])

    if t == 3:
        data.video = message['content']

    if t == 9:
        text = extra['kmarkdown']['raw_content']

    if t == 10:
        card: List[dict] = json.loads(message['content'])
        for item in card:
            modules: List[dict] = item.get('modules', [])

            for module in modules:
                if module['type'] == 'file' and module['canDownload']:
                    data.files.append(File(module['src'], module['title']))

    if extra.get('quote'):
        if extra['quote']['type'] == 2:
            data.image.append(extra['quote']['content'])

    return text_convert(data, text.strip(), text)
