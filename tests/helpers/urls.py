PEOPLE_URL = '/api/people'
RELATIONSHIPS_URL = '/api/relationships'

def get_prayers_url(person_id: int = None, prayer_id: int = None):
    if person_id is None:
        return '/api/prayers'
    
    prayers_url = f"{PEOPLE_URL}/{person_id}/prayers"
    if prayer_id is not None:
        prayers_url += f"/{prayer_id}"
    return prayers_url
    