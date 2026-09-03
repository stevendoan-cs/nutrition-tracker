const API_BASE = "https://nutrition-tracker-api-ir8r.onrender.com";

let currentParsedItems = [];

function loadFoods() {
  fetch(API_BASE + "/foods")
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

  fetch(API_BASE + "/foods", {
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

    const mealData = { items: newItems };

  fetch(API_BASE + "/meals", {
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
  fetch(API_BASE + "/stats/today")
    .then(response => response.json())
    .then(data => {
      document.getElementById("stat-calories").textContent = data.calories;
      document.getElementById("stat-protein").textContent = data.protein;
      document.getElementById("stat-carbs").textContent = data.carbs;
      document.getElementById("stat-fat").textContent = data.fat;
    });
}

function parseMeal() {
  const text = document.getElementById("ai-text").value;

  fetch(API_BASE + "/parse-meal?text=" + encodeURIComponent(text), {
    method: "POST"
  })
    .then(response => response.json())
    .then(data => {
      currentParsedItems = data.items;

      const preview = document.getElementById("parsed-preview");
      preview.innerHTML = "";

      data.items.forEach(item => {
        const line = document.createElement("p");
        line.textContent = item.quantity + "x " + item.name;
        preview.appendChild(line);
      });

      document.getElementById("confirm-btn").style.display = "inline";
    });
}

function confirmMeal() {
  const mealData = {
    items: currentParsedItems.map(item => ({
      food_id: item.food_id,
      quantity: item.quantity
    }))
  };

  fetch(API_BASE + "/meals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mealData)
  })
    .then(response => response.json())
    .then(data => {
      console.log("meal logged", data);
      document.getElementById("parsed-preview").innerHTML = "";
      document.getElementById("confirm-btn").style.display = "none";
      document.getElementById("ai-text").value = "";
      loadStats();
    });
}
