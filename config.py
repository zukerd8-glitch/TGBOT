import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

if not BOT_TOKEN or not ADMIN_ID or not CHANNEL_ID:
    raise RuntimeError(
        "Environment variables BOT_TOKEN, ADMIN_ID, CHANNEL_ID must be set"
    )
