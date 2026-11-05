from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, EmailStr
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory=".")


events = [
    {
        "id": 1,
        "title": "Концерт",
        "date": "15.12.2026",
        "place": "Москва",
        "seats": 50
    },
    {
        "id": 2,
        "title": "IT-конференция",
        "date": "20.12.2026",
        "place": "Санкт-Петербург",
        "seats": 30
    },
    {
        "id": 3,
        "title": "Выставка",
        "date": "25.12.2026",
        "place": "Казань",
        "seats": 20
    }
]

bookings = []

class User(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="The username of the user")
    email: EmailStr 
    password: str = Field(min_length=8, max_length=100, description="The password of the user")


class Event(BaseModel):
    title: str = Field(min_length=1)
    date: str 
    place: str
    seats: int = Field(gt=0)


class Booking(BaseModel):
    event_id: int = Field(gt=0)
    username: str = Field(min_length=4, max_length=50, description='ur username')
    email: EmailStr
    tickets: int = Field(gt=0)

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,      
        name="index.html",
        context={"request": request}
    )


@app.get('/events')
async def get_events():
    return events

@app.get('/events/{event_id}')
async def get_event(event_id:int):
    for event in events:
        if event['id'] == event_id:
            return event
    raise HTTPException(
        status_code=404,
        detail='Мероприятие не найдено'
    )   

@app.post('/events')
async def create_event(event: Event):
    new_id = len(events) + 1 
    new_event = event.model_dump()
    new_event["id"] = new_id
    events.append(new_event)
    return new_event


@app.post('/bookings')
async def create_booking(booking: Booking):
    event = None

    for item in events:
        if item["id"] == booking.event_id:
            event = item
            break
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Мероприятие не найдено"
        )

    if event["seats"] < booking.tickets:
        raise HTTPException(
            status_code=400,
            detail="Недостаточно свободных мест"
        )
    new_id = len(bookings) + 1

    new_booking = booking.model_dump()
    new_booking["id"] = new_id

    bookings.append(new_booking)
    event["seats"] -= booking.tickets

    return new_booking

@app.get('/bookings')
async def get_bookings():
    return bookings

@app.delete('/bookings/{booking_id}')
async def delete_booking(booking_id:int):
    for booking in bookings:
        if booking['id'] == booking_id:
            for event in events:
                if event['id'] == booking['event_id']:
                    event['seats'] += booking['tickets']
                    break 
            bookings.remove(booking)
            return {
                'message': 'Бронирование отменено йоу',
                'booking': booking
            }
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)