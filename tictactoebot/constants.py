from .data import GameData
from dotenv import load_dotenv
import os

load_dotenv()

DATA_GAME=GameData()
BOT_TOKEN = os.getenv('TTT_API_TOKEN')