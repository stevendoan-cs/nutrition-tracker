from fastapi import FastAPI

app = FastAPI()

@app.get("/foods")
def get_foods():
    return [
        {"name": "banana", "calories": 105, "protein": 1.3},
        {"name": "chicken breast", "calories": 165, "protein": 31},
        {"name": "egg", "calories": 78, "protein": 6},
    ]