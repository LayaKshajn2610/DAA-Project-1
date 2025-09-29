# recipe_matching.py
import sqlite3
import os
from substitution import SubstitutionEngine
from collections import defaultdict
import math

class RecipeMatcher:
    def __init__(self, db_path='data/recipes.db'):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"SQLite DB not found at: {self.db_path}")
        # test connection
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.close()
        # load graph
        self._load_graph()
        self.subst = SubstitutionEngine(self.db_path)

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _load_graph(self):
        self.recipes = {}
        self.req_ings = defaultdict(set)
        self.opt_ings = defaultdict(set)
        self.ingredient_popularity = defaultdict(int)  # how many recipes use an ingredient

        conn = self._conn()
        cur = conn.cursor()
        cur.execute('SELECT id, name, cuisine, servings FROM recipes')
        for r_id, name, cuisine, servings in cur.fetchall():
            self.recipes[r_id] = {'id': r_id, 'name': name, 'cuisine': cuisine, 'servings': servings}

        cur.execute('''SELECT ri.recipe_id, lower(i.name), ri.optional
                       FROM recipe_ingredients ri
                       JOIN ingredients i ON i.id = ri.ingredient_id''')
        for recipe_id, ing_name, optional in cur.fetchall():
            ing_name = ing_name.lower()
            if optional:
                self.opt_ings[recipe_id].add(ing_name)
            else:
                self.req_ings[recipe_id].add(ing_name)
            self.ingredient_popularity[ing_name] += 1

        conn.close()

    def suggest(self, user_ingredients, max_results=20, allow_subst=True):
        """
        user_ingredients: list of ingredient names (strings)
        allow_subst: bool - whether to attempt substitutes
        """
        S = set([u.strip().lower() for u in (user_ingredients or [])])
        candidates = []

        # Precompute rarity boost: ingredients that appear in fewer recipes are rarer -> positive boost if present
        # rarity_score(ing) = 1 / (1 + log(1 + popularity))
        rarity_score = {}
        for ing, pop in self.ingredient_popularity.items():
            rarity_score[ing] = 1.0 / (1.0 + math.log(1 + pop))

        for r_id, recipe in self.recipes.items():
            required = set(self.req_ings.get(r_id, set()))
            optional = set(self.opt_ings.get(r_id, set()))
            missing = required - S
            optional_missing = optional - S

            subst_plan = {}
            covered_by_subst = 0

            if allow_subst and missing:
                # try to cover each missing ingredient with substitutes
                for m in list(missing):
                    subs = self.subst.find_substitutes(m, limit=6)
                    # prefer substitutes present in S
                    chosen = None
                    chosen_score = 0.0
                    chosen_reason = None
                    for name, score, reason in subs:
                        if name in S:
                            # choose best substitute present in pantry
                            if score > chosen_score:
                                chosen = name
                                chosen_score = score
                                chosen_reason = reason
                    if chosen:
                        covered_by_subst += 1
                        subst_plan[m] = {'substitute': chosen, 'score': chosen_score, 'reason': chosen_reason}

            missing_after_subst = set([m for m in missing if m not in subst_plan])
            req_count = max(1, len(required))
            # match fraction after substitution
            matched = req_count - len(missing_after_subst)
            match_fraction = matched / req_count

            # substitution coverage fraction
            subst_fraction = covered_by_subst / req_count

            # optional penalty
            optional_penalty = len(optional_missing) / max(1, len(optional) + 1)

            # rarity bonus: if user has rare ingredients required by recipe, bump score a bit
            rarity_bonus = 0.0
            for ing in required & S:
                rarity_bonus += 0.05 * rarity_score.get(ing, 0.2)  # small additive bonus

            # final score (weighted)
            score = (0.7 * match_fraction) + (0.18 * subst_fraction) + (0.02 * rarity_bonus) - (0.04 * optional_penalty)

            # normalize score into 0..1
            score = max(0.0, min(1.0, score))

            # additional metadata for ranking: fewer total required ingredients preferred if scores close
            candidates.append({
                'score': score,
                'r_id': r_id,
                'missing_after_subst': sorted(list(missing_after_subst)),
                'substitution_plan': subst_plan,
                'required_count': req_count,
                'matched_count': matched
            })

        # sort by score desc, tiebreaker: fewer missing after subst, more matched, fewer required_count
        candidates.sort(key=lambda x: (x['score'], -x['matched_count'], -x['required_count']), reverse=True)

        out = []
        for item in candidates[:max_results]:
            r = self.recipes[item['r_id']]
            out.append({
                'recipe_id': item['r_id'],
                'name': r['name'],
                'cuisine': r.get('cuisine'),
                'score': round(item['score'], 3),
                'required_count': item['required_count'],
                'matched_count': item['matched_count'],
                'missing_ingredients': item['missing_after_subst'],
                'substitution_plan': item['substitution_plan']
            })
        return out
