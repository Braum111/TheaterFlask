# models.py
from db import get_db


class UserModel:
    @staticmethod
    def create_user(username, email, password_hash):
        db = get_db()
        cursor = db.cursor()
        query = "INSERT INTO User (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password_hash))
        db.commit()

    @staticmethod
    def get_user_by_username(username):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE username=%s"
        cursor.execute(query, (username,))
        return cursor.fetchone()

    @staticmethod
    def get_user_by_id(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE user_id=%s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_user_tickets(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Так как в Ticket у нас Performance_performance_id и User_user_id
        # Связь к Play через Performance: p.Play_play_id -> Play.play_id
        query = """SELECT t.ticket_id, pl.title AS play_title, p.date_time, p.venue, t.price, t.purchase_date
                   FROM Ticket t
                   JOIN Performance p ON t.Performance_performance_id = p.performance_id
                   JOIN Play pl ON p.Play_play_id = pl.play_id
                   WHERE t.User_user_id = %s"""
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

    @staticmethod
    def get_user_reviews(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = """SELECT r.review_id, r.rating, r.text, r.date_posted
                   FROM Review r
                   WHERE r.User_user_id = %s
                   ORDER BY r.date_posted DESC"""
        cursor.execute(query, (user_id,))
        return cursor.fetchall()


class PlayModel:
    @staticmethod
    def get_all_plays():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM Play"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_play_by_id(play_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM Play WHERE play_id=%s"
        cursor.execute(query, (play_id,))
        return cursor.fetchone()

    @staticmethod
    def create_play(title, description, genre, duration):
        db = get_db()
        cursor = db.cursor()
        # Хранимая процедура AddPlay предполагается без изменений.
        cursor.callproc('AddPlay', [title, description, genre, duration])
        db.commit()

    @staticmethod
    def update_play(play_id, title, description, genre, duration):
        db = get_db()
        cursor = db.cursor()
        query = """UPDATE Play SET title=%s, description=%s, genre=%s, duration=%s WHERE play_id=%s"""
        cursor.execute(query, (title, description, genre, duration, play_id))
        db.commit()

    @staticmethod
    def delete_play(play_id):
        db = get_db()
        cursor = db.cursor()
        query = "DELETE FROM Play WHERE play_id=%s"
        cursor.execute(query, (play_id,))
        db.commit()

    @staticmethod
    def search_plays(keyword, genre):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Базовый запрос
        query = "SELECT * FROM Play WHERE 1=1"
        params = []

        # Если есть ключевое слово, добавляем фильтр по названию
        if keyword:
            query += " AND title LIKE %s"
            params.append('%' + keyword + '%')

        # Если есть жанр, добавляем фильтр по жанру
        if genre:
            query += " AND genre LIKE %s"
            params.append('%' + genre + '%')

        cursor.execute(query, tuple(params))
        return cursor.fetchall()

class PerformanceModel:
    @staticmethod
    def get_performances_by_play(play_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Здесь нужно использовать p.Play_play_id вместо p.play_id
        query = """SELECT p.performance_id, p.Play_play_id AS play_id, p.date_time, p.venue, p.available_seats
                   FROM Performance p
                   WHERE p.Play_play_id=%s
                   ORDER BY p.date_time"""
        cursor.execute(query, (play_id,))
        return cursor.fetchall()

    @staticmethod
    def get_performance_by_id(performance_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Соединение с Play: p.Play_play_id = pl.play_id
        query = """SELECT p.performance_id, p.Play_play_id AS play_id, p.date_time, p.venue, p.available_seats, pl.title
                   FROM Performance p
                   JOIN Play pl ON p.Play_play_id = pl.play_id
                   WHERE p.performance_id=%s"""
        cursor.execute(query, (performance_id,))
        return cursor.fetchone()

    @staticmethod
    def create_performance(play_id, date_time, venue, available_seats):
        db = get_db()
        cursor = db.cursor()
        # Используем Play_play_id
        query = """INSERT INTO Performance (Play_play_id, date_time, venue, available_seats)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (play_id, date_time, venue, available_seats))
        db.commit()

    @staticmethod
    def update_performance(performance_id, play_id, date_time, venue, available_seats):
        db = get_db()
        cursor = db.cursor()
        query = """UPDATE Performance
                   SET Play_play_id=%s, date_time=%s, venue=%s, available_seats=%s
                   WHERE performance_id=%s"""
        cursor.execute(query, (play_id, date_time, venue, available_seats, performance_id))
        db.commit()

    @staticmethod
    def delete_performance(performance_id):
        db = get_db()
        cursor = db.cursor()
        query = "DELETE FROM Performance WHERE performance_id=%s"
        cursor.execute(query, (performance_id,))
        db.commit()

    @staticmethod
    def get_all_performances():
        conn = get_db()  # Если у вас есть функция get_db() для получения соединения
        cursor = conn.cursor(dictionary=True)
        # Предположим, что таблица называется Performance
        # и имеет поля performance_id, date_time, venue, available_seats
        # а также связь через Play_play_id -> Play.play_id
        query = """
        SELECT p.performance_id, p.date_time, p.venue, p.available_seats, pl.title
        FROM Performance p
        JOIN Play pl ON p.Play_play_id = pl.play_id
        ORDER BY p.date_time
        """
        cursor.execute(query)
        performances = cursor.fetchall()
        cursor.close()
        return performances

class TicketModel:
    @staticmethod
    def create_ticket(performance_id, price, user_id):
        db = get_db()
        cursor = db.cursor()
        # В таблице Ticket колонка: Performance_performance_id и User_user_id
        query = """INSERT INTO Ticket (Performance_performance_id, purchase_date, price, User_user_id) 
                   VALUES (%s, CURDATE(), %s, %s)"""
        cursor.execute(query, (performance_id, price, user_id))
        db.commit()


class ReviewModel:
    @staticmethod
    def get_all_reviews():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = """SELECT r.review_id, r.rating, r.text, r.date_posted, u.username
                   FROM Review r
                   JOIN User u ON r.User_user_id = u.user_id
                   ORDER BY r.date_posted DESC"""
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def add_review(rating, text, user_id):
        db = get_db()
        cursor = db.cursor()
        query = "INSERT INTO Review (rating, text, date_posted, User_user_id) VALUES (%s, %s, CURDATE(), %s)"
        cursor.execute(query, (rating, text, user_id))
        db.commit()
