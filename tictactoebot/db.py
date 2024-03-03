import logging
import sqlite3

from .enums import Language, Difficulty


DB_NAME = "gamedata.db"
logger = logging.getLogger(__name__)

# TODO: Добавить дополнительные параметры в таблицу User

class Database:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def __enter__(self) -> "Database":
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def create_tables(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                language TEXT DEFAULT 'en',
                difficulty TEXT DEFAULT 'easy',
                scores INTEGER DEFAULT 0,
                FOREIGN KEY(scores) REFERENCES Score(id)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_id ON User(chat_id)
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Score (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                player INTEGER DEFAULT 0,
                bot INTEGER DEFAULT 0,
                draw INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES User(id)
            )
            """
        )
        self.conn.commit()

    def add_user(
        self,
        chat_id: int,
        language: Language = Language.ENGLISH,
        difficulty: Difficulty = Difficulty.EASY
    ) -> None:
        self.cursor.execute('INSERT INTO User (chat_id, language, difficulty) VALUES (?, ?, ?)', (chat_id, language, difficulty))
        
        # Получение id добавленного пользователя
        user_id = self.cursor.lastrowid
        
        # Добавление score для добавленного пользователя
        self.cursor.execute('INSERT INTO Score (user_id, player, bot, draw) VALUES (?, 0, 0, 0)', (user_id,))
        
        self.conn.commit()

    def get_user_by_id(self, user_id: int):
        self.cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
        logger.info(f"Get user:{user_id} data from db")
        return self.cursor.fetchone()

    def get_user_by_chat_id(self, chat_id: int) -> tuple:
        self.cursor.execute("SELECT * FROM User WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        logger.info(f"Get user:{chat_id} data:{result} from db")
        return result

    def change_user_language(self, chat_id: int, new_language: Language) -> None:
        self.cursor.execute(
            "UPDATE User SET language = ? WHERE chat_id = ?", (new_language, chat_id)
        )
        logger.info(f"Changed user:{chat_id} language to {new_language}")
        self.conn.commit()

    def delete_user(self, user_id: int):
        self.cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
        self.conn.commit()

    def change_user_difficulty(self, chat_id: int, new_difficulty: Difficulty) -> None:
        self.cursor.execute(
            "UPDATE User SET difficulty = ? WHERE chat_id = ?",
            (new_difficulty, chat_id),
        )
        logger.info(f"Changed user:{chat_id} difficulty to {new_difficulty}")
        self.conn.commit()

    def get_user_score_by_id(self, id: int):
        self.cursor.execute("SELECT * FROM Score WHERE id = ?", (id,))
        result = self.cursor.fetchone()
        logger.info(f"Get user:{id} score:{result} from db")
        return result

    def get_user_score_by_user_id(self, user_id: int):
        self.cursor.execute("SELECT * FROM Score WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        logger.info(f"Get user:{user_id} score:{result} from db")
        return result

    def update_user_score(self, user_id: int, player: int, bot: int, draw: int) -> None:
        self.cursor.execute(
        """
            UPDATE Score 
            SET player = ?,
                bot = ?,
                draw = ?
            WHERE user_id = ?
        """,
            (player, bot, draw, user_id),
        )
        logger.info(f"Updated user:{user_id} scores")
        self.conn.commit()
