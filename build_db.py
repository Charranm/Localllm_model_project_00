import os, random, sqlite3
from datetime import date, timedelta

random.seed(42)
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/shop.db")
conn.executescript("""
DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;    DROP TABLE IF EXISTS customers;
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, country TEXT, signup_date TEXT);
CREATE TABLE products  (product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders    (order_id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(customer_id),
                        order_date TEXT, status TEXT);
CREATE TABLE order_items (item_id INTEGER PRIMARY KEY, order_id INTEGER REFERENCES orders(order_id),
                          product_id INTEGER REFERENCES products(product_id), quantity INTEGER);
""")

countries = ["UK", "India", "USA", "Germany", "France", "Canada"]
categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
start = date(2024, 1, 1)

for i in range(1, 201):
    conn.execute("INSERT INTO customers VALUES (?,?,?,?)",
                 (i, f"Customer {i}", random.choice(countries),
                  str(start + timedelta(days=random.randint(0, 300)))))
for i in range(1, 41):
    conn.execute("INSERT INTO products VALUES (?,?,?,?)",
                 (i, f"Product {i}", random.choice(categories), round(random.uniform(5, 500), 2)))
item_id = 1
for o in range(1, 2001):
    conn.execute("INSERT INTO orders VALUES (?,?,?,?)",
                 (o, random.randint(1, 200), str(start + timedelta(days=random.randint(0, 729))),
                  random.choice(["completed", "completed", "completed", "cancelled", "returned"])))
    for _ in range(random.randint(1, 4)):
        conn.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                     (item_id, o, random.randint(1, 40), random.randint(1, 5)))
        item_id += 1
conn.commit()
conn.close()
print("Created data/shop.db")