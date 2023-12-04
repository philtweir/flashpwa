import json
import numpy as np
import random

with open("forms.json", "r") as forms_f:
    forms = json.load(forms_f)

weights = np.array([entry["multiplier"] for entry in forms])
weights = weights / weights.sum()
for n in range(1000):
    block = np.random.choice(forms, 1000, p=weights)
    with open(f"forms-{n}.json", "w") as block_f:
        json.dump(block.tolist(), block_f)
