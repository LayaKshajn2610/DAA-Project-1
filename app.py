import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
user_ingredients = []


def get_db_connection():
    conn = sqlite3.connect("recipes.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    global user_ingredients
    if request.method == 'POST':
        raw = request.form.get("ingredients", "")
        user_ingredients = [i.strip().lower() for i in raw.split(",") if i.strip()]
        return redirect(url_for('recipes'))
    return render_template("ingredients.html")


@app.route('/recipes')
def recipes():
    if not user_ingredients:
        return redirect(url_for('ingredients'))

    conn = get_db_connection()

    # Get all recipes with ingredients
    rows = conn.execute("""
        SELECT r.id, r.name, r.steps, GROUP_CONCAT(i.name) AS ingredients
        FROM recipes r
        JOIN ingredients i ON r.id = i.recipe_id
        GROUP BY r.id
    """).fetchall()

    conn.close()

    possible, missing = [], []

    for row in rows:
        rec_ing = row["ingredients"].split(",")
        rec_ing = [ing.strip().lower() for ing in rec_ing]
        missing_ing = [ing for ing in rec_ing if ing not in user_ingredients]

        recipe = {
            "name": row["name"],
            "steps": row["steps"].split("|"),
            "ingredients": rec_ing
        }

        if not missing_ing:
            possible.append(recipe)
        else:
            missing.append({**recipe, "missing": missing_ing})

    return render_template("recipes.html",
                           possible=possible,
                           missing=missing,
                           ingredients=user_ingredients)


if __name__ == "__main__":
    app.run(debug=True)
