function loadFoods() {
  fetch("http://127.0.0.1:8000/foods")
    .then(response => response.json())
    .then(data => {
      const foodList = document.getElementById("food-list");
      data.forEach(food => {
        const listItem = document.createElement("li");
        listItem.textContent = food.name + " - " + food.calories + " calories " + food.protein + " protein";
        foodList.appendChild(listItem);
      });
    });
}

function addFood() {
  const newFood = {
    name: document.getElementById("input-name").value.trim(),
    calories: Number(document.getElementById("input-calories").value),
    protein: Number(document.getElementById("input-protein").value),
    carbs: Number(document.getElementById("input-carbs").value),
    fat: Number(document.getElementById("input-fat").value)
  };

  fetch("http://127.0.0.1:8000/foods", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newFood)
  })
  .then(response => {
    console.log("food added");
    loadFoods();
  });
}

function logMeal() {
    const mealType = document.getElementById("meal-type").value;
    const newItems = [];

    for (i = 1; i < 4; i++){
        const foodIdValue = document.getElementById("item-food-id-" + i).value;
        if (foodIdValue !== "") {
            const newMealEntry = {
                food_id: Number(document.getElementById("item-food-id-" + i).value),
                quantity: Number(document.getElementById("item-quantity-" + i).value)
            }
            newItems.push(newMealEntry);
        }
    }

    const mealData = {
        meal_type: mealType,
        items: newItems
    };

  fetch("http://127.0.0.1:8000/meals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mealData)
  })
  .then(response => {
    console.log("meal added");
    loadStats();
  });
}

function loadStats() {
  fetch("http://127.0.0.1:8000/stats/today")
    .then(response => response.json())
    .then(data => {
      document.getElementById("stat-calories").textContent = data.calories;
      document.getElementById("stat-protein").textContent = data.protein;
      document.getElementById("stat-carbs").textContent = data.carbs;
      document.getElementById("stat-fat").textContent = data.fat;
    });
}

loadFoods();
loadStats();