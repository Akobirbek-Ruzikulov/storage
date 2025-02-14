import psycopg2

conn = psycopg2.connect(
    dbname="akobir1",
    user="postgres",
    password="****",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

def create_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        password TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        phone INT NOT NULL ,
        email VARCHAR(100) UNIQUE,
        password TEXT NOT NULL,
        balance DECIMAL(10,2) NOT NULL CHECK(balance > -15000000)
    );
    
    CREATE TABLE IF NOT EXISTS category (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        category_id INT REFERENCES category(id) ON DELETE CASCADE,
        price DECIMAL(10,2) NOT NULL CHECK (price > 0),
        available_quantity INT NOT NULL CHECK (available_quantity >= 0)
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        customer_id INT REFERENCES customers(id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS order_details (
        id SERIAL PRIMARY KEY,
        order_id INT,
        product_id INT,
        quantity INT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    ''')
    conn.commit()

def show_category():
    cursor.execute("SELECT name FROM category")
    cat = cursor.fetchall()
    if not cat:
        print("⚠️ Tur mavjud emas!")
        return False
    print("\n📂 Mavjud turlar:")
    for c in cat:
        print(f"- {c[0]}")
    return True

def add_category():
    name = input("Tur nomini kiriting: ").strip()
    if not name:
        print("⚠️ Tur nomi bo‘sh bo‘lishi mumkin emas!")
        return

    try:
        cursor.execute("INSERT INTO category (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))
        conn.commit()
        print(f"✅ Tur '{name}' qo‘shildi!")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

def add_customer():

    username = input("👤 Ismingiz :").strip()
    if not username:
        print("⚠️ Ism bo‘sh bo‘lishi mumkin emas!")
        return

    phone = input("📞 Raqamingizni kiriting (masalan--->901234567):")
    email = input("📧 Elektron pochta manzilingiz: ").strip()
    password = input("🔑 Yangi parol kiriting:").strip()

    try:
        balance = float(input("💰 Balansni kiriting: "))
        if balance < 0:
            print("⚠️ Balans manfiy bo‘lishi mumkin emas!")
            return

        cursor.execute("""INSERT INTO customers (username, phone, email, password, balance) 
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING""",
                       (username, phone, email, password, balance))
        conn.commit()
        print(f"✅ Mijoz '{username}' qo‘shildi!")
    except ValueError:
        print("⚠️ Balans raqam bo‘lishi kerak!")

def add_product():
    if not show_category():
        print("⚠️ Avval tur qo‘shing!")
        return

    name = input("\nTovar nomini kiriting: ").strip()
    cat = input("Tur nomini kiriting: ").strip()

    cursor.execute("SELECT id FROM category WHERE name = %s", (cat,))
    cat_id = cursor.fetchone()

    if not cat_id:
        print("⚠️ Bunday tur topilmadi!")
        return

    try:
        price = float(input("💰 Narxini kiriting: "))
        available_quantity = int(input("📦 Mavjud sonini kiriting: "))

        if price <= 0 or available_quantity < 0:
            print("⚠️ Narx musbat bo‘lishi, son esa 0 yoki undan katta bo‘lishi kerak!")
            return

        cursor.execute(
            "INSERT INTO products (name, category_id, price, available_quantity) VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING",
            (name, cat_id[0], price, available_quantity)
        )
        conn.commit()
        print(f"✅ '{name}' tovar qo‘shildi!")
    except ValueError:
        print("⚠️ Narx va son raqam bo‘lishi kerak!")

def remove_pro():
    name = input("🗑️ O'chiriladigan tovar nomi:")
    cursor.execute("""
    DELETE FROM products WHERE name = %s RETURNING name
    """,(name,))
    deleted_product = cursor.fetchone()
    if deleted_product:
        conn.commit()
        print(f"✅ {deleted_product[0]} tovari o‘chirildi.")
    else:
        print("⚠️ Bunday tovar topilmadi yoki allaqachon o‘chirilgan.")

def show_product():
    cursor.execute("SELECT name, price, available_quantity FROM products")
    product = cursor.fetchall()

    if not product:
        print("⚠️ Tovarlar mavjud emas!")
        return False

    print("\n Mavjud tovarlar:")
    for pro in product:
        print(f"- {pro[0]} | {pro[1]}so'm- (mavjud: {pro[2]} dona)")

    return True

def view_all_orders():
    print("\n📜 Barcha buyurtmalar:")
    cursor.execute("""
        SELECT orders.id, customers.username, products.name,
        order_details.quantity, (order_details.quantity * products.price) AS total_price
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_details ON orders.id = order_details.order_id
        JOIN products ON order_details.product_id = products.id
        ORDER BY orders.id DESC
    """)
    orders = cursor.fetchall()

    if not orders:
        print("⚠️ Hozircha buyurtmalar yo'q...")

    for order in orders:
        print(f"📦 Buyurtma ID: {order[0]} | 👤 {order[1]} | {order[2]} - {order[3]} dona | 💰 {order[4]} so'm")

def view_orders_by_cus():
    customer_name = input("👤 Mijoz ismini kiriting:")

    cursor.execute("""
        SELECT orders.id, products.name,order_details.quantity,
        (order_details.quantity * products.price) AS total_price
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_details ON orders.id = order_details.order_id
        JOIN products ON order_details.product_id = products.id
        WHERE customers.username = %s
    """, (customer_name,))

    orders = cursor.fetchall()

    if not orders:
        print(f"⚠️ {customer_name} bu mijozning buyurtmalari yo'q")
        return
    print(f"\n📜 {customer_name}ning buyurtmalari:")
    for order in orders:
        print(f"📦 Buyurtma ID: {order[0]} | {order[1]} - {order[2]} dona | 💰 {order[3]} so'm")

def view_cust():
    print("\n📜 Barcha mijozlar:")
    cursor.execute("""
        SELECT id, username, phone, email, balance FROM customers ORDER BY id
    """)
    customer=cursor.fetchall()

    if not customer:
        print("⚠️ Hozircha mijozlar yo'q...")
        return

    for c in customer:
        print(f"👤 ID: {c[0]} | {c[1]} | 📞 {c[2]} | 📧 {c[3]} | 💰 {c[4]} so'm")

def order_product(customer_id):
    print("\n🛒 Buyurtma berish......")

    cursor.execute("SELECT id, name, price, available_quantity FROM products")
    products = cursor.fetchall()

    if not products:
        print("⚠️ Hozircha tovarlar mavjud emas...")
        return

    print("\n📦 Mavjud tovarlar: ")
    for pro in products:
        print(f"{pro[0]} | {pro[1]} - 💰 {pro[2]} so'm | mavjud:{pro[3]} dona")

    pro_id = input("📌Tovar ID sini kiriting: ")
    quantity = input("📦 Miqdorini kiriting:")

    cursor.execute("SELECT price FROM products WHERE id = %s", (pro_id,))
    pro_price = cursor.fetchone()

    if not pro_price:
        print("❌ Noto‘g‘ri tovar ID!")
        return

    total_price = int(quantity) * pro_price[0]  # Jami narx

    cursor.execute("SELECT balance FROM customers WHERE id = %s", (customer_id,))
    cus_balance = cursor.fetchone()

    if not cus_balance:
        print("❌ Mijoz topilmadi!")
        return

    cus_balance = cus_balance[0]
    max_debt = -15_000_000

    new_balance = cus_balance - total_price

    if new_balance >= max_debt:
        cursor.execute("INSERT INTO orders (customer_id) VALUES (%s) RETURNING id", (customer_id,))
        order_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (order_id, pro_id, quantity))

        cursor.execute("UPDATE products SET available_quantity = available_quantity - %s WHERE id = %s", (quantity, pro_id))
        cursor.execute("UPDATE customers SET balance = %s WHERE id = %s", (new_balance, customer_id))
        conn.commit()
        print(f"✅ Buyurtma qabul qilindi! Jami: {total_price} so'm | Yangi balans: {new_balance} so‘m")
    else:
        print("❌ Xatolik: Hisobingiz juda katta minusda! Tovar sotib olish mumkin emas.")

def view_orders(customer_id):
    print("\n📜 Buyurtmalar tarixi-- ")
    cursor.execute("""
        SELECT orders.id, products.name, order_details.quantity,
        (order_details.quantity * products.price) AS total_price
        FROM orders
        JOIN order_details ON orders.id = order_details.order_id
        JOIN products ON order_details.product_id = products.id
        WHERE orders.customer_id = %s
    """, (customer_id,))

    orders = cursor.fetchall()

    if not orders:
        print("⚠️ Hozircha buyurtmalar yo'q...")
        return

    for order in orders:
        print(f"📦 Buyurtma ID: {order[0]} | {order[1]} - {order[2]} dona | 💰 {order[3]} so'm")

def view_balance(customer_id):
    cursor.execute("SELECT balance FROM customers WHERE id = %s",(customer_id,))
    balance = cursor.fetchone()

    if balance:
        print(f"💰 Sizning balansingiz: {balance[0]} so'm")
    else:
        print("⚠️ Balans topilmadi...")

def by_balance(customer_id):
    soqqa = float(input("💰 To'ldirmoqchi bo'lgan summani kiriting:"))

    if soqqa <= 0:
        print("⚠️ Xato! Summani to'g'ri kiriting.")
        return
    cursor.execute("UPDATE customers SET balance = balance + %s  WHERE id = %s", (soqqa,customer_id))
    conn.commit()

    print(f"✅ Hisobingiz {soqqa} so'mga to'ldirildi!")
    view_balance(customer_id)

def add_admin():
    secret_code="6772802"
    code=input("🔑 Maxfiy kodni kiriting:")
    if code != secret_code:
        print("⚠️ Noto'g'ri kod. Admin qo'shish mumkin emas!")
        return

    username = input("👤 Yangi admin ismini kiriting: ")
    password = input("🔑 Parolni kiriting: ")
    cursor.execute("INSERT INTO admin (name,password) VALUES (%s,%s)",(username,password))
    conn.commit()
    print(f"✅ Admin {username} qo'shildi!")

def check_admin():
    cursor.execute("SELECT COUNT(*) FROM admin")
    admin_count=cursor.fetchone()[0]

    if admin_count ==0:
        print("⚠️ Hali hech qanday admin mavjud emas!")
        confirm = input("🛑 Admin profilini qo‘shmoqchimisiz? (yes/no): ").strip().lower()

        if confirm == "yes":
            secret_code = "6772802"
            code_input = input("✅ Maxsus kodni kiriting: ")

            if code_input == secret_code:
                username = input("👤 Yangi admin ismini kiriting: ")
                password = input("🔑 Parolni kiriting: ")

                cursor.execute("INSERT INTO admin (name, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                print("✅ Admin muvaffaqiyatli qo‘shildi!")
            else:
                print("❌ Xato kod! Admin qo‘shilmadi.")
        else:
            print("❌ Admin qo‘shilmadi.")

    else:
        username = input("👤 Ism: ")
        password = input("🔑 Parol: ")
        cursor.execute("""
            SELECT * FROM admin
            WHERE name = %s AND password = %s
        """, (username,password))
        return cursor.fetchone()

create_table()

def customer_login():
    username = input("👤 Ism: ")
    password = input("🔑 Parol: ")

    cursor.execute("SELECT id FROM customers WHERE username = %s AND password = %s", (username,password))
    customer = cursor.fetchone()

    if customer:
        print(f"✅ Xush kelibsiz! {username}")
        customer_menu(customer[0])
    else:
        print("❌ Username yoki parol noto'g'ri...")

# 🔧 Admin menyusi
def admin_menu():
    while True:
        print("\n📌 ADMIN PANEL")
        print("1. Tur qo'shish ")
        print("2. Turlarni ko'rish ")
        print("3. Tovar qo‘shish ")
        print("4. Tovar o'chirish ")
        print("5. Tovarlarni ko‘rish ")
        print("6. Buyurtmalarni ko‘rish ")
        print("7. Mijoz buyurtmalarini ko‘rish ")
        print("8. Mijozlarni ko'rish ")
        print("9. Yangi admin qo'shish ")
        print("0. Chiqish")
        choice = input("Tanlang: ")
        if choice == "0":
            break
        elif choice == "1":
            add_category()
        elif choice == "2":
            show_category()
        elif choice == "3":
            add_product()
        elif choice == "4":
            remove_pro()
        elif choice == "5":
            show_product()
        elif choice == "6":
            view_all_orders()
        elif choice == "7":
            view_orders_by_cus()
        elif choice == "8":
            view_cust()
        elif choice == "9":
            add_admin()
        else:
            print("⚠️ Xato tanlov!")

# 🛒 Mijoz menyusi
def customer_menu(customer_id):

    while True:
        print("\n📌 MIJOZ PANELI")
        print("1. Tovarlarni ko‘rish")
        print("2. Buyurtma berish")
        print("3. Buyurtmalarimni ko'rish")
        print("4. Hisobimni ko‘rish")
        print("5. Hisobimni yangilash")
        print("0. Chiqish")
        choice = input("Tanlang: ")
        if choice == "0":
            break
        elif choice == "1":
            show_product()
        elif choice == "2":
            order_product(customer_id)
        elif choice == "3":
            view_orders(customer_id)
        elif choice == "4":
            view_balance(customer_id)
        elif choice == "5":
            by_balance(customer_id)
        else:
            print("⚠️ Xato tanlov!")



def main():
    while True:
        print("\n📌 Kirish turini tanlang:")
        print("1️⃣ Admin sifatida kirish")
        print("2️⃣ Mijoz sifatida kirish")
        print("3️⃣ Yangi mijoz qo‘shish")
        print("0️⃣ Dasturdan chiqish")

        choice = input("Tanlang (1/2/3/0): ")

        if choice == "0":
            print("🔚 Dasturdan chiqildi!")
            break

        elif choice == "3":
            add_customer()
            continue
        if choice == "1" and check_admin():
            admin_menu()
        elif choice == "2" :
            customer_login()
        else:
            print("❌ Noto‘g‘ri ma’lumot! Qayta urinib ko‘ring.")


main()



