import pytest
import requests
import json
from src.error import AccessError, InputError
from src.other import check_session, SECRET, get_user
from src.config import url
from jwt import encode
from src.other import check_session, SECRET
from src.error import AccessError, InputError

#* Fixture that clears and registers the first user
@pytest.fixture
def user1():
    requests.delete(f"{url}clear/v1")    
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "first@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "1"
    })
    return response.json()

#* Fixture that registers a second user
@pytest.fixture
def user2():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "second@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "2"
    })
    return response.json()

# tests the return value of the auth login of a valid user
def test_http_auth_login_valid():
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    r = requests.post(f"{url}auth/login/v2", json={"email": "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    payload = r.json()
    assert payload['token'] == token
    assert payload['auth_user_id'] == 0

# tests the case when the inputted email is of invalid format
def test_http_auth_login_invalid_email():
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    response = requests.post(f"{url}auth/login/v2", json={"email": "caricoleman.com", "password": "1234567"})
    assert response.status_code == 400

# tests the case when the inputted email does not correspond to a registerd user
def test_http_auth_login_invalid_not_registered_email():
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/login/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    response = requests.post(f"{url}auth/login/v2", json={"email": "caricoleman@yahoo.com", "password": "1234567"})
    assert response.status_code == 400

# tests the case when the inputted password does not match the password of the user corresponding to 
# the inputted email
def test_http_auth_login_invalid_incorrect_password():
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    response = requests.post(f"{url}auth/login/v2", json={"email": "caricoleman@gmail.com", "password": "789101112"})
    assert response.status_code == 400

# tests the return value of an auth_register with valid input (email, password, first name, last name)
def test_http_auth_register_valid():
    requests.delete(f"{url}clear/v1")
    r = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    payload = r.json()
    assert payload["token"] == token
    assert payload['auth_user_id'] == 0

# tests the case when the inputted email is of invalid format 
def test_http_auth_register_invalid_email():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    assert response.status_code == 400

# tests the case when the inputted email is already used by a registered user  
def test_http_auth_register_invalid_email_in_use():
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "erica", "name_last": "mondy"})
    assert response.status_code == 400

# tests the case when the inputted password has less than 6 characters
def test_http_auth_register_invalid_password():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "123", "name_first": "cari", "name_last": "coleman"})
    assert response.status_code == 400

# tests the case when the inputted first name is empty
def test_http_auth_register_invalid_empty_first_name():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "", "name_last": "coleman"})
    assert response.status_code == 400

# tests the case when the inputted first name exceeds the 50 character limit
def test_http_auth_register_invalid_long_first_name():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cariiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", "name_last": "coleman"})
    assert response.status_code == 400

# tests the case when the inputted last name is empty
def test_http_auth_register_invalid_empty_last_name():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "", "name_last": ""})
    assert response.status_code == 400

# tests the case when the inputted last name exceeds the 50 character limit
def test_http_auth_register_invalid_long_last_name():
    requests.delete(f"{url}clear/v1")
    response = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "", "name_last": "colemaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaan"})
    assert response.status_code == 400

# tests for the existence of session ids and validity of tokens after a logout is called by a user
def test_http_auth_logout_valid():
    requests.delete(f"{url}clear/v1")
    response_1 = requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})
    payload_1 = response_1.json()
    response_2 = requests.post(f"{url}auth/login/v2", json={"email": "caricoleman@gmail.com", "password": "1234567"})
    payload_2 = response_2.json()
    
    response_3 = requests.post(f"{url}auth/logout/v1", json={'token': payload_1['token']})
    payload_3 = response_3.json()
    assert payload_3['is_success'] == True

    with pytest.raises(AccessError):
        check_session(0, 0)

    response_4 = requests.post(f"{url}auth/logout/v1", json={'token': payload_2['token']})
    payload_4 = response_4.json()
    assert payload_4['is_success'] == True

    with pytest.raises(AccessError):
        check_session(0, 1)

# tests for the case when a token with an invalid session_id is inputted
def test_http_auth_logout_v1_invalid():   
    requests.delete(f"{url}clear/v1")
    requests.post(f"{url}auth/register/v2", json={"email": "caricoleman@gmail.com", "password": "1234567", "name_first": "cari", "name_last": "coleman"})

    token_1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response_3 = requests.post(f"{url}auth/logout/v1", json={'token': token_1})
    assert response_3.status_code == 403

#* Test that for a registered email, it is successful (response 200)
def test_http_auth_passwordreset_valid_email(user1, user2):
    
    result = requests.post(f"{url}auth/passwordreset/request/v1", json={'email': get_user(user1['auth_user_id'])['email']})
    assert result.status_code == 200

    result = requests.post(f"{url}auth/passwordreset/request/v1", json={'email': get_user(user2['auth_user_id'])['email']})
    assert result.status_code == 200

#* Test that for an unregistered email, it raises an InputError (response 400)
def test_http_auth_passwordreset_invalid_email():
    requests.delete(f"{url}clear/v1")
    result = requests.post(f"{url}auth/passwordreset/request/v1", json={'email': 'CorrectFormat@asd.com'})
    assert result.status_code == 400

    result = requests.post(f"{url}auth/passwordreset/request/v1", json={'email': 'NotAnEmail'})
    assert result.status_code == 400

#* Test that if the reset password is less than 6 characters long, it raises an InputError (response 400)
def test_http_auth_passwordreset_invalid_reset(user1, user2):
    result = requests.post(f"{url}auth/passwordreset/reset/v1", json={'reset_code': -1, 'new_password': 'badpw'})
    assert result.status_code == 400
