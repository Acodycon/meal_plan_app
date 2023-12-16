def compute_BMR(gender:str,weight:float,height:float,age:int):
    """
    gender in  F/M
    weight in kg\n
    height in cm\n
    age in years
    """
    return 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age) if gender == "Male" else 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age) if gender == "Female" else "Wrong Gender syntax"

def compute_TDEE(BMR,activity):
    """
    BMR => Base Metabolic Rate\n
    Activity_Level:\n
    light = 1 - 3 days/week\n
    moderate = 3 - 5 days/week\n
    high = 6 - 7 days/week\n
    very high = intense sports every day
    """
    print(f"BMR:{BMR}")
    print(f"activity:{activity}")
    return float(BMR) * activity


