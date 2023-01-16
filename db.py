import sqlite3
from os import path, mkdir


db_path = path.join(f"{path.abspath('db')}", "couple_db.db")

def create_folder() -> None:
    """Создаёт папку для БД"""
    if not path.isdir("db"):
        mkdir("db")

def create_db() -> None:
    """Создаёт таблицу БД, если её нет"""
    create_folder()
    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS couple(
            id INTEGER PRIMARY KEY,
            black_listed INTEGER,
            favorite INTEGET
        );
        """)
        conn.commit()

def check_exist(couple_id: int) -> bool:
    """Проверяет добавлена ли пара в БД"""
    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT id FROM couple WHERE id = ?;
        """, (couple_id,))
        if cur.fetchone() is None:
            return False
        return True

def add_couple(couple_id: int) -> None:
    """Добавляет подходящую пару в БД"""

    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO couple(id)
        VALUES (?);
        """, (couple_id,))
        conn.commit()


# Ниже функции с заделом на будущее

def add_to_black_list(couple_id) -> None:
    """Добавляет пару в черный список"""
    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        UPDATE couple SET black_listed = %s WHERE id = %s;
        """, (1, couple_id))
        conn.commit()

def add_to_favorite(couple_id) -> None:
    """Добавляет пару в избранное"""
    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        UPDATE couple SET favorite = %s WHERE id = %s;
        """, (1, couple_id))
        conn.commit()