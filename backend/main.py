from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

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


@app.post("/meals")
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    # 1. create and save the Meal (add, commit, refresh)
    new_meal = models.Meal(
        meal_type = meal.meal_type
    )

    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    
    # 2. loop through meal.items, create a MealEntry for each, add() each (don't commit yet)
    for item in meal.items:
        new_entry = models.MealEntry(
            meal_id = new_meal.id,
            food_id = item.food_id,
            quantity = item.quantity
        )
        db.add(new_entry)
    
    # 3. commit once, after the loop
    db.commit()
    
    # 4. return something
    return new_meal


@app.get("/meal-entries")
def get_meal_entries(db: Session = Depends(get_db)):
    meals = db.query(models.MealEntry).all()
    return meals