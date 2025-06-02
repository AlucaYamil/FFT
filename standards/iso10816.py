THRESHOLDS = {"G1": (1.8, 4.5, 7.1), "G2": (2.8, 7.1, 11.0)}

def zone(value_mm_s: float, group: str = "G1") -> str:
    a,b,c = THRESHOLDS[group]
    if value_mm_s < a: return "A"
    if value_mm_s < b: return "B"
    if value_mm_s < c: return "C"
    return "D"