
LOG_CHAT_ID = -5514443061

async def send_log(event, log, **data):
    user = event.from_user

    text = (
        f"👤 {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 @{user.username or 'нет username'}\n\n"
        f"{log}"
    )

    if data:
        text += "\n\n"

        for key, value in data.items():
            text += f"{key}: {value}\n"

    await event.bot.send_message(
        chat_id=LOG_CHAT_ID,
        text=text
    )