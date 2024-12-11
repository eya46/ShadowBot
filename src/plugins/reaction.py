from nonebot import logger, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent


@on_command("e").handle()
async def _(bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()):
    reply = event.reply

    if reply is None:
        return

    emojiId = None
    if len(faces := message.get("face", 1)) > 0:
        emojiId = faces[0].data.get("id")
        logger.info(f'emojiData: {faces[0].data.get("id")} {message.get("face", 1)}')
    elif len(text := message.get("text", 1)) > 0:
        try:
            emojiId = int(str(text[0]))
        except:
            pass

    try:
        await bot.delete_msg(message_id=event.message_id)
    except:
        logger.error(f"delete message failed {event.message_id}")

    logger.info(f"reaction: {reply.message_id} {event.message_id} {emojiId} {message.get('face', 1)}")
    if emojiId is None:
        return await bot.call_api("set_msg_emoji_like", message_id=event.message_id, emoji_id=38)

    await bot.call_api("set_msg_emoji_like", message_id=reply.message_id, emoji_id=emojiId)
