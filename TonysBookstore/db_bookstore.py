import os

from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
from sql import *

load_dotenv(".env_edit")


class DB:
    def __init__(self):
        self.__config = {"host": os.environ.get("DB_HOST", "localhost"),
                         "user": os.environ.get("DB_USER", "username"),
                         "password": os.environ.get("DB_PASSWORD", "password"),
                         "cursorclass": DictCursor}
        # self.__conn = None
        # self.__cursor = None

    def __enter__(self):
        self.__conn = pymysql.connect(**self.__config)
        self.__cursor = self.__conn.cursor()
        print("Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            if exc_type:
                self.__conn.rollback()
            else:
                self.__conn.commit()
            self.__conn.close()

    @property
    def cursor(self):
        return self.__cursor

    def use_bookstore(self):
        self.__cursor.execute(use_my_db)

    def create_db(self):
        self.__cursor.execute(create_my_db)
        self.__cursor.execute("SHOW DATABASES LIKE 'bookstore_anton_t'")
        db_check = self.__cursor.fetchone()
        if db_check:
            print("Database 'bookstore' created or already exists.")
        else:
            print("Database was not created (unknown reason).")

    def create_table_book(self):
        return self.__cursor.execute(create_table_books)

    def create_table_users(self):
        return self.__cursor.execute(create_table_users)

    def upload_your_books(self, books_file_name_csv):
        file_lines_into_list = []
        update_count = 0
        with open(books_file_name_csv, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip().split(",")
                if len(line) != 4:
                    print("Use only these fields: title, author, price, stock")
                    break
                title, author, price, stock = line
                line = (title, author, float(price), int(stock))
                if self.__cursor.execute(if_book_already_exists, (title, author)):
                    self.__cursor.execute(update_books_quantity, (stock, title, author))
                    update_count += 1
                else:
                    file_lines_into_list.append(line)
        self.__cursor.executemany(insert_books, file_lines_into_list)
        self.__conn.commit()
        print(f"{len(file_lines_into_list)} books uploaded. {update_count} updated.")
        file_lines_into_list.clear()

    def show_me_books_in_file(self, books_file_name_csv):
        with open(books_file_name_csv, "r", encoding="utf-8") as file:
            print("Presented books in file: ")
            for line in file:
                line = line.strip().split(",")
                title, author, price, stock = line
                print(f" - {title} {author}, {price}€ {stock} Available.")

    def user_registration(self):
        while True:
            try:
                your_credentials = input("Enter your login: ").lower()
                if len(your_credentials) < 4:
                    raise ValueError("Login must contain at least 4 symbols!!")
                if self.__cursor.execute(if_user_exists, your_credentials):
                    print("Such a user already exists in our system. We are really sorry.")
                    return
                break
            except ValueError as e:
                print(e)
        while True:
            try:
                your_pass = input("Set your unique password: ").lower()
                if len(your_pass) < 5:
                    raise ValueError("Password must be longer!! at least 5 symbols!!")
                break
            except ValueError as e:
                print(e)
        while True:
            try:
                init_balance = int(input("Choose your initial balance (EUR): "))
                break
            except ValueError:
                print("To set the balance use only numbers!!")
        self.__cursor.execute(insert_new_user_into_users, (your_credentials, your_pass, float(init_balance)))
        self.__conn.commit()
        print("Thank you for your registration! :)")
