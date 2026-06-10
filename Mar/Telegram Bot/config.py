import os

def get_token():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ BOT_TOKEN is not set")
    return token

def get_admin_ids():
    admin_ids = os.getenv("ADMIN_IDS")
    if not admin_ids:
        raise RuntimeError("❌ ADMIN_IDS is not set")
    return [int(x.strip()) for x in admin_ids.split(",")]
