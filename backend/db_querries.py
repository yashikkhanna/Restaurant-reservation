import psycopg2
import os
# Database connection setup
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432)
)

cursor = conn.cursor()

def make_booking(restaurant_id, user_name, contact_number, email, date, slot):
    """
    Inserts a booking into the bookings table. Returns the booking_id if successful.
    """
    # Check if slot is already booked for this date
    cursor.execute("""
        SELECT 1 FROM bookings
        WHERE restaurant_id = %s AND date = %s AND slot = %s;
    """, (restaurant_id, date, slot))

    if cursor.fetchone():
        return None  # Slot already booked

    cursor.execute("""
        INSERT INTO bookings (
            restaurant_id, user_name, contact_number, email, date, slot
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING booking_id;
    """, (restaurant_id, user_name, contact_number, email, date, slot))

    booking_id = cursor.fetchone()[0]
    conn.commit()
    return booking_id

def cancel_booking_by_id(booking_id):
    """
    Cancels a booking using the booking ID. Returns True if a booking was deleted.
    """
    cursor.execute("""
        DELETE FROM bookings
        WHERE booking_id = %s;
    """, (booking_id,))

    deleted = cursor.rowcount
    conn.commit()
    return deleted > 0

def search_bookings_by_user(contact_number, email):
    """
    Retrieves all bookings for a given user, including the restaurant name.
    """
    cursor.execute("""
        SELECT b.booking_id, b.restaurant_id, r.name, b.date, b.slot
        FROM bookings b
        JOIN restaurants r ON b.restaurant_id = r.id
        WHERE b.contact_number = %s AND b.email = %s;
    """, (contact_number, email))

    return cursor.fetchall()

def check_availability(restaurant_id, date):
    """
    Returns a list of available slots for a restaurant on a specific date.
    """
    cursor.execute("SELECT time FROM slots WHERE restaurant_id = %s;", (restaurant_id,))
    all_slots = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT slot FROM bookings
        WHERE restaurant_id = %s AND date = %s;
    """, (restaurant_id, date))
    booked_slots = [row[0] for row in cursor.fetchall()]

    available_slots = list(set(all_slots) - set(booked_slots))
    return sorted(available_slots)

def close_connection():
    cursor.close()
    conn.close()
