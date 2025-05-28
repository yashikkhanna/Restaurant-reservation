import json
import datetime
from db_querries import make_booking, cancel_booking_by_id, check_availability, search_bookings_by_user
from ai_agent import extract_intent_entities
from pinecone_search import query_pinecone
import re

def parse_entities(json_str):
    if not json_str or json_str.strip() == "":
        print("No intent/entities extracted from AI agent.")
        return {}

    # Clean up triple backticks and "json" markdown
    cleaned = re.sub(r"^```json\s*|```$", "", json_str.strip(), flags=re.DOTALL)

    try:
        return json.loads(cleaned)
    except Exception as e:
        print("Failed to parse extracted intent/entities JSON:", e)
        return {}

def ask_for_missing(field, prompt, validate_func=None):
    while True:
        val = input(prompt).strip()
        if not val:
            continue
        if validate_func:
            valid, msg = validate_func(val)
            if not valid:
                print(msg)
                continue
        return val

def prompt_for_fields(entities, fields_with_validators):
    # Prompt only for given fields if missing, with validation if any
    for field, (prompt, validator) in fields_with_validators.items():
        if not entities.get(field):
            entities[field] = ask_for_missing(field, prompt, validator)
    return entities

def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "❌ Invalid date format. Please enter date as YYYY-MM-DD."

def validate_number(val):
    if val.isdigit() and int(val) > 0:
        return True, ""
    return False, "❌ Please enter a valid positive number."

def validate_email(email):
    # Simple email validation
    if "@" in email and "." in email:
        return True, ""
    return False, "❌ Please enter a valid email address."

def display_recommendations(user_query, city=None, cuisine=None):
    print("\n🔍 Searching for restaurants matching your preferences...")
    results = query_pinecone(user_query, city_filter=city, cuisine_filter=cuisine, top_k=3)
    if results:
        for idx, res in enumerate(results, 1):
            meta = res['metadata']
            print(f"{idx}. {meta.get('name', 'N/A')} (ID: {res['id']}) - {meta.get('city', 'N/A')}")
            print(f"   Cuisine(s): {', '.join(meta.get('cuisines', []))}")
            print(f"   Features: {', '.join(meta.get('features', []))}\n")
    else:
        print("No matching restaurants found.")
    print("\nUse the above names or IDs to specify restaurant for booking.")

def main():
    print("🤖 Welcome to the Restaurant Reservation Chatbot!")
    print("Type 'exit' or 'quit' anytime to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye! Have a great day.")
            break

        raw_output = extract_intent_entities(user_input)
        intent_entities = parse_entities(raw_output)
        intent = intent_entities.get("intent")
        entities = intent_entities.get("entities", {})
        if isinstance(entities, str):
            try:
                entities = json.loads(entities)
            except Exception:
                entities = {}

        if intent == "greeting":
            print("🤖 Hello! How can I assist you with your restaurant booking today?")
            continue

        if intent == "booking":
            # Prompt for cuisine if missing
            if not entities.get("cuisine"):
                entities["cuisine"] = ask_for_missing("cuisine", "Please enter cuisine preference: ")

            # Prompt for city if missing
            if not entities.get("city"):
                entities["city"] = ask_for_missing("city", "Please enter the city: ")

            city = entities.get("city")
            cuisine = entities.get("cuisine")

            # Show recommendations
            display_recommendations(user_input, city, cuisine)

            # Prompt for restaurant_name if missing
            if not entities.get("restaurant_name"):
                entities["restaurant_name"] = ask_for_missing("restaurant_name", "Please specify restaurant name or ID: ")

            # Prompt for date with validation
            while True:
                if not entities.get("date"):
                    entities["date"] = ask_for_missing("date", "Please enter the reservation date (YYYY-MM-DD): ")
                valid, msg = validate_date(entities["date"])
                if valid:
                    break
                print(msg)
                entities["date"] = None

            booking_date = datetime.datetime.strptime(entities["date"], "%Y-%m-%d").date()
            restaurant_id = entities["restaurant_name"]

            available_slots = check_availability(restaurant_id, booking_date)
            if not available_slots:
                print("❌ No slots available for the selected date.")
                continue

            print("\n🕒 Available Slots:")
            for i, slot in enumerate(available_slots, 1):
                print(f"{i}. {slot}")

            # Prompt for remaining fields with validation
            other_fields = {
                "time": ("Please enter the time (e.g., 19:00 or 7 PM): ", None),
                "number_of_people": ("Number of people: ", validate_number),
                "contact_name": ("Your full name: ", None),
                "contact_email": ("Your email: ", validate_email),
                "contact_number": ("Your contact number: ", None),
            }
            entities = prompt_for_fields(entities, other_fields)

            # Let user pick a slot from available slots
            while True:
                slot_choice = input("Choose a slot number: ").strip()
                if slot_choice.isdigit() and 1 <= int(slot_choice) <= len(available_slots):
                    slot = available_slots[int(slot_choice) - 1]
                    break
                else:
                    print("Invalid choice, please select a valid slot number.")

            booking_id = make_booking(
                restaurant_id=restaurant_id,
                user_name=entities["contact_name"],
                contact_number=entities["contact_number"],
                email=entities["contact_email"],
                date=booking_date,
                slot=slot
            )
            if booking_id:
                print(f"\n✅ Booking confirmed! Your booking ID is: {booking_id}")
            else:
                print("❌ Sorry, the selected slot is already booked or there was an error.")

        elif intent == "cancel":
            # Always ask for contact info first to find user bookings
            contact_name = ask_for_missing("contact_name", "Please enter your full name: ")
            contact_email = ask_for_missing("contact_email", "Please enter your email: ", validate_email)
            contact_number = ask_for_missing("contact_number", "Please enter your contact number: ")

            # Search bookings for this user
            user_bookings = search_bookings_by_user(contact_number, contact_email)
            if not user_bookings:
                print("❌ No bookings found for the provided details.")
                continue

            # Display all bookings for user
            print("\nHere are your bookings:")
            for b in user_bookings:
                print(f"Booking ID: {b[0]}")
                print(f"  Restaurant ID: {b[1]}")
                print(f"  Name: {b[2]}")
                print(f"  Date: {b[3]}")
                print(f"  Time Slot: {b[4]}\n")

            # Ask for booking ID to cancel
            booking_id = ask_for_missing("booking_id", "Please enter the Booking ID you want to cancel: ")

            success = cancel_booking_by_id(booking_id)
            if success:
                print("✅ Booking cancelled successfully.")
            else:
                print("❌ No booking found with that ID.")

        else:
            print("🤖 Sorry, I didn't understand that. Could you please rephrase or say if you want to 'book' or 'cancel'?")

if __name__ == "__main__":
    main()
