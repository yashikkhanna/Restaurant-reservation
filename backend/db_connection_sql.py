import psycopg2
import json
import os

# Connect to your Postgres DB (update these values)
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432)
)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    rating REAL,
    rating_count INTEGER,
    cost INTEGER,
    lic_no TEXT,
    address TEXT,
    capacity INTEGER,
    description TEXT,
    opening_time TEXT,
    closing_time TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cuisines (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurant_cuisines (
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    cuisine_id INTEGER REFERENCES cuisines(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, cuisine_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS features (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS restaurant_features (
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES features(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, feature_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS slots (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    time TEXT,
    is_booked BOOLEAN DEFAULT FALSE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    user_name TEXT,
    contact_number TEXT,
    email TEXT,
    date DATE,
    slot TEXT
);
""")

conn.commit()

# Load data
with open('restaurants.json', 'r') as f:
    data = json.load(f)

def get_or_create_id(table, name):
    cursor.execute(f"SELECT id FROM {table} WHERE name=%s;", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} (name) VALUES (%s) RETURNING id;", (name,))
    new_id = cursor.fetchone()[0]
    conn.commit()
    return new_id

for restaurant in data:
    # Insert restaurant basic info
    cursor.execute("""
        INSERT INTO restaurants (
            id, name, city, rating, rating_count, cost, lic_no,
            address, capacity, description, opening_time, closing_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            city = EXCLUDED.city,
            rating = EXCLUDED.rating,
            rating_count = EXCLUDED.rating_count,
            cost = EXCLUDED.cost,
            lic_no = EXCLUDED.lic_no,
            address = EXCLUDED.address,
            capacity = EXCLUDED.capacity,
            description = EXCLUDED.description,
            opening_time = EXCLUDED.opening_time,
            closing_time = EXCLUDED.closing_time
        ;
    """, (
        restaurant["id"],
        restaurant["name"],
        restaurant["city"],
        restaurant.get("rating"),
        restaurant.get("rating_count"),
        restaurant.get("cost"),
        restaurant.get("lic_no"),
        restaurant.get("address"),
        restaurant.get("capacity"),
        restaurant.get("description"),
        restaurant.get("opening_time"),
        restaurant.get("closing_time"),
    ))

    # Insert cuisines and link to restaurant
    for cuisine_name in restaurant["cuisine"]:
        cuisine_id = get_or_create_id("cuisines", cuisine_name)
        cursor.execute("""
            INSERT INTO restaurant_cuisines (restaurant_id, cuisine_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING;
        """, (restaurant["id"], cuisine_id))

    # Insert features and link to restaurant
    for feature_name in restaurant.get("features", []):
        feature_id = get_or_create_id("features", feature_name)
        cursor.execute("""
            INSERT INTO restaurant_features (restaurant_id, feature_id)
            VALUES (%s, %s) ON CONFLICT DO NOTHING;
        """, (restaurant["id"], feature_id))

    # Insert slots
    for slot in restaurant.get("daily_slots", []):
        cursor.execute("""
            INSERT INTO slots (restaurant_id, time, is_booked)
            VALUES (%s, %s, FALSE)
            ON CONFLICT DO NOTHING;
        """, (restaurant["id"], slot))

conn.commit()
cursor.close()
conn.close()

print("Data ingested successfully into PostgreSQL!")
