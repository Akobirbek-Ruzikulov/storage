import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname='akobir1',
        user='postgres',
        password='1212',
        host='localhost',
        port='5432'

    )


def create_ta():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tipe (
        id SERIAL PRIMARY KEY,
        tipy TEXT NOT NULL
    )
    ''')

    cursor.execute('INSERT INTO Tipe(tipy) VALUES (%s)',('Birinchi_taom',))
    cursor.execute('INSERT INTO Tipe(tipy) VALUES (%s)',('Ikkinchi taom',))
    cursor.execute('INSERT INTO Tipe(tipy) VALUES (%s)', ('Uchinchi_taom',))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_Billur (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        discription TEXT NOT NULL,
        price INTEGER NOT NULL,
        tipe_id INTEGER REFERENCES Tipe(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Order_menu (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        menu_id INTEGER REFERENCES menu_Billur(id) ON DELETE CASCADE
    )
    ''')

    connection.commit()
    print("Barcha jadvallar yaratildi!")
    connection.close()

def remove_menu(name):
    connection= get_connection()
    cursor=connection.cursor()
    cursor.execute("DELETE FROM menu_Billur WHERE name = %s", (name,))
    connection.commit()
    print(f"{name} menyudan o'chirildi!")

def add_menu(name,discription,price,tipe_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Tipe')
    cursor.execute('''INSERT INTO menu_Billur (name, discription, price, tipe_id)
    VALUES (%s, %s, %s, %s)''',
    (name, discription, price, tipe_id))
    connection.commit()
    print(f"'{name}'-menuga  qo'shildi")
    connection.close()


def add_order(name, menu_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''
    INSERT INTO Order_menu (name, menu_id)
    VALUES (%s, %s)
    ''', (name, menu_id))
    connection.commit()
    print(f"'{name}' buyurtmaga qo'shildi!")
    connection.close()


def get_menu():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
    SELECT menu_Billur.id, menu_Billur.name, menu_Billur.discription AS description, menu_Billur.price AS price,
    Tipe.tipy AS type
    FROM menu_Billur
    JOIN Tipe ON menu_Billur.tipe_id = Tipe.id
    ''')
    menu_Billur = cursor.fetchall()
    for menu in menu_Billur:
        print(menu)

    connection.close()

def get_order(name):
    connection=get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM menu_Billur WHERE name = %s", (name,))
    dish = cursor.fetchone()
    if dish:
        cursor.execute("INSERT INTO Order_menu (menu_id) VALUES (%s)", (dish[0],))
        connection.commit()
        print(f"{name} buyurtmaga qo'shildi!")
    else:
        print("Bunday taom topilmadi!")


def get_sum():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT COALESCE(SUM(menu_Billur.price), 0) FROM Order_menu
    JOIN menu_Billur ON Order_menu.menu_id = menu_Billur.id
     ''')
    total = cursor.fetchone()[0]

    connection.commit()
    connection.close()
    return total

if __name__ == '__main__':
    create_ta()

    while True:
        print("\nBillur restorani  boshqaruv tizimi")
        print("1. Menyuga taom qo'shish")
        print("2. Taomni o'chirish")
        print("3. Menyuni ko'rish")
        print("4. Buyurtma berish ")
        print("5. Chiqish")

        choice = input("Tanlovingizni kiriting: ")

        if choice == '1':
            name = input("Taom nomi: ")
            discription = input("Taom tavsifi:")
            price = int(input("Taom narxi:"))
            tipe_id=int(input("Taom turi (1.starter/2.main/3.dessert):"))
            add_menu(name,discription,price,tipe_id)
        elif choice == '2':
            name = input("O'chiriladigan taom nomini kiriting: ")
            remove_menu(name)
        elif choice == '3':
            print("\nMenyu:")
            get_menu()
        elif choice == '4':
            get_menu()
            name = input("Taom nomi:")
            menu_id = input("Menyudagi taomni raqami:")
            add_order(name,menu_id)

        elif choice == '5':
            get_sum()
            print("Dasturdan chiqildi.")
            break
        else:
            print("Noto'g'ri tanlov! Qaytadan urinib ko'ring.")


