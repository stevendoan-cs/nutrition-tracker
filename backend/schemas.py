from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FoodCreate(BaseModel):
    # fields a client sends when creating a food
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class FoodOut(BaseModel):
    # fields returned to the client when reading a food
    id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

    class Config:
        from_attributes = True

class MealEntryCreate(BaseModel):
    food_id: int
    quantity: float
    

class MealCreate(BaseModel):
    meal_type: Optional[str] = None
    items: list[MealEntryCreate]
    
class MealEntryOut(BaseModel):
    food_id: int
    quantity: float
    food: FoodOut

    class Config:
        from_attributes = True


class MealOut(BaseModel):
    id: int
    meal_type: str
    date: datetime
    entries: list[MealEntryOut]

    class Config:
        from_attributes = True