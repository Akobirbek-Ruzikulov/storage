import psycopg2

# PostgreSQL bilan bog'lanish
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="****",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Jadvallarni yaratish
def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tur (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS taom (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            tur_id INT REFERENCES tur(id) ON DELETE CASCADE,
            price DECIMAL(10,2) NOT NULL CHECK (price > 0),
            available_quantity INT NOT NULL CHECK (available_quantity >= 0)
        );

        CREATE TABLE IF NOT EXISTS mijoz (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            balance DECIMAL(10,2) NOT NULL CHECK (balance >= 0)
        );

        CREATE TABLE IF NOT EXISTS buyurtma (
            id SERIAL PRIMARY KEY,
            mijoz_id INT REFERENCES mijoz(id) ON DELETE CASCADE,
            taom_id INT REFERENCES taom(id) ON DELETE CASCADE,
            quantity INT NOT NULL CHECK (quantity > 0),
            total_price DECIMAL(10,2) NOT NULL CHECK (total_price >= 0)
        );
    """)
    conn.commit()


# Turlarni ko'rsatish
def show_turlar():
    cursor.execute("SELECT name FROM tur")
    turlar = cursor.fetchall()

    if not turlar:
        print("⚠️ Tur mavjud emas!")
        return False

    print("\n📂 Mavjud turlar:")
    for tur in turlar:
        print(f"- {tur[0]}")
    return True


# Tur qo'shish
def add_tur():
    name = input("Tur nomini kiriting: ").strip()
    if not name:
        print("⚠️ Tur nomi bo‘sh bo‘lishi mumkin emas!")
        return

    try:
        cursor.execute("INSERT INTO tur (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))
        conn.commit()
        print(f"✅ Tur '{name}' qo‘shildi!")
    except Exception as e:
        print(f"❌ Xatolik: {e}")


# Taom qo'shish
def add_taom():
    if not show_turlar():
        print("⚠️ Avval tur qo‘shing!")
        return

    name = input("\n🍽 Taom nomini kiriting: ").strip()
    tur = input("Tur nomini kiriting: ").strip()

    cursor.execute("SELECT id FROM tur WHERE name = %s", (tur,))
    tur_id = cursor.fetchone()

    if not tur_id:
        print("⚠️ Bunday tur topilmadi!")
        return

    try:
        price = float(input("💰 Narxini kiriting: "))
        available_quantity = int(input("📦 Mavjud sonini kiriting: "))

        if price <= 0 or available_quantity < 0:
            print("⚠️ Narx musbat bo‘lishi, son esa 0 yoki undan katta bo‘lishi kerak!")
            return

        cursor.execute(
            "INSERT INTO taom (name, tur_id, price, available_quantity) VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING",
            (name, tur_id[0], price, available_quantity)
        )
        conn.commit()
        print(f"✅ '{name}' taomi qo‘shildi!")
    except ValueError:
        print("⚠️ Narx va son raqam bo‘lishi kerak!")


# Mijoz qo'shish
def add_mijoz():
    username = input("👤 Mijoz nomini kiriting: ").strip()
    if not username:
        print("⚠️ Mijoz nomi bo‘sh bo‘lishi mumkin emas!")
        return

    try:
        balance = float(input("💰 Balansni kiriting: "))
        if balance < 0:
            print("⚠️ Balans manfiy bo‘lishi mumkin emas!")
            return

        cursor.execute("INSERT INTO mijoz (username, balance) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
                       (username, balance))
        conn.commit()
        print(f"✅ Mijoz '{username}' qo‘shildi!")
    except ValueError:
        print("⚠️ Balans raqam bo‘lishi kerak!")


# Barcha taomlarni ko'rsatish
def show_taomlar():
    cursor.execute("SELECT name, available_quantity FROM taom")
    taomlar = cursor.fetchall()

    if not taomlar:
        print("⚠️ Taomlar mavjud emas!")
        return False

    print("\n🍽 Mavjud taomlar:")
    for taom in taomlar:
        print(f"- {taom[0]} (mavjud: {taom[1]} dona)")

    return True


# Buyurtma berish
def make_buyurtma():
    if not show_taomlar():
        print("⚠️ Avval taom qo‘shing!")
        return

    mijoz_name = input("\n👤 Mijoz nomini kiriting: ").strip()
    taom_name = input("🍽 Taom nomini kiriting: ").strip()

    cursor.execute("SELECT id, balance FROM mijoz WHERE username = %s", (mijoz_name,))
    mijoz = cursor.fetchone()

    if not mijoz:
        print("⚠️ Bunday mijoz topilmadi!")
        return

    mijoz_id, mijoz_balance = mijoz

    cursor.execute("SELECT id, price, available_quantity FROM taom WHERE name = %s", (taom_name,))
    taom = cursor.fetchone()

    if not taom:
        print("⚠️ Bunday taom mavjud emas!")
        return

    taom_id, price, available_quantity = taom

    try:
        quantity = int(input("📦 Nechta buyurtma qilmoqchisiz? "))
        if quantity <= 0:
            print("⚠️ Buyurtma soni 0 dan katta bo‘lishi kerak!")
            return
    except ValueError:
        print("⚠️ Buyurtma soni raqam bo‘lishi kerak!")
        return

    if available_quantity < quantity:
        print("⚠️ Yetarli taom yo‘q!")
        return

    total_price = price * quantity

    if mijoz_balance < total_price:
        print("⚠️ Yetarli balans yo‘q!")
        return

    cursor.execute(
        "INSERT INTO buyurtma (mijoz_id, taom_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
        (mijoz_id, taom_id, quantity, total_price)
    )

    cursor.execute("UPDATE taom SET available_quantity = available_quantity - %s WHERE id = %s", (quantity, taom_id))
    cursor.execute("UPDATE mijoz SET balance = balance - %s WHERE id = %s", (total_price, mijoz_id))

    conn.commit()
    print(f"✅ Buyurtma qabul qilindi! Umumiy summa: {total_price} so‘m")


# Buyurtmalar tarixini ko‘rsatish
def show_buyurtmalar():
    cursor.execute("""
        SELECT mijoz.username, taom.name, buyurtma.quantity, buyurtma.total_price
        FROM buyurtma
        JOIN mijoz ON buyurtma.mijoz_id = mijoz.id
        JOIN taom ON buyurtma.taom_id = taom.id
    """)
    buyurtmalar = cursor.fetchall()

    if not buyurtmalar:
        print("⚠️ Buyurtmalar mavjud emas!")
        return

    print("\n📜 Buyurtmalar tarixi:")
    for buyurtma in buyurtmalar:
        print(f"{buyurtma[0]} | {buyurtma[1]} | {buyurtma[2]} dona | {buyurtma[3]} so'm")
def show_users():
    cursor.execute("SELECT id,username, balance FROM mijoz")
    users=cursor.fetchall()
    for u in users:
        print(f"{u[0]}| {u[1]} | {u[2]} so'm|")




# Jadvallarni yaratish
create_tables()

# Asosiy menyu va tanlovlar
while True:
    print("\n\n==== Menu ====")
    print("1. Tur qo‘shish")
    print("2. Taom qo‘shish")
    print("3. Mijoz qo‘shish")
    print("4. Taomlar ro‘yxatini ko‘rish")
    print("5. Buyurtma berish")
    print("6. Buyurtmalar tarixini ko‘rish")
    print("7. mijolar ro‘yxatini ko‘rish")
    print("8. Chiqish")

    choice = input("\nTanlovni kiriting (1-8): ").strip()

    if choice == "1":
        add_tur()
    elif choice == "2":
        add_taom()
    elif choice == "3":
        add_mijoz()
    elif choice == "4":
        show_taomlar()
    elif choice == "5":
        make_buyurtma()
    elif choice == "6":
        show_buyurtmalar()
    elif choice == "7":
        show_users()
    elif choice == "8":
        print("👋 Dasturdan chiqyapsiz...")
        break
