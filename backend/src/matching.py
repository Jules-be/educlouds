from ..models import Lender


# Score table: how well a lender's resource_type matches the job's estimated_workload
# Higher score = better match
MATCH_SCORE = {
    "High":   {"High": 3, "Medium": 1, "Low": 0},
    "Medium": {"High": 2, "Medium": 3, "Low": 1},
    "Low":    {"High": 1, "Medium": 2, "Low": 3},
}


def find_best_lender(estimated_workload):
    """
    Given a job's estimated workload (High/Medium/Low),
    find the best available lender from the database.
    Returns the winning Lender object, or None if no lender is available.
    """
    available_lenders = Lender.query.filter_by(availability_status="Available").all()

    if not available_lenders:
        return None

    best_lender = None
    best_score = -1

    for lender in available_lenders:
        score = calculate_score(estimated_workload, lender.resource_type)
        if score > best_score:
            best_lender = lender
            best_score = score

    return best_lender


def calculate_score(estimated_workload, resource_type):
    """
    Return a compatibility score between a job's workload and a lender's resource type.
    Score ranges from 0 (incompatible) to 3 (perfect match).
    """
    return MATCH_SCORE.get(estimated_workload, {}).get(resource_type, 0)
