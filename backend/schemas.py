from pydantic import BaseModel
from datetime import datetime

class FoodCreate(BaseModel):
    # fields a client sends when creating a food
    # think: which fields should NOT be here that are in your Food model?
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class FoodOut(BaseModel):
    # fields returned to the client when reading a food
    # this one probably includes everything, including id
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
    meal_type: str
    items: list[MealEntryCreate]
    
