import random
import math

def process_data(**kwargs):
    result = {}
    for key, value in kwargs.items():
        if key == 'Ages':
            result[key] = [round(v + random.random(), 3) if isinstance(v, (int, float)) and not math.isnan(v) else v for v in value]

        elif key == 'Grades':
            result[key] = [str(v).upper() for v in value ]

        else:
            result[key] = value

        print(f"key={key}, value={result[key]}")

    return result