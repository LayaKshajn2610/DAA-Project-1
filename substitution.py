# substitution.py
import sqlite3
import os

class SubstitutionEngine:
    def __init__(self, db_path='data/recipes.db'):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"SubstitutionEngine: DB not found at {self.db_path}")

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def find_substitutes(self, ingredient_name, limit=6):
        """
        Returns list of (substitute_name, score, reason)
        Strategies:
         - direct explicit substitutes from substitutions table (best)
         - same-category substitutes (look up ingredients with same category)
         - fuzzy substring matches (e.g., 'oil' -> 'olive oil' or 'cooking oil')
        """
        ing = ingredient_name.strip().lower()
        conn = self._conn()
        cur = conn.cursor()

        # 1) find ingredient id and category
        cur.execute("SELECT id, category FROM ingredients WHERE lower(name)=?", (ing,))
        row = cur.fetchone()
        if not row:
            # fallback: try substring match for ingredient name
            cur.execute("SELECT id, name, category FROM ingredients WHERE lower(name) LIKE ? LIMIT 1", (f"%{ing}%",))
            row = cur.fetchone()
        if not row:
            conn.close()
            return []

        ing_id, category = row[0], row[1] if row and len(row) > 1 else None

        results = []
        # 2) direct substitutions table
        cur.execute('''SELECT i2.name, s.score FROM substitutions s
                       JOIN ingredients i2 ON i2.id = s.substitute_id
                       WHERE s.ingredient_id = ? ORDER BY s.score DESC LIMIT ?''', (ing_id, limit))
        for name, score in cur.fetchall():
            results.append((name.lower(), float(score), 'direct'))

        # 3) same-category substitutes (if not too many results already)
        if category:
            needed = limit - len(results)
            if needed > 0:
                cur.execute('''SELECT name FROM ingredients WHERE category=? AND id != ? LIMIT ?''', (category, ing_id, needed))
                for (name,) in cur.fetchall():
                    # assign a modest default score for category match
                    results.append((name.lower(), 0.45, 'category'))

        # 4) fuzzy substring (e.g., 'oil' -> 'olive oil', 'cooking oil')
        needed = limit - len(results)
        if needed > 0:
            cur.execute("SELECT name FROM ingredients WHERE lower(name) LIKE ? AND id != ? LIMIT ?", (f"%{ing}%", ing_id, needed))
            for (name,) in cur.fetchall():
                results.append((name.lower(), 0.4, 'fuzzy'))

        conn.close()
        # deduplicate preserving best score
        dedup = {}
        for name, score, reason in results:
            if name not in dedup or dedup[name][0] < score:
                dedup[name] = (score, reason)
        out = [(n, dedup[n][0], dedup[n][1]) for n in dedup]
        # sort by score desc
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:limit]
