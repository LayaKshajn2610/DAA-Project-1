import sqlite3

# Connect / create database file
conn = sqlite3.connect("recipes.db")
c = conn.cursor()

# Drop old tables if re-running
c.execute("DROP TABLE IF EXISTS recipes;")
c.execute("DROP TABLE IF EXISTS ingredients;")

# Create tables
c.execute("""
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    steps TEXT
)
""")

c.execute("""
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    name TEXT NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
)
""")

# Example data
recipes = [
    ("Pasta with Tomato Sauce", "Boil pasta|Make tomato sauce|Mix and serve"),
    ("Veggie Stir Fry", "Chop vegetables|Stir fry with soy sauce|Serve hot"),
    ("Garlic Butter Rice", "Cook rice|Fry garlic in butter|Mix and serve"),
]

ingredients = [
    (1, "pasta"), (1, "tomato"), (1, "garlic"),
    (2, "broccoli"), (2, "carrot"), (2, "soy sauce"),
    (3, "rice"), (3, "garlic"), (3, "butter"),
]

# Insert data
c.executemany("INSERT INTO recipes (name, steps) VALUES (?, ?)", recipes)
c.executemany("INSERT INTO ingredients (recipe_id, name) VALUES (?, ?)", ingredients)

# Save and close
conn.commit()
conn.close()

print("✅ recipes.db created with sample data")
