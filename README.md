# AI Nutrition Tracker

A full-stack nutrition tracker with an AI twist: instead of manually picking foods from a list, you can just type what you ate ("2 eggs, toast, and a banana for breakfast") and it gets parsed into structured food entries automatically, with calories and macros tracked from there.

**Live app:** https://nutrition-tracker-azure-nine.vercel.app
**API docs:** https://nutrition-tracker-api-ir8r.onrender.com/docs

> Heads up: the backend is on a free hosting tier and spins down after 15 minutes of inactivity. The first request after it's been idle can take 30 to 60 seconds to wake back up.

## Features

- Add, view, and delete foods, each with full nutrition info (calories, protein, carbs, fat)
- Log meals made up of multiple foods and quantities, just by typing the food's name (no need to know internal ids)
- AI-assisted meal logging: describe a meal in plain English and it gets parsed into structured entries, automatically adding any foods it doesn't already recognize using AI-estimated nutrition
- AI-parsed meals are shown for review before anything actually gets saved, so nothing gets logged without confirmation
- Daily and weekly nutrition stats
- Look up stats and the full meal list for any specific past date
- Deleting a food that's currently used in a logged meal is blocked, so you can't accidentally corrupt your meal history
- Deleting a meal automatically cleans up everything logged under it

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL (SQLite for local dev)
**Frontend:** HTML, CSS, JavaScript (no framework)
**AI:** Anthropic Claude API (Haiku 4.5) for natural language meal parsing
**Deployment:** Render (backend and Postgres), Vercel (frontend)

## A Few Design Decisions Worth Explaining

- Meals and foods are relational. A `Meal` has many `MealEntry` rows, each pointing at a `Food` and a quantity, instead of copying nutrition data into every meal. That way nutrition info only ever lives in one place, and updating a food's info automatically reflects in every meal that references it.
- The AI never writes to the database directly. It returns a proposed interpretation of what you typed, and the user has to confirm it, going through the exact same `/meals` endpoint used for manually logging a meal.
- Deleting a meal cascades and cleans up its entries, since they only exist because of that meal. Deleting a food that's still used somewhere gets blocked instead of cascading, since removing something from the food catalog shouldn't quietly wipe out real meal history.
- Manual meal logging resolves food names to ids on the backend rather than requiring the user to know or look up an id, using the same "find or create" logic the AI parser relies on internally, just without the auto-create step (an unrecognized name here returns an error asking you to add the food first, since there's no AI involved to supply a nutrition estimate).

## Known Limitations

- Food name matching (both manual logging and AI-created foods) is case-insensitive but exact, not fuzzy, so near-duplicates like "egg" vs "egg white" can happen. A production version would use fuzzy matching or a proper food database like USDA FoodData Central.
- AI-estimated nutrition for unrecognized foods is an estimate, not verified label data.
- "Today" and daily/weekly stats are currently calculated using UTC time rather than the user's actual local time zone, so the day can shift by a few hours near midnight depending on where you are. A full fix would track the user's local time zone through the app; this was scoped out for now as a known tradeoff.
- No login system. This is a single-user app by design, with authentication planned as a future addition rather than built into this version.
- Editing an existing meal isn't supported. Deleting and re-logging covers the same need for now.
- The free-tier Postgres database expires 30 days after creation.
