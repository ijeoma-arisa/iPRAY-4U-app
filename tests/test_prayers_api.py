from models import Relationship
from helpers.assertions import (
    assert_success_response, 
    assert_error_response,
    assert_valid_delete_response,
    assert_prayer_data,
)
from helpers.fixtures import client
from helpers.sample_data import (
    generate_person_json, 
    generate_prayer_json,
    update_existing_json_fields  
)
from helpers.urls import (
    PEOPLE_URL, 
    PERSON_1_PRAYERS_URL,
    get_prayers_url,
)

# POST endpoint
def test_add_prayer_valid_default_has_prayed(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json("Good grades")        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)
    
    assert_success_response(
        response,
        expected_message="Prayer added",
        expected_status=201
    )
    
def test_add_prayer_valid_set_has_prayed(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json("Good grades", has_prayed=True)        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)
    
    assert_success_response(
        response,
        expected_message="Prayer added",
        expected_status=201
    )
    
def test_add_prayer_valid_missing_has_prayed(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json("Good grades", has_prayed=None)        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)
    
    assert_success_response(
        response,
        expected_message="Prayer added",
        expected_status=201
    )

def test_add_prayer_missing_prayer(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json(prayer=None, has_prayed=True)        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)

    assert_error_response(
        response,
        expected_message="Validation failed",
        expected_errors={"'prayer' is required."}
    )

def test_add_prayer_invalid_prayer(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json(prayer=123, has_prayed=True)        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)

    assert_error_response(
        response,
        expected_message="Validation failed",
        expected_errors={"'prayer' is required."}
    )

def test_add_prayer_invalid_has_prayed(client):
    person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
    client.post(PEOPLE_URL, json=person)
    
    prayer = generate_prayer_json(prayer=None, has_prayed=True)        
    response = client.post(PERSON_1_PRAYERS_URL, json=prayer)

    assert_error_response(
        response,
        expected_message="Validation failed",
        expected_errors={"'prayer' is required."}
    )


# GET endpoint
def test_get_prayers(client):    
    people = [
        generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
        generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    ]
    
    