# seed_db.py
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'recipes.db')

print("Seeding DB at:", DB_PATH)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS substitutions;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS ingredients;

CREATE TABLE IF NOT EXISTS ingredients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  category TEXT,
  unit TEXT
);
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  cuisine TEXT,
  servings INTEGER DEFAULT 1,
  instructions TEXT
);
CREATE TABLE IF NOT EXISTS recipe_ingredients (
  recipe_id INTEGER,
  ingredient_id INTEGER,
  qty REAL,
  unit TEXT,
  optional INTEGER DEFAULT 0,
  PRIMARY KEY (recipe_id, ingredient_id),
  FOREIGN KEY (recipe_id) REFERENCES recipes(id),
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);
CREATE TABLE IF NOT EXISTS substitutions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ingredient_id INTEGER NOT NULL,
  substitute_id INTEGER NOT NULL,
  score REAL DEFAULT 0.5,
  notes TEXT,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
  FOREIGN KEY (substitute_id) REFERENCES ingredients(id)
);
""")

# Insert ingredients (expandable)
ingredients = [
    # common
    ('flour', 'baking', 'g'),
    ('maida', 'baking', 'g'),
    ('wheat flour', 'grain', 'g'),
    ('rice', 'grain', 'g'),
    ('basmati rice', 'grain', 'g'),
    ('poha', 'grain', 'g'),
    ('rava', 'grain', 'g'),
    ('semolina', 'grain', 'g'),
    ('sugar', 'sweetener', 'g'),
    ('salt', 'spice', 'g'),
    ('turmeric', 'spice', 'g'),
    ('red chili', 'spice', 'g'),
    ('green chili', 'spice', 'pcs'),
    ('garlic', 'vegetable', 'cloves'),
    ('onion', 'vegetable', 'pcs'),
    ('tomato', 'vegetable', 'pcs'),
    ('potato', 'vegetable', 'pcs'),
    ('mustard seeds', 'spice', 'g'),
    ('cumin seeds', 'spice', 'g'),
    ('coriander powder', 'spice', 'g'),
    ('garam masala', 'spice', 'g'),
    ('tur dal', 'legume', 'g'),
    ('moong dal', 'legume', 'g'),
    ('chana dal', 'legume', 'g'),
    ('urad dal', 'legume', 'g'),
    ('lentils', 'legume', 'g'),
    ('toor dal', 'legume', 'g'),
    ('curry leaves', 'herb', 'g'),
    ('ginger', 'vegetable', 'g'),
    ('coconut', 'fruit', 'g'),
    ('coriander', 'herb', 'g'),
    ('fenugreek', 'herb', 'g'),
    ('besan', 'flour', 'g'),
    ('yogurt', 'dairy', 'ml'),
    ('curd', 'dairy', 'ml'),
    ('milk', 'dairy', 'ml'),
    ('butter', 'dairy', 'g'),
    ('ghee', 'dairy', 'g'),
    ('margarine', 'dairy', 'g'),
    ('oil', 'oil', 'ml'),
    ('olive oil', 'oil', 'ml'),
    ('cooking oil', 'oil', 'ml'),
    ('sesame oil', 'oil', 'ml'),
    ('pav buns', 'bakery', 'pcs'),
    ('bread', 'bakery', 'slices'),
    ('tomato puree', 'canned', 'ml'),
    ('green peas', 'vegetable', 'g'),
    ('spinach', 'vegetable', 'g'),
    ('egg', 'protein', 'pcs'),
    ('paneer', 'dairy', 'g'),
    ('chili powder', 'spice', 'g'),
    ('tamarind', 'fruit', 'g'),
    ('jaggery', 'sweetener', 'g'),
    ('peanuts', 'nut', 'g'),
    ('coconut oil', 'oil', 'ml'),
    ('vinegar', 'condiment', 'ml'),
    ('ginger-garlic paste', 'condiment', 'g'),
    ('asafoetida', 'spice', 'g'),
]

cur.executemany("INSERT OR IGNORE INTO ingredients (name, category, unit) VALUES (?, ?, ?);", ingredients)

# Insert recipes (Telugu, Gujarati, Marathi, Pan-Indian)
recipes = [
    # Telugu / South
    ('Pesarattu (moong dal dosa)', 'Telugu', 2, 'Soak moong dal, grind, ferment slightly, cook like dosa.'),
    ('Pulihora (tamarind rice)', 'Telugu', 3, 'Cook rice; prepare tamarind tempering; mix and serve.'),
    ('Hyderabadi Biryani (veg)', 'Telugu', 4, 'Layer cooked rice with spiced vegetables and dum cook.'),
    ('Sambar', 'South Indian', 4, 'Cook toor dal; add vegetables and sambar masala and tamarind.'),
    # Gujarati
    ('Khichdi', 'Gujarati', 3, 'Cook rice and moong dal together with turmeric and salt.'),
    ('Khandvi', 'Gujarati', 4, 'Make gram flour batter, spread thin and roll.'),
    ('Dhokla', 'Gujarati', 4, 'Ferment besan batter with eno and steam.'),
    ('Thepla', 'Gujarati', 6, 'Make soft dough with wheat flour and methi, roll and cook on tawa.'),
    # Marathi / Maharashtrian
    ('Pithla Bhakri (besan curry & flatbread)', 'Marathi', 3, 'Make pithla from besan and spices; serve with bhakri or roti.'),
    ('Misal Pav', 'Marathi', 4, 'Cook sprouted matki curry, top with farsan, serve with pav.'),
    ('Poha', 'Marathi', 2, 'Flattened rice tempered with mustard, curry leaves, peanuts and turmeric.'),
    ('Vada Pav', 'Marathi', 2, 'Spiced potato filling battered in besan fried and served in pav.'),
    # Pan-Indian favorites
    ('Pancakes', 'International', 4, 'Mix flour, milk, egg and cook on skillet.'),
    ('Tomato Pasta', 'Italian', 2, 'Cook pasta, prepare tomato garlic sauce.'),
]

cur.executemany("INSERT INTO recipes (name, cuisine, servings, instructions) VALUES (?, ?, ?, ?);", recipes)

# Map names -> ids
cur.execute("SELECT id, name FROM ingredients;")
rows = cur.fetchall()
name_to_id = {name: iid for iid, name in rows}

cur.execute("SELECT id, name FROM recipes;")
rows = cur.fetchall()
recipe_to_id = {name: rid for rid, name in rows}

# Helper to add recipe ingredient by name
def add_ing(recipe_name, ing_name, qty=0, unit='', optional=0):
    rid = recipe_to_id.get(recipe_name)
    iid = name_to_id.get(ing_name)
    if rid and iid:
        cur.execute("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, qty, unit, optional) VALUES (?, ?, ?, ?, ?)",
                    (rid, iid, qty, unit, optional))

# Add ingredients to recipes (simplified essential sets)
# Pesarattu
add_ing('Pesarattu (moong dal dosa)', 'moong dal', 200, 'g', 0)
add_ing('Pesarattu (moong dal dosa)', 'rice', 50, 'g', 0)
add_ing('Pesarattu (moong dal dosa)', 'green chili', 2, 'pcs', 0)
add_ing('Pesarattu (moong dal dosa)', 'ginger', 10, 'g', 0)
add_ing('Pesarattu (moong dal dosa)', 'salt', 2, 'g', 0)

# Pulihora
add_ing('Pulihora (tamarind rice)', 'rice', 300, 'g', 0)
add_ing('Pulihora (tamarind rice)', 'tamarind', 30, 'g', 0)
add_ing('Pulihora (tamarind rice)', 'mustard seeds', 3, 'g', 0)
add_ing('Pulihora (tamarind rice)', 'peanuts', 30, 'g', 1)
add_ing('Pulihora (tamarind rice)', 'curry leaves', 5, 'g', 1)

# Hyderabadi Biryani (veg)
add_ing('Hyderabadi Biryani (veg)', 'basmati rice', 300, 'g', 0)
add_ing('Hyderabadi Biryani (veg)', 'onion', 2, 'pcs', 0)
add_ing('Hyderabadi Biryani (veg)', 'tomato', 2, 'pcs', 0)
add_ing('Hyderabadi Biryani (veg)', 'yogurt', 100, 'ml', 0)
add_ing('Hyderabadi Biryani (veg)', 'garam masala', 5, 'g', 0)
add_ing('Hyderabadi Biryani (veg)', 'oil', 40, 'ml', 0)

# Sambar
add_ing('Sambar', 'toor dal', 200, 'g', 0)
add_ing('Sambar', 'tamarind', 20, 'g', 0)
add_ing('Sambar', 'drumstick', 0, '', 1)  # optional - not in ingredient list but kept optional
add_ing('Sambar', 'turmeric', 2, 'g', 0)
add_ing('Sambar', 'sambar masala', 10, 'g', 0)

# Khichdi
add_ing('Khichdi', 'rice', 200, 'g', 0)
add_ing('Khichdi', 'moong dal', 100, 'g', 0)
add_ing('Khichdi', 'turmeric', 2, 'g', 0)
add_ing('Khichdi', 'ghee', 10, 'g', 1)

# Dhokla
add_ing('Dhokla', 'besan', 200, 'g', 0)
add_ing('Dhokla', 'yogurt', 100, 'ml', 0)
add_ing('Dhokla', 'eno', 5, 'g', 0)  # eno may not exist in ingredients table; optional note

# Thepla
add_ing('Thepla', 'wheat flour', 250, 'g', 0)
add_ing('Thepla', 'fenugreek', 20, 'g', 0)
add_ing('Thepla', 'turmeric', 1, 'g', 0)
add_ing('Thepla', 'oil', 10, 'ml', 0)

# Pithla Bhakri
add_ing('Pithla Bhakri (besan curry & flatbread)', 'besan', 150, 'g', 0)
add_ing('Pithla Bhakri (besan curry & flatbread)', 'onion', 1, 'pcs', 1)
add_ing('Pithla Bhakri (besan curry & flatbread)', 'garlic', 3, 'cloves', 0)
add_ing('Pithla Bhakri (besan curry & flatbread)', 'oil', 20, 'ml', 0)

# Misal Pav - simplified
add_ing('Misal Pav', 'moong dal', 150, 'g', 0)
add_ing('Misal Pav', 'onion', 1, 'pcs', 0)
add_ing('Misal Pav', 'garlic', 2, 'cloves', 0)
add_ing('Misal Pav', 'pav buns', 4, 'pcs', 0)

# Poha
add_ing('Poha', 'poha', 200, 'g', 0)
add_ing('Poha', 'mustard seeds', 2, 'g', 0)
add_ing('Poha', 'peanuts', 30, 'g', 1)
add_ing('Poha', 'turmeric', 1, 'g', 0)

# Vada Pav (potato filling)
add_ing('Vada Pav', 'potato', 300, 'g', 0)
add_ing('Vada Pav', 'besan', 100, 'g', 0)
add_ing('Vada Pav', 'pav buns', 4, 'pcs', 0)

# Pancakes
add_ing('Pancakes', 'flour', 200, 'g', 0)
add_ing('Pancakes', 'milk', 300, 'ml', 0)
add_ing('Pancakes', 'egg', 2, 'pcs', 0)
add_ing('Pancakes', 'sugar', 30, 'g', 0)
add_ing('Pancakes', 'butter', 20, 'g', 1)

# Tomato Pasta
add_ing('Tomato Pasta', 'pasta', 200, 'g', 0)
add_ing('Tomato Pasta', 'tomato', 3, 'pcs', 0)
add_ing('Tomato Pasta', 'garlic', 2, 'cloves', 0)
add_ing('Tomato Pasta', 'olive oil', 20, 'ml', 0)
add_ing('Tomato Pasta', 'basil', 5, 'g', 1)

conn.commit()

# Add some substitution pairs (ingredient -> substitute, score 0..1)
# butter -> margarine
def add_sub(orig, sub, score=0.8, notes=''):
    orig_id = name_to_id.get(orig)
    sub_id = name_to_id.get(sub)
    if orig_id and sub_id:
        cur.execute("INSERT OR IGNORE INTO substitutions (ingredient_id, substitute_id, score, notes) VALUES (?, ?, ?, ?)",
                    (orig_id, sub_id, score, notes))

add_sub('butter', 'margarine', 0.8, 'Margarine often works instead of butter.')
add_sub('ghee', 'oil', 0.6, 'Oil can substitute for ghee, flavour differs.')
add_sub('yogurt', 'curd', 0.95, 'Yogurt and curd are equivalent in most Indian kitchens.')
add_sub('basmati rice', 'rice', 0.9, 'Any long-grain rice can substitute for basmati in many recipes.')
add_sub('olive oil', 'cooking oil', 0.85, 'Any neutral cooking oil works.')
add_sub('moong dal', 'toor dal', 0.5, 'Legumes can substitute but cooking times differ.')
add_sub('ghee', 'butter', 0.9, 'Butter can often replace ghee.')

conn.commit()
conn.close()
print("Seeding complete.")
