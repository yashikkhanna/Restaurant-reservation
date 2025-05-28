
---

````markdown
# 🍽️ Restaurant Reservation Chatbot

An intelligent, conversational AI system for booking restaurant reservations in natural language. Built using **FastAPI**, **Gemini Pro (Google AI)** for intent extraction, **Pinecone** for RAG and semantic search, and a custom restaurant dataset covering Indian metro cities.

---

## 📌 Key Features

- 💬 **Conversational interface** with Google Gemini 1.5 Flash
- 🧠 Smart intent recognition & entity extraction:
  - Table bookings
  - Modifications & rescheduling
  - Cancellations
  - Restaurant recommendations & FAQs
- 🌆 City-aware filters (Delhi, Goa, Mumbai, Bangalore, Noida, Sonipat, Udaipur)
- 🧾 Real-time availability, overbooking prevention & slot management
- 🔍 **Semantic Search** (RAG) powered by **Pinecone** vector DB
- 🔁 Handles incomplete prompts with follow-up Q&A flow
- 🌐 Simple frontend for real-time chat via `index.html`

---

## 🛠️ Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| 💡 LLM       | Gemini 1.5 Flash (Google AI Studio API)    |
| 🧠 RAG       | Pinecone Vector DB for semantic retrieval  |
| 🔧 Backend   | FastAPI (Python)                          |
| 📊 Database  | PostgreSQL + JSON Dataset (Hybrid)        |
| 💻 Frontend  | HTML + JavaScript Chat UI                 |
| ☁️ Deployment| Render / Vercel Ready                     |

---

## 🗃️ Dataset Overview

Custom JSON Dataset for 100+ restaurants:
- 📍 **City**, 🏷️ **Cuisine**, ⭐ **Rating**, 💸 **Cost for 2**
- 🕒 **Opening hours**, 🗓️ **Daily time slots**
- 🧾 **License**, 📬 **Address**, 🔢 **Capacity**
- 📆 **Booking limits**, ✏️ **Live reservation records**
- 📌 Stored in both JSON and PostgreSQL formats

---

## 🧠 Conversational Flow

1. **User Says:**  
   `"Book a table for 3 in Delhi tomorrow at 8PM"`

2. **Gemini Extracts:**  
   ```json
   {
     "intent": "book",
     "entities": {
       "city": "Delhi",
       "persons": 3,
       "time": "8PM",
       "date": "2025-05-29"
     }
   }
````

3. **System Response:**

   * Finds available restaurants via Pinecone (semantic + filter-based)
   * Shows available slots
   * Books and confirms reservation with slot lock

4. **Fallback:**

   * If required fields are missing (e.g., city), bot prompts for them
   * Handles rescheduling/cancellation via booking ID

---

## 💼 Business Strategy

### 🔍 Problem

Manual or app-based reservation systems:

* Require structured input
* Lack true flexibility or personalization
* Often disconnected from real-time slot availability

### 🚀 Solution

A **fully conversational, intelligent booking assistant** using Gemini + Pinecone to:

* Understand vague, messy, or incomplete inputs
* Engage with users naturally
* Offer hyper-local, real-time reservation functionality

### 👤 Target Audience

| Segment           | Value                            |
| ----------------- | -------------------------------- |
| **Restaurants**   | Streamlined reservation system   |
| **Customers**     | 24/7 intelligent booking         |
| **Marketplaces**  | Add-on AI agent (Zomato, Swiggy) |
| **SaaS startups** | White-labeled booking AI         |

### 💰 Revenue Streams (Future)

* SaaS licensing to restaurants or chains
* Commission-based booking partnerships
* Freemium model (free chatbot, paid analytics)
* Premium AI Concierge service for luxury restaurants

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app.py             # FastAPI app and endpoints
│   ├── ai_agent.py          # Gemini intent + entity logic
│   ├── pinecone_search.py  # Semantic restaurant search
│   ├── db_querries.py    # Booking, slots, DB operations
│   └── restaurant.json           # Raw dataset (JSON format)
├── frontend/
│   └── index.html          # HTML/JS chatbot UI       
├── .env                    # API keys (Gemini, Pinecone)
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/yashikkhanna/Restaurant-reservation.git
cd Restaurant-reservation
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

### 4. Launch Backend

```bash
uvicorn app.main:app --reload
```

### 5. Open the Chatbot

Just open `static/index.html` in your browser.

---

## ✅ Sample Prompts & Intents

| Prompt                                   | Detected Intent      |
| ---------------------------------------- | -------------------- |
| "Find me a Chinese restaurant in Goa"    | Recommendation       |
| "Book for 5 at 9PM tonight in Bangalore" | Booking              |
| "Change my reservation to 7PM tomorrow"  | Modification         |
| "Cancel my booking ID 845691"            | Cancellation         |
| "What restaurants are open past 10?"     | Availability Inquiry |
| "Hi, I'm hungry!"                        | Greeting             |

---

## 🧪 Test Cases

| Scenario                       | Handled?    |
| ------------------------------ | ----------- |
| Booking with missing fields    | ✅ Prompted  |
| Booking already full           | ✅ Rejected  |
| Cancelling invalid booking ID  | ✅ 404 error |
| Changing city mid-conversation | ✅ Handled   |
| Booking at closed hours        | ✅ Blocked   |

---

## 📈 Future Improvements

* 🔐 User authentication for reservation history
* 📊 Admin panel for restaurant owners
* 🤖 WhatsApp & Telegram bot integration
* ✉️ Email & SMS confirmations (Twilio)
* 📦 Docker deployment for production

---

## 🙌 Acknowledgments

* [Gemini API – Google AI Studio](https://aistudio.google.com/)
* [Pinecone – Vector Search](https://www.pinecone.io/)
* [FastAPI – Modern Web Framework](https://fastapi.tiangolo.com/)
* Inspired by ChatGPT-style LLM UI

---

## 🧠 Built for the future of dining & dialogue.

```

---

Would you like this saved to a `README.md` file or pushed to your GitHub directly via script or PR instructions? Let me know!
```
