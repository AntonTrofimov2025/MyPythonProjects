from TonysBookstore.sql import user_auth
from db_bookstore import DB
from ui import Menu
from mongodb import Mongo

def main():
    with Mongo() as mongo_db, DB(mongo_db) as conn:
        cursor = conn.cursor
        conn.use_bookstore()
        conn.create_db()
        conn.create_table_book()
        conn.create_table_users()
        conn.create_table_purchases()
        # cursor.execute("DELETE FROM books")
        # cursor.execute("DELETE FROM users")
        # cursor.execute("ALTER TABLE books auto_increment=1")
        # cursor.execute("ALTER TABLE users auto_increment=1")
        cursor.execute("SHOW TABLES")
        # res = cursor.fetchall()
        # print(res)
        # print("Tables in 'bookstore_anton_t': ", *(f" - {value}" for table in cursor for key, value in table.items()), sep="\n")
        print("Tables in 'bookstore_anton_t': ", *(f" - {table['Tables_in_bookstore_anton_t']}" for table in cursor), sep="\n")

        menu = Menu()
        menu.add_options(["показать указанные в файле книги", "загрузить книги из файла", "загрузить свою книгу",
                          "зарегистрироваться как клиент", "войти в свой аккаунт", "Show Top10 user queries",
                          "завершить работу"])
        is_first_start = True
        while True:
            if not is_first_start:
                input("Press ENTER to continue...")
            match menu.show_options():
                case 1:
                    conn.show_me_books_in_file("my_books")
                case 2:
                    conn.upload_your_books("my_books")
                case 3:
                    conn.upload_one_book()
                case 4:
                    conn.user_registration()
                case 5:
                    user_data = conn.user_authorization()
                    if user_data:
                        print(f"Greetings, {user_data['name']}!", f"your user_id: {user_data['id']}", sep="\n")
                        user_menu = Menu()
                        user_menu.add_options(
                            ["Show your current balance", "просмотреть список всех книг в наличии",
                             "выполнить поиск книги по части названия", "купить выбранную книгу",
                             "выйти из аккаунта и вернуться в главное меню"])
                        first_start = True
                        while True:
                            if not first_start:
                                input("Press ENTER to continue...")
                            match user_menu.show_options():
                                case 1:
                                    print(f"Your current balance: {user_data['balance']}")
                                case 2:
                                    conn.show_me_available_books()
                                case 3:
                                    conn.show_book_like()
                                case 4:
                                    conn.buy_book(user_data)
                                    cursor.execute(user_auth, (user_data['name'], user_data['password']))
                                    user_data = cursor.fetchone()
                                case 5:
                                    break
                            first_start = False
                case 6:
                    conn.show_top10_queries()
                case 7:
                    print("Good bye!! :)")
                    break
            is_first_start = False
        # cursor.execute("SELECT id, title, author, price, stock FROM books")
        # for book in cursor:
        #     print(book)

if __name__ == "__main__":
    main()


