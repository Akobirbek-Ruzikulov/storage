# from os.path import curdir
#
# import psycopg2
#
# def get_connection():
#     return psycopg2.connect(
#         dbname='akobir1',
#         user='postgres',
#         password='1212',
#         host='localhost',
#         port='5432'
#
#
#     )
#
# def create_tables():
#     """Kutubxona uchun jadvallarni yaratish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#
#     # Catalog jadvali
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS catalog (
#         id SERIAL PRIMARY KEY,
#         name TEXT NOT NULL
#     )
#     ''')
#
#     # Author jadvali
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS author (
#         id SERIAL PRIMARY KEY,
#         name TEXT NOT NULL,
#         country TEXT
#     )
#     ''')
#
#     # Book jadvali
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS book (
#         id SERIAL PRIMARY KEY,
#         title TEXT NOT NULL,
#         catalog_id INTEGER REFERENCES catalog(id) ON DELETE CASCADE,
#         author_id INTEGER REFERENCES author(id) ON DELETE CASCADE,
#         published_year INTEGER
#     )
#     ''')
#
#     connection.commit()
#     print("Barcha jadvallar yaratildi!")
#     connection.close()
#
#
# def add_catalog(name):
#     connection=get_connection()
#     cursor=connection.cursor()
#
#     cursor.execute('INSERT INTO catalog(name) VALUES (%s)',(name,))
#     connection.commit()
#     print(f"Katalog '{name}' qo'shildi")
#     connection.close()
#
# def add_author(name, country):
#     """Muallif qo'shish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#     cursor.execute('INSERT INTO author (name, country) VALUES (%s, %s)', (name, country))
#     connection.commit()
#     print(f"Muallif '{name}' qo'shildi!")
#     connection.close()
#
# def add_book(title, catalog_id, author_id, published_year):
#     """Kitob qo'shish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#     cursor.execute('''
#     INSERT INTO book (title, catalog_id, author_id, published_year)
#     VALUES (%s, %s, %s, %s)
#     ''', (title, catalog_id, author_id, published_year))
#     connection.commit()
#     print(f"Kitob '{title}' qo'shildi!")
#     connection.close()
#
# def get_catalogs():
#     """Barcha kataloglarni ko'rish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#
#     cursor.execute('SELECT * FROM catalog')
#     catalogs = cursor.fetchall()
#     for catalog in catalogs:
#         print(catalog)
#
#     connection.close()
#
# def get_authors():
#     """Barcha mualliflarni ko'rish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#     cursor.execute('SELECT * FROM author')
#     authors = cursor.fetchall()
#     for author in authors:
#         print(author)
#     connection.close()
#
# def get_books():
#     """Barcha kitoblarni ko'rish"""
#     connection = get_connection()
#     cursor = connection.cursor()
#     cursor.execute('''
#     SELECT book.id, book.title, catalog.name AS catalog, author.name AS author, book.published_year
#     FROM book
#     JOIN catalog ON book.catalog_id = catalog.id
#     JOIN author ON book.author_id = author.id
#     ''')
#     books = cursor.fetchall()
#     for book in books:
#         print(book)
#     connection.close()
#
# if __name__ == '__main__':
#     create_tables()
#
#     while True:
#         print("\nKutubxona boshqaruv tizimi:")
#         print("1. Katalog qo'shish")
#         print("2. Muallif qo'shish")
#         print("3. Kitob qo'shish")
#         print("4. Barcha kataloglarni ko'rish")
#         print("5. Barcha mualliflarni ko'rish")
#         print("6. Barcha kitoblarni ko'rish")
#         print("7. Chiqish")
#
#         choice = input("Tanlovingizni kiriting: ")
#
#         if choice == '1':
#             name = input("Katalog nomini kiriting: ")
#             add_catalog(name)
#         elif choice == '2':
#             name = input("Muallif nomini kiriting: ")
#             country = input("Muallif mamlakatini kiriting: ")
#             add_author(name, country)
#         elif choice == '3':
#             title = input("Kitob nomini kiriting: ")
#             catalog_id = int(input("Katalog ID sini kiriting: "))
#             author_id = int(input("Muallif ID sini kiriting: "))
#             published_year = int(input("Nashr yilini kiriting: "))
#             add_book(title, catalog_id, author_id, published_year)
#         elif choice == '4':
#             get_catalogs()
#         elif choice == '5':
#             get_authors()
#         elif choice == '6':
#             get_books()
#         elif choice == '7':
#             print("Dasturdan chiqildi.")
#             break
#         else:
#             print("Noto'g'ri tanlov! Qaytadan urinib ko'ring.")
#
#
#
#
#
