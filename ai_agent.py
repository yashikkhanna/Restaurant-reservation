import os
from dotenv import load_dotenv
from google.generativeai import GenerativeModel, configure
from datetime import datetime
import json

# Load environment variables from .env
load_dotenv()

# Configure Gemini with your API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API Key not found in environment variables!")

configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model
intent_model = GenerativeModel("gemini-1.5-flash")

def get_today_date():
    return datetime.today().strftime('%Y-%m-%d')

def extract_intent_entities(user_input):
    prompt = f"""
You are a smart assistant that extracts structured booking-related information from user messages.

Extract the following:
- intent: One of [greeting, booking, cancel, other]
- entities (always include these fields, use null if not mentioned):
    - city (e.g., Delhi, Mumbai)
    - cuisine (e.g., North Indian, Italian)
    - features (e.g., romantic dinner, rooftop, outdoor seating) — return as a list, only if explicitly mentioned
    - date (parse expressions like "tomorrow", "next Friday" into YYYY-MM-DD format, assuming today's date is {get_today_date()})
    - time (e.g., 7 PM, 19:00)
    - number_of_people (e.g., 2, 4 people, couple, group of 5)
    - restaurant_name (if a specific one is mentioned)
    - contact_name (full name of the user, e.g., John Doe)
    - contact_email (email address, e.g., john@example.com)
    - contact_number (phone number, e.g., +91 9876543210 or 9876543210)

Rules:
- Use YYYY-MM-DD format for the date field.
- Convert relative dates like "tomorrow", "this weekend", etc. using today's date as reference: {get_today_date()}.
- Features should only include phrases explicitly mentioned in the user input. Do NOT add features that are not mentioned.
- Ensure "romantic dinner" or similar phrases go into features (as a list), only if present in the input.
- If features are multiple, return them as a list.
- If something is missing, return null for that field.
- Output must be a valid JSON object only. No preamble or explanation.
- in number_of_people only give the integer value dont add anything extra like 5 person 3 people or any other return only integer value like 5 , 6 , 10 etc

User input:
\"\"\"{user_input}\"\"\"
"""
    try:
        response = intent_model.generate_content(prompt)
        text = response.text.strip()
        # If output is empty or looks like an error, return '{}'
        if not text or text.lower().startswith("error:"):
            return '{}'
        # Optional: Validate JSON here or just return string
        # We'll parse in main code anyway
        return text
    except Exception as e:
        # Log the error if you want
        return '{}'



# Example usage
# if __name__ == "__main__":
#     while True:
#         user_input = input("\nUser: ")
#         if user_input.lower() in {"exit", "quit"}:
#             break
#         extracted = extract_intent_entities(user_input)
#         print("\nExtracted Info:\n", extracted)
