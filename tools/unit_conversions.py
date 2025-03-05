conversion_factors = {
    'mg/100g': 1,
    'mg/100 g': 1,
    'mg/kg': 0.1,
    'mg/100 g of dry matter': 1,  # Assuming dry matter is similar
    'mg/kg fresh weight': 0.1,
    'mg/100 g fresh weight': 1,
    'mg/100 g freshweight': 1,
    'umol/g Fresh weight': 0.001,  # Assuming molecular weight not provided
    'umol/g dry weight': 0.001,    # Assuming molecular weight not provided
    'mg/g dry weight': 100,        # 1 g = 100 mg
    'mg/100 g dry weight': 1,
    'ug/L': 0.0001,                # 1 ug = 0.001 mg
    'ppb': 0.001,                  # 1 ppb = 0.001 mg/kg
    'mg/l': 0.1,                   # 1 liter = 1 kg (assuming water density)
    'mg/kg fresh sample': 0.1,
    'mg/kg puree': 0.1,
    'g/kg fresh weight': 1000,     # 1 g = 1000 mg
    'IU': None,                    # Requires compound-specific information
    'IU/100 g': None,              # Requires compound-specific information
    'RE': None,                    # Requires compound-specific information
    'NE': None,                    # Cannot be normalized
}

# Function to normalize content amounts
def normalize_content(orig_content, orig_unit):
    factor = conversion_factors.get(orig_unit)
    if factor is not None and orig_content is not None:
        return orig_content * factor
    return None  # Return None if unit cannot be normalized

def calc_score(content, condition):
    if content > 120:
        return 5*condition
    elif content > 70:
        return 4*condition
    elif content > 40:
        return 3*condition
    elif content > 20:
        return 2*condition
    else:
        return condition
