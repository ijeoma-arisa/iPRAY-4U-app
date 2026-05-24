PEOPLE_URL = '/api/people'

PERSON_1_PRAYERS_URL = f"{PEOPLE_URL}/1/prayers"

def get_prayers_url(person_id: int = None, prayer_id: int = None):
    if person_id is None:
        return '/api/prayers'
    
    prayers_url = f"{PEOPLE_URL}/{person_id}/prayers"
    if prayer_id is not None:
        prayers_url += f"/{prayer_id}"
    return prayers_url
    