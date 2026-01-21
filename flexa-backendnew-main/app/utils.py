def compute_bmi(height_m: float, weight_kg: float) -> float:
    """
    BMI = weight (kg) / height^2 (m^2)
    """
    if height_m <= 0:
        raise ValueError("Height must be > 0")
    return weight_kg / (height_m ** 2)


def bmi_level(bmi: float) -> str:
    """
    Simple BMI categories (general):
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def normalize_yes_no(value: str) -> str:
    v = str(value).strip().lower()
    if v in ["yes", "y", "true", "1"]:
        return "Yes"
    return "No"


def normalize_sex(value: str) -> str:
    v = str(value).strip().lower()
    if v.startswith("m"):
        return "Male"
    if v.startswith("f"):
        return "Female"
    # fallback
    return value.strip().capitalize()
