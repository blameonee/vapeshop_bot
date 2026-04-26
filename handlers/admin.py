import os
from dotenv import load_dotenv


from aiogram import Router

admin_router = Router()

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))