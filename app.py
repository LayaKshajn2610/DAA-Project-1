import os
from flask import Flask, request, jsonify, render_template
import sqlite3
from recipe_matching import RecipeMatcher

app = Flask(__name__, static_folder='static', template_folder='templates')

# make DB path absolute (safe regardless of how you run the app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'recipes.db')

# create matcher (will raise clear errors if DB missing/corrupt)
matcher = RecipeMatcher(db_path=DB_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/suggest', methods=['POST'])
def suggest():
    data = request.get_json() or {}
    user_ings = [i.strip().lower() for i in data.get('ingredients', [])]
    max_results = int(data.get('max_results', 20))
    allow_subst = bool(data.get('allow_subst', True))
    results = matcher.suggest(user_ings, max_results=max_results, allow_subst=allow_subst)
    return jsonify(results)


@app.route('/api/recipe/<int:recipe_id>', methods=['GET'])
def recipe_details(recipe_id: int):
    # Return recipe details including instructions and ingredients
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, cuisine, servings, instructions FROM recipes WHERE id=?", (recipe_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    rid, name, cuisine, servings, instructions = row
    cur.execute(
        """
        SELECT i.name, COALESCE(ri.qty, 0), COALESCE(ri.unit, ''), COALESCE(ri.optional, 0)
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = ?
        ORDER BY i.name
        """,
        (recipe_id,)
    )
    ings = [
        {
            'name': n,
            'qty': q,
            'unit': u,
            'optional': bool(opt)
        } for (n, q, u, opt) in cur.fetchall()
    ]
    conn.close()
    return jsonify({
        'id': rid,
        'name': name,
        'cuisine': cuisine,
        'servings': servings,
        'instructions': instructions,
        'ingredients': ings
    })

if __name__ == '__main__':
    # debug=True for development only
    app.run(debug=True, host='0.0.0.0', port=5000)
