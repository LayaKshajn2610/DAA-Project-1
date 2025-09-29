# Recipe Suggester (Minimal)

A minimal Flask project that suggests recipes based on available ingredients.
This repo includes a seeded SQLite database (`data/recipes.db`) with a few sample recipes
and substitutions.

## How to run

1. Create a virtualenv (optional):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open http://localhost:5000 in your browser.

## What is included

- `app.py` — Flask app
- `recipe_matching.py` — core matching logic
- `substitution.py` — substitution lookup
- `templates/index.html` — simple frontend
- `static/styles.css` — basic styling
- `data/recipes.db` — seeded SQLite DB

