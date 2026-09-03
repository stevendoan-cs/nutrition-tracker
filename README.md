# \# AI Nutrition Tracker

# 

# A full-stack nutrition tracker with an AI twist: instead of manually picking foods from a list, you can just type what you ate ("2 eggs, toast, and a banana for breakfast") and it gets parsed into structured food entries automatically, with calories and macros tracked from there.

# 

# \*\*Live app:\*\* https://nutrition-tracker-azure-nine.vercel.app

# \*\*API docs:\*\* https://nutrition-tracker-api-ir8r.onrender.com/docs

# 

# > Heads up: the backend is on a free hosting tier and spins down after 15 minutes of inactivity. First request after it's been idle can take 30 to 60 seconds to wake back up.

# 

# \## Features

# 

# \- Add and manage foods with full nutrition info (calories, protein, carbs, fat)

# \- Log meals made up of multiple foods with quantities

# \- AI-assisted meal logging: describe a meal in plain English and it gets parsed into structured entries, auto-adding any foods it doesn't already know using AI-estimated nutrition

# \- AI-parsed meals are shown for review before anything actually gets saved, so nothing gets logged without a confirmation

# \- Daily and weekly nutrition stats

# \- Full CRUD on foods, with a conflict check so you can't delete a food that's still being used in a logged meal

# \- Deleting a meal cleans up everything tied to it automatically

# 

# \## Tech Stack

# 

# \*\*Backend:\*\* Python, FastAPI, SQLAlchemy, PostgreSQL (SQLite locally)

# \*\*Frontend:\*\* HTML, CSS, JavaScript (no framework)

# \*\*AI:\*\* Anthropic Claude API (Haiku 4.5) for meal parsing

# \*\*Deployment:\*\* Render (backend + Postgres), Vercel (frontend)

# 

# \## A Few Design Decisions Worth Explaining

# 

# \- Meals and foods are relational: a `Meal` has many `MealEntry` rows, each pointing at a `Food` and a quantity, instead of copying nutrition data into every meal. That way nutrition info only ever lives in one place.

# \- The AI never writes to the database directly. It just returns a proposed interpretation of what you typed, and you have to confirm it, going through the exact same `/meals` endpoint as manually logging a meal.

# \- Deleting a meal cascades and cleans up its entries, since they only exist because of that meal. Deleting a food that's still used somewhere gets blocked instead, since removing something from the food catalog shouldn't quietly wipe out real meal history.

# 

# \## Known Limitations

# 

# \- Matching food names (whether typed manually or created by the AI) is case-insensitive but exact, not fuzzy, so near-duplicates like "egg" vs "egg white" can happen. A real production version would want fuzzy matching or a proper food database like USDA FoodData Central.

# \- AI-estimated nutrition for unrecognized foods is just that, an estimate, not verified label data.

# \- No login system yet. This is single-user for now, with auth planned as a future addition.

# \- The free Postgres database expires 30 days after creation.

# 

