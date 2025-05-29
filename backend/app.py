from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from db_querries import make_booking, cancel_booking_by_id, check_availability, search_bookings_by_user
from ai_agent import extract_intent_entities
from pinecone_search import query_pinecone
import re
import json

app = FastAPI()

# Allow CORS for frontend to call this API
origins = [
    "https://restaurant-reservation-775lvhp1a-yashik-khannas-projects.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_entities(json_str: str):
    if not json_str or json_str.strip() == "":
        return {}
    cleaned = re.sub(r"^```json\s*|```$", "", json_str.strip(), flags=re.DOTALL)
    try:
        return json.loads(cleaned)
    except Exception as e:
        print("Failed to parse extracted intent/entities JSON:", e)
        return {}


# Pydantic models

class IntentRequest(BaseModel):
    user_input: str

class IntentResponse(BaseModel):
    intent: Optional[str]
    entities: Optional[dict]

class RecommendationRequest(BaseModel):
    user_query: str
    city: Optional[str] = None
    cuisine: Optional[str] = None

class RecommendationItem(BaseModel):
    id: str
    name: Optional[str]
    city: Optional[str]
    cuisines: List[str] = []
    features: List[str] = []

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]

class AvailabilityRequest(BaseModel):
    restaurant_id: int
    date: date

class AvailabilityResponse(BaseModel):
    available_slots: List[str]

class BookingRequest(BaseModel):
    restaurant_id: int
    contact_name: str
    contact_number: str
    contact_email: EmailStr
    date: date
    slot: str
    number_of_people: Optional[int] = Field(1, gt=0)

class BookingResponse(BaseModel):
    success: bool
    message: str
    booking_id: Optional[str] = None

class CancelRequest(BaseModel):
    booking_id: str

class CancelResponse(BaseModel):
    success: bool
    message: str


class GetBookingsRequest(BaseModel):
    contact_number: str
    contact_email: EmailStr

class BookingItem(BaseModel):
    booking_id: str
    restaurant_id: int
    name: str
    date: date
    time_slot: str

class GetBookingsResponse(BaseModel):
    bookings: List[BookingItem]

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ Validation error details:", exc.errors())
    body = await request.body()
    print("➡️ Request body causing error:", body.decode())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
# Routes

@app.post("/intent", response_model=IntentResponse)
def get_intent(data: IntentRequest):
    raw_output = extract_intent_entities(data.user_input)
    intent_entities = parse_entities(raw_output)
    return intent_entities

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(data: RecommendationRequest):
    results = query_pinecone(data.user_query, city_filter=data.city, cuisine_filter=data.cuisine, top_k=3)
    recs = []
    for res in results or []:
        meta = res.get('metadata', {})
        recs.append(RecommendationItem(
            id=res.get("id"),
            name=meta.get("name"),
            city=meta.get("city"),
            cuisines=meta.get("cuisines", []),
            features=meta.get("features", [])
        ))
    return {"recommendations": recs}

@app.post("/availability", response_model=AvailabilityResponse)
def get_availability(data: AvailabilityRequest):
    slots = check_availability(data.restaurant_id, data.date)
    return {"available_slots": slots}

@app.post("/book", response_model=BookingResponse)
def book(data: BookingRequest):
    try:
        booking_id = make_booking(
            restaurant_id=data.restaurant_id,
            user_name=data.contact_name,
            contact_number=data.contact_number,
            email=data.contact_email,
            date=data.date,
            slot=data.slot
        )

        if booking_id:
            return BookingResponse(
                success=True,
                message="Booking confirmed!",
                booking_id=str(booking_id)
            )
        else:
            return BookingResponse(
                success=False,
                message="Booking failed: Slot already booked",
                booking_id=None
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel", response_model=CancelResponse)
def cancel(data: CancelRequest):
    success = cancel_booking_by_id(data.booking_id)
    if success:
        return CancelResponse(
            success=True,
            message="Booking cancelled successfully"
        )
    else:
        raise HTTPException(status_code=404, detail="Booking ID not found")

@app.post("/bookings", response_model=GetBookingsResponse)
def get_bookings(data: GetBookingsRequest):
    bookings = search_bookings_by_user(data.contact_number, data.contact_email)
    result = []
    for b in bookings:
        result.append(BookingItem(
            booking_id=str(b[0]),         # booking_id
            restaurant_id=b[1],           # restaurant_id
            name=b[2],                    # restaurant name from JOIN
            date=b[3],                    # date
            time_slot=b[4]                # slot
        ))
    return {"bookings": result}


# To run this API: uvicorn app:app --reload
