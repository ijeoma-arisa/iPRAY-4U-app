from .helpers.assertions import (
    assert_success_response, 
    assert_error_response,
    assert_valid_delete_response,
    assert_prayer_data,
    assert_prayers_list,
)
from .helpers.fixtures import  (
    client, 
    auth_client,
    sample_person, 
    sample_prayer,
)

from .helpers.sample_data import generate_prayer_json, update_existing_json_fields
from .helpers.urls import get_prayers_url, PRAYERS_URL
from ipray4u.utils.error_messages import (
    VALIDATION_FAILED_ERROR,
    AUTHENTICATION_REQUIRED_ERROR,
    required_error,
    string_error,
    not_found_error,
)

from ipray4u.utils.success_messages import (
    get_success,
    post_success,
    patch_success,
)

POST_PRAYER_SUCCESS_MSG = post_success("Prayer")

# POST endpoint
def test_add_prayer_auth_required(client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    with client.session_transaction() as session:
        session.clear()
    
    prayer = generate_prayer_json("Good grades")
    response = client.post(prayers_url, json=prayer)
    
    assert_error_response(
        response,
        expected_message=AUTHENTICATION_REQUIRED_ERROR,
        expected_status=401
    )    

def test_add_valid_prayer_default_has_prayed_field(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades")        
    response = auth_client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )
    
def test_add_valid_prayer_set_has_prayed_field(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades", has_prayed=True)        
    response = auth_client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )
    
def test_add_valid_prayer_missing_has_prayed_field(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json("Good grades", has_prayed=None)        
    response = auth_client.post(prayers_url, json=prayer)
    
    assert_success_response(
        response,
        expected_message=POST_PRAYER_SUCCESS_MSG,
        expected_status=201
    )

def test_add_invalid_prayer_missing_prayer_field(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json(prayer=None, has_prayed=True)        
    response = auth_client.post(prayers_url, json=prayer)

    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors={required_error("prayer")}
    )

def test_add_invalid_prayer_invalid_prayer_field(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayer = generate_prayer_json(prayer=123, has_prayed=True)        
    response = auth_client.post(prayers_url, json=prayer)

    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors={string_error("prayer")}
    )

# GET endpoint
def test_get_all_prayers_auth_required(client, sample_prayer):
    _ = sample_prayer

    with client.session_transaction() as session:
        session.clear()
    
    response = client.get(PRAYERS_URL)
    
    assert_error_response(
        response,
        expected_message=AUTHENTICATION_REQUIRED_ERROR,
        expected_status=401
    )    

def test_get_all_prayers(auth_client, sample_person):
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    auth_client.post(prayers_url, json=generate_prayer_json("Grace"))

    response = auth_client.get(PRAYERS_URL)
    
    data = assert_success_response(
        response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert len(data) == 2


def test_prayers_by_person_auth_required(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayers_url = get_prayers_url(person_id)
    

    with client.session_transaction() as session:
        session.clear()
    
    response = client.get(prayers_url)
    
    assert_error_response(
        response,
        expected_message=AUTHENTICATION_REQUIRED_ERROR,
        expected_status=401
    )   
    
def test_get_prayers_by_person(auth_client, sample_person):    
    person_id = sample_person["id"]
    prayers_url = get_prayers_url(person_id)
    
    prayers = [
        generate_prayer_json("Clarity"),
        generate_prayer_json("Peace of mind"),
        generate_prayer_json("Joy")
    ]
    
    for prayer in prayers:
        auth_client.post(prayers_url, json=prayer)
    
    response = auth_client.get(prayers_url)
    
    data = assert_success_response(
        response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert isinstance(data, list)
    assert len(data) == 4
    
# PATCH endpoint
def test_update_prayer_auth_required(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    with client.session_transaction() as session:
        session.clear()
    
    updated_prayer_field = {"prayer": "Peace of mind"}
    update_existing_json_fields(updated_prayer_field, sample_prayer)
    
    response = client.patch(prayer_url, json=updated_prayer_field)
    
    assert_error_response(
        response,
        expected_message=AUTHENTICATION_REQUIRED_ERROR,
        expected_status=401
    )

def test_update_prayer_valid_prayer_only(auth_client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    updated_prayer_field = {"prayer": "Peace of mind"}
    update_existing_json_fields(updated_prayer_field, sample_prayer)
    
    response = auth_client.patch(prayer_url, json=updated_prayer_field)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)
    
    
def test_update_prayer_valid_has_prayed_only(auth_client, sample_prayer):   
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    updated_has_prayed_field = {"has_prayed": True}
    update_existing_json_fields(updated_has_prayed_field, sample_prayer)
    
    response = auth_client.patch(prayer_url, json=updated_has_prayed_field)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)


def test_update_prayer_valid_all_fields(auth_client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id) 
    
    updated_prayer_and_has_prayed_fields = {
        "prayer": "Peace of mind",
        "has_prayed": True
    }
    
    update_existing_json_fields(updated_prayer_and_has_prayed_fields, sample_prayer)

    response = auth_client.patch(prayer_url, json=updated_prayer_and_has_prayed_fields)
    
    prayer_data = assert_success_response(
        response,
        expected_message=patch_success("Prayer")
    )
    
    assert_prayer_data(prayer_data, sample_prayer)

def test_update_prayer_missing_all_fields(auth_client, sample_prayer):
    person_id = sample_prayer["person_id"]
    person_prayers_url = get_prayers_url(person_id)
    
    get_prayers_response = auth_client.get(person_prayers_url)
    original_prayers_list = assert_success_response(
        get_prayers_response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id) 
    
    response = auth_client.patch(prayer_url, json={})
    
    assert_error_response(
        response,
        expected_message=VALIDATION_FAILED_ERROR,
        expected_errors=set(required_error(["prayer", "has_prayed"]))
    )
    
    get_prayers_response = auth_client.get(person_prayers_url)
    
    prayers_data_list = assert_success_response(
        get_prayers_response,
        expected_message=get_success("Prayers"),
        data_type=list
    )
    
    assert_prayers_list(prayers_data_list, original_prayers_list)
    

# DELETE endpoint
def test_delete_prayer_auth_required(client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_id = sample_prayer["id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    with client.session_transaction() as session:
        session.clear()
    
    response = client.delete(prayer_url)
    
    assert_error_response(
        response,
        expected_message=AUTHENTICATION_REQUIRED_ERROR,
        expected_status=401
    )
    
def test_delete_prayer_valid(auth_client, sample_prayer):
    prayer_id = sample_prayer["id"]
    person_id = sample_prayer["person_id"]
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    response = auth_client.delete(prayer_url)
    
    assert_valid_delete_response(response)

def test_delete_prayer_nonexistent_id(auth_client, sample_prayer):
    person_id = sample_prayer["person_id"]
    prayer_url = get_prayers_url(person_id, 2)
    
    response = auth_client.delete(prayer_url)
    
    assert_error_response(
        response,
        expected_message=not_found_error("Prayer"),
        expected_status=404
    )

def test_delete_prayer_duplicate_request(auth_client, sample_prayer):
    prayer_id = sample_prayer["id"]
    person_id = sample_prayer["person_id"]
    
    prayer_url = get_prayers_url(person_id, prayer_id)
    
    auth_client.delete(prayer_url)
    
    response = auth_client.delete(prayer_url)
    
    assert_error_response(
        response,
        expected_message=not_found_error("Prayer"),
        expected_status=404
    )