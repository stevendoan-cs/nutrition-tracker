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