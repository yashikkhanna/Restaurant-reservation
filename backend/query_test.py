from datetime import date
from db_querries import (
    make_booking,
    cancel_booking_by_id,
    search_bookings_by_user,
    check_availability,
    close_connection
)

def run_tests():
    restaurant_id = 45
    slot = "7:30 PM"
    booking_date = date(2025, 6, 6)

    user_name = "Goa Tester"
    contact_number = "9876543210"
    email = "goa.tester@example.com"

    print("=== Test 1: Check Availability Before Booking ===")
    print(check_availability(restaurant_id, booking_date))

    print("\n=== Test 2: Make Booking ===")
    booking_id = make_booking(restaurant_id, user_name, contact_number, email, booking_date, slot)
    if booking_id:
        print(f"✅ Booking successful! Booking ID: {booking_id}")
    else:
        print("❌ Slot already booked or invalid.")

    print("\n=== Test 3: Search Bookings by User ===")
    bookings = search_bookings_by_user(contact_number, email)
    for b in bookings:
        print(f"📌 Booking: ID={b[0]}, Restaurant ID={b[1]}, Name={b[2]}, Date={b[3]}, Slot={b[4]}")

    print("\n=== Test 4: Check Availability After Booking ===")
    print(check_availability(restaurant_id, booking_date))

    if booking_id:
        print("\n=== Test 5: Cancel Booking ===")
        if cancel_booking_by_id(booking_id):
            print("✅ Booking cancelled.")
        else:
            print("❌ Cancel failed.")

        print("\n=== Test 6: Final Availability Check ===")
        print(check_availability(restaurant_id, booking_date))

    close_connection()

if __name__ == "__main__":
    run_tests()
