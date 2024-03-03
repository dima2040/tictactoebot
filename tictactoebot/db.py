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
                chat_id TEXT,
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
        chat_id: str,
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
        return self.cursor.fetchone()

    def get_user_by_chat_id(self, chat_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM User WHERE chat_id = ?", (chat_id,))
        return self.cursor.fetchone()

    def change_user_language(self, chat_id: str, new_language: Language) -> None:
        self.cursor.execute(
            "UPDATE User SET language = ? WHERE chat_id = ?", (new_language, chat_id)
        )
        logger.info(f"Changed user:{chat_id} language to {new_language}")
        self.conn.commit()

    def delete_user(self, user_id: int):
        self.cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
        self.conn.commit()

    def change_user_difficulty(self, chat_id: str, new_difficulty: Difficulty) -> None:
        self.cursor.execute(
            "UPDATE User SET difficulty = ? WHERE chat_id = ?",
            (new_difficulty, chat_id),
        )
        logger.info(f"Changed user:{chat_id} difficulty to {new_difficulty}")
        self.conn.commit()

    def get_user_score_by_id(self, id: int):
        self.cursor.execute("SELECT * FROM Score WHERE id = ?", (id,))
        return self.cursor.fetchone()

    def get_user_score_by_user_id(self, user_id: int):
        self.cursor.execute("SELECT * FROM Score WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    def update_user_score(
        self, user_id: int, player_inc: int = 0, bot_inc: int = 0, draw_inc: int = 0
    ) -> None:
        self.cursor.execute(
            """
            UPDATE Score 
            SET player = player + ?,
                bot = bot + ?,
                draw = draw + ?
            WHERE user_id = ?
        """,
            (player_inc, bot_inc, draw_inc, user_id),
        )
        logger.info(f"Updated user:{user_id} scores")
        self.conn.commit()


if __name__ == "__main__":
    with Database(DB_NAME) as db:
        db.add_user('12345', Language.ENGLISH, Difficulty.HARD)
        user = db.get_user_by_chat_id('12345')
        assert user == {}
        db.change_user_language('12345', Language.SPANISH)
        db.change_user_difficulty('12345', Difficulty.EASY)
        user = db.get_user_by_chat_id('12345')
        assert user == {}
        db.update_user_score(user_id=1, player_inc=1)
        score = db.get_user_score_by_id()
        assert score == {}
