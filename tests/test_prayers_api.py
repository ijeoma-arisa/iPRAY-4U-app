from helpers.assertions import (
    assert_success_response, 
    assert_error_response,
    assert_valid_delete_response,
    assert_prayer_data,
)
from helpers.fixtures import client, sample_person
from helpers.sample_data import (
    generate_person_json, 
    generate_prayer_json,
    update_existing_json_fields  
)

from helpers.urls import get_prayers_url
from utils.error_messages import (
    VALIDATION_FAILED_ERROR,
    required_error,
    string_error,
    valid_relationship_error,
    not_found_error,
)

from utils.success_messages import (
    get_success,
    post_success,
    patch_success,
)

POST_PRAYER_SUCCESS_MSG = post_success("Prayer")

# POST endpoint
def test_add_valid_prayer_default_has_prayed_field(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades")        
    response = client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )
    
def test_add_valid_prayer_set_has_prayed_field(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades", has_prayed=True)        
    response = client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )
    
def test_add_valid_prayer_missing_has_prayed_field(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades", has_prayed=None)        
    response = client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )

def test_add_invalid_prayer_missing_prayer_field(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json(prayer=None, has_prayed=True)        
    response = client.post(prayers_url, json=prayer)

    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors={required_error("prayer")}
    )

def test_add_invalid_prayer_invalid_prayer_field(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json(prayer=123, has_prayed=True)        
    response = client.post(prayers_url, json=prayer)

    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors={string_error("prayer")}
    )
    
#TODO: Update invalid has_prayed field logic in API and validators
# def test_add_invalid_prayer_invalid_has_prayed_field(client, sample_person):
#     person_id = sample_person["id"]
#     prayers_url = get_prayers_url(person_id)
    
#     prayer = generate_prayer_json("Good grades", has_prayed="True")        
#     response = client.post(prayers_url, json=prayer)

#     assert_error_response(
#         response,
#         expected_message=VALIDATION_FAILED_ERROR,
#         expected_errors={PRAYER_REQUIRED_ERROR}
#     )


# GET endpoint
def test_get_prayers(client, sample_person):    
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayers = [
        generate_prayer_json("Clarity"),
        generate_prayer_json("Peace of mind"),
        generate_prayer_json("Joy")
    ]
    
    for prayer in prayers:
        client.post(prayers_url, json=prayer)
    
    response = client.get(prayers_url)
    
    data = assert_success_response(
        response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert isinstance(data, list)
    assert len(data) == 4