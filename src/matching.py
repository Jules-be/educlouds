def match_resources(requests, resources):
    matches = []
    for request in requests:
        best_match = None
        best_score = 0
        for resource in resources:
            if resource['Availability']:
                score = calculate_compatibility_score(request, resource)
                if score > best_score:
                    best_match = resource
                    best_score = score
        matches.append((request['RequestID'], best_match['ResourceID']))
    return matches

def calculate_compatibility_score(request, resource):
    score = 0
    for req_resource in request['RequiredResources']:
        for avail_resource in resource['Specifications']:
            if req_resource['type'] == avail_resource['type']:
                # Example scoring: +10 points for each matching resource type
                score += 10
                if req_resource['type'] == 'CPU':
                    score += min(req_resource['cores'], avail_resource['cores'])
                elif req_resource['type'] == 'RAM':
                    score += min(req_resource['size'], avail_resource['size'])

    return score
