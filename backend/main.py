from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from datetime import datetime, timezone, timedelta
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/foods", response_model=list[schemas.FoodOut])
def get_foods(db: Session = Depends(get_db)):
    foods = db.query(models.Food).all()
    return foods

@app.post("/foods", response_model=schemas.FoodOut)
def food_create(food: schemas.FoodCreate, db: Session = Depends(get_db)):
    new_food = models.Food(
        name = food.name,
        calories = food.calories,
        protein = food.protein,
        carbs = food.carbs,
        fat = food.fat,
    )
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food

@app.post("/meals", response_model=schemas.MealOut)
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    new_meal = models.Meal(
        meal_type = meal.meal_type
    )
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    for item in meal.items:
        new_entry = models.MealEntry(
            meal_id = new_meal.id,
            food_id = item.food_id,
            quantity = item.quantity
        )
        db.add(new_entry)
    db.commit()

    return new_meal

@app.get("/meal-entries", response_model=list[schemas.MealEntryOut])
def get_meal_entries(db: Session = Depends(get_db)):
    meals = db.query(models.MealEntry).all()
    return meals

@app.get("/meals/{meal_id}", response_model=schemas.MealOut)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal

def calculate_nutrition_totals(start_date, db: Session):
    meals = db.query(models.Meal).filter(models.Meal.date >= start_date).all()
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    for meal in meals:
        for entry in meal.entries:
            total_calories += entry.quantity * entry.food.calories
            total_protein += entry.quantity * entry.food.protein
            total_carbs += entry.quantity * entry.food.carbs
            total_fat += entry.quantity * entry.food.fat
    return {
        "calories": total_calories,
        "protein": total_protein,
        "carbs": total_carbs,
        "fat": total_fat,
    }

@app.get("/stats/today")
def get_today_stats(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    return calculate_nutrition_totals(today, db)

@app.get("/stats/week")
def get_week_stats(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    last_week = today - timedelta(weeks=1)
    return calculate_nutrition_totals(last_week, db)

@app.delete("/foods/{food_id}")
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(models.Food).filter(models.Food.id == food_id).first()
    if food is None:
        raise HTTPException(status_code=404, detail="Food not found")
    
    existing_entry = db.query(models.MealEntry).filter(models.MealEntry.food_id == food_id).first()
    if existing_entry is not None:
        raise HTTPException(status_code=409, detail="Meals have these foods in it, Delete them first to delete this food")

    db.delete(food)
    db.commit()
    return {"message": "Food Deleted"}

@app.delete("/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")


    db.delete(meal)
    db.commit()
    return {"message": "Meal Deleted"}


@app.put("/foods/{food_id}", response_model=schemas.FoodOut)
def update_food(food_id: int, updated_food: schemas.FoodCreate, db: Session = Depends(get_db)):
    food = db.query(models.Food).filter(models.Food.id == food_id).first()

    if food is None:
        raise HTTPException(status_code=404, detail="Food not found")

    food.name = updated_food.name
    food.calories = updated_food.calories
    food.protein = updated_food.protein
    food.carbs = updated_food.carbs
    food.fat = updated_food.fat
    
    db.commit()
    db.refresh(food)

    return food


def find_or_create_food(name: str, calories: float, protein: float, carbs: float, fat: float, db: Session):
    existing = db.query(models.Food).filter(models.Food.name.ilike(name)).first()
    if existing is not None:
        return existing.id

    new_food = models.Food(
        name = name,
        calories = calories,
        protein = protein,
        carbs = carbs,
        fat = fat
    )
    db.add(new_food)
    db.commit()
    db.refresh(new_food)

    return new_food.id


@app.post("/parse-meal")
def parse_meal(text: str, db: Session = Depends(get_db)):
    prompt = f"""Extract each food item from this meal description. For each food, provide your best estimate of its nutrition per serving. Use simple, singular, lowercase food names (e.g. "egg" not "Eggs" or "eggs").

Meal description: "{text}"

Respond with ONLY valid JSON, no other text, in exactly this format:
[
  {{"name": "food name", "calories": 100, "protein": 10, "carbs": 20, "fat": 5, "quantity": 1}}
]
"""
    response = ai_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.split("```")[1]
        if cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
        cleaned_text = cleaned_text.strip()

    parsed_data = json.loads(cleaned_text)

    items = []
    for item in parsed_data:
        food_id = find_or_create_food(
            name=item["name"],
            calories=item["calories"],
            protein=item["protein"],
            carbs=item["carbs"],
            fat=item["fat"],
            db=db,
        )
        items.append({
    "food_id": food_id,
    "quantity": item["quantity"],
    "name": item["name"],
})

    return {"items": items}