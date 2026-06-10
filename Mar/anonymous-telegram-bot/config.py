import os
import sys

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS")

if not TOKEN:
    print("❌ BOT_TOKEN missing")
    sys.exit(1)

if not ADMIN_IDS_RAW:
    print("❌ ADMIN_IDS missing")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",")]
