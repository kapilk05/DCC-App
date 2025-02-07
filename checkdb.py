import sqlite3

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

print("📦 Inventory Table:")
cursor.execute("SELECT * FROM inventory")
for row in cursor.fetchall():
    print(row)

print("\n🔄 Transformations Table:")
cursor.execute("SELECT * FROM transformations")
for row in cursor.fetchall():
    print(row)

conn.close()
