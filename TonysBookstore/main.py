from TonysBookstore.sql import show_available_books
from db_bookstore import DB
from ui import Menu

def main():
    with DB() as conn:
        cursor = conn.cursor
        conn.use_bookstore()
        conn.create_db()
        conn.create_table_book()
        conn.create_table_users()
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
        menu.add_options(["показать указанные в файле книги", "загрузить книги из файла", "загрузить свою книгу", "посмотреть книги в наличии", "зарегистрироваться как клиент",
                          "войти в свой аккаунт", "завершить работу"])
        while True:
            match menu.show_options():
                case 1:
                    conn.show_me_books_in_file("my_books")
                case 2:
                    conn.upload_your_books("my_books")
                case 3:
                    conn.upload_one_book()
                case 4:
                    conn.show_me_available_books()
                case 5:
                    conn.user_registration()
                case 7:
                    print("Good bye!! :)")
                    break
        cursor.execute("SELECT id, title, author, price, stock FROM books")
        for book in cursor:
            print(book)

if __name__ == "__main__":
    main()


