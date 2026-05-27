from helpers.assertions import (
    assert_success_response, 
    assert_error_response,
    assert_valid_delete_response,
    assert_prayer_data,
    assert_prayers_list,
)
from helpers.fixtures import  (
    client, 
    sample_person, 
    sample_prayer,
)

from helpers.sample_data import (
    generate_person_json, 
    generate_prayer_json,
    update_existing_json_fields  
)

from helpers.urls import get_prayers_url, PRAYERS_URL
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

# GET endpoint
def test_get_all_prayers(client, sample_person):
    person1_id = sample_person["id"]
    prayers_url = get_prayers_url(person1_id)
    
    client.post(prayers_url, json=generate_prayer_json("Grace"))

    response = client.get(PRAYERS_URL)
    
    data = assert_success_response(
        response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert len(data) == 2


def test_get_prayers_by_person(client, sample_person):    
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
    
# PATCH endpoint
def test_update_prayer_valid_prayer_only(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    updated_prayer_field = {"prayer": "Peace of mind"}
    update_existing_json_fields(updated_prayer_field, sample_prayer)
    
    response = client.patch(prayer_url, json=updated_prayer_field)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)
    
    
def test_update_prayer_valid_has_prayed_only(client, sample_prayer):   
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    updated_has_prayed_field = {"has_prayed": True}
    update_existing_json_fields(updated_has_prayed_field, sample_prayer)
    
    response = client.patch(prayer_url, json=updated_has_prayed_field)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)


def test_update_prayer_valid_all_fields(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id) 
    
    updated_prayer_and_has_prayed_fields = {
        "prayer": "Peace of mind",
        "has_prayed": True
    }
    
    update_existing_json_fields(updated_prayer_and_has_prayed_fields, sample_prayer)

    response = client.patch(prayer_url, json=updated_prayer_and_has_prayed_fields)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)

def test_update_prayer_missing_all_fields(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    person_prayers_url = get_prayers_url(person_id)
    
    get_prayers_response = client.get(person_prayers_url)
    original_prayers_list = assert_success_response(
        get_prayers_response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id) 
    
    response = client.patch(prayer_url, json={})
    
    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors=set(required_error(["prayer", "has_prayed"]))
    )
    
    get_prayers_response = client.get(person_prayers_url)
    
    prayers_data_list = assert_success_response(
        get_prayers_response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert_prayers_list(prayers_data_list, original_prayers_list)
    

# DELETE endpoint
def test_delete_prayer_valid(client, sample_prayer):
    pass

def test_delete_prayer_nonexistent_id(client, sample_prayer):
    pass

def test_delete_prayer_duplicate_request(client, sample_prayer):
    pass