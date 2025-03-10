import math
from typing import List, Dict


def calculate_compound_health_weight(papers: List[Dict[str, float]], max_participants: float) -> float:
    """
    Calculate the weight w(c,h) between a compound and health condition.

    Args:
        papers: List of dictionaries containing study data for each paper
               Each dict should have: 'effect_source', 'participants', 'bias'
        max_participants: Maximum number of participants across all studies

    Returns:
        float: Total weight w(c,h)
    """
    # Effect source weights
    EFFECT_SOURCE_WEIGHTS = {
        'single_compound': 6,
        'combination_therapy': 4,
        'comparative': 4,
        'derivative': 2,
        'other': 1
    }

    total_weight = 0.0

    for paper in papers:
        # Get effect source weight (Ep)
        effect_weight = EFFECT_SOURCE_WEIGHTS.get(paper['effect_source'].lower(), 1)

        # Calculate normalized participant count (Np')
        np = paper['participants']
        normalized_participants = math.log(np + 1) / math.log(max_participants + 1)

        # Calculate bias adjustment (Bp')
        bias = max(0.0, min(1.0, paper['bias']))  # Ensure bias is between 0 and 1
        bias_adjusted = 1 - math.sqrt(bias)

        # Calculate individual paper weight (wp)
        paper_weight = effect_weight * normalized_participants * bias_adjusted
        total_weight += paper_weight

    return total_weight


# Example usage:
papers_data = [
    {'effect_source': 'single_compound', 'participants': 100, 'bias': 0.2},
    {'effect_source': 'comparative', 'participants': 500, 'bias': 0.4},
    {'effect_source': 'derivative', 'participants': 50, 'bias': 0.1}
]
max_n = 1000  # Should be set to maximum across all studies
weight_ch = calculate_compound_health_weight(papers_data, max_n)
print(f"Compound to Health weight: {weight_ch}")


def calculate_food_health_weight(compounds_data: Dict[str, Dict[str, float]]) -> float:
    """
    Calculate the weight w(f,h) between a food and health condition through compounds.

    Args:
        compounds_data: Dictionary with compound IDs as keys and nested dict as values
                       containing 'w_ch' (compound-health weight),
                       'w_cf' (compound-food content), and 'n_c' (compound frequency)

    Returns:
        float: Total weight w(f,h)
    """
    total_weight = 0.0

    for compound_id, data in compounds_data.items():
        w_ch = data.get('w_ch', 0.0)  # Compound to health weight
        w_cf = data.get('w_cf', 0.0)  # Compound content in food
        n_c = data.get('n_c', 1.0)  # Frequency of compound across foods

        # Calculate compound contribution with rarity adjustment
        compound_weight = w_ch * w_cf * (1 / math.log(n_c + 1))
        total_weight += compound_weight

    return total_weight


# Example usage:
compounds_data = {
    'c1': {'w_ch': 2.5, 'w_cf': 0.8, 'n_c': 5},
    'c2': {'w_ch': 1.8, 'w_cf': 0.6, 'n_c': 2},
    'c3': {'w_ch': 3.0, 'w_cf': 0.3, 'n_c': 10}
}
weight_fh = calculate_food_health_weight(compounds_data)
print(f"Food to Health weight: {weight_fh}")