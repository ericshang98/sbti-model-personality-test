"""
Minimal example: take SBTI with all middle answers (value=2), print result.
Run: python example.py
"""
from sbti_score import load_data, score

data = load_data()
answers = {q["id"]: 2 for q in data.questions}  # everyone picks middle option
result = score(answers, data)

print(f"pattern: {result.pattern}")
print(f"final:   {result.final_type_code}  ({result.final_type.get('cn','')})")
print(f"special override: {result.special}")
print("top 3 normal matches:")
for r in result.ranked[:3]:
    print(f"  {r['code']:8s}  sim={r['similarity']:3d}%  exact={r['exact']}/15  dist={r['distance']}")
