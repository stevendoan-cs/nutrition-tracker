from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from datetime import datetime, timezone, timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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