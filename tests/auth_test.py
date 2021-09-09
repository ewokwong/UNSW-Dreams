# File to test functions in src/auth.py
from src.error import AccessError, InputError
import pytest
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.user import user_profile_v2
import src.channel, src.channels
from src.other import clear_v1, SECRET, check_session, get_user, get_reset_code
from jwt import encode
from src.config import url

# tests the return value of the auth login of a valid user
def test_auth_login_valid():
    clear_v1()
    auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token, 'auth_user_id': 0,}

# tests the return value of the auth login of multiple valid users
def test_auth_login_valid_multiple():
    clear_v1()
    auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    token1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    auth_register_v2("ericamondy@gmail.com", "1234567", "erica", "mondy") 
    token2 = encode({'session_id': 1, 'user_id': 1}, SECRET, algorithm='HS256')

    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token1, 'auth_user_id': 0,}  
    assert auth_login_v2("ericamondy@gmail.com", "1234567") == {'token': token2, 'auth_user_id': 1,}

# tests the session ids contained within the payload of the token returned when auth login 
# is called by the same user multiple times
def test_auth_login_valid_sessions():
    clear_v1()
    auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    token1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')    
    token2 = encode({'session_id': 2, 'user_id': 0}, SECRET, algorithm='HS256')

    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token1, 'auth_user_id': 0,}  
    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token2, 'auth_user_id': 0,}

# tests the session ids contained within the payload of the token returned when auth login 
# is called by the same user multiple times by multiple users
def test_auth_login_valid_multiple_sessions():
    clear_v1()
    auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    token1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    token2 = encode({'session_id': 2, 'user_id': 0}, SECRET, algorithm='HS256')

    auth_register_v2("ericamondy@gmail.com", "1234567", "erica", "mondy") 
    token3 = encode({'session_id': 1, 'user_id': 1}, SECRET, algorithm='HS256')
    token4 = encode({'session_id': 2, 'user_id': 1}, SECRET, algorithm='HS256')

    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token1, 'auth_user_id': 0,}  
    assert auth_login_v2("caricoleman@gmail.com", "1234567") == {'token': token2, 'auth_user_id': 0,}
    assert auth_login_v2("ericamondy@gmail.com", "1234567") == {'token': token3, 'auth_user_id': 1,}
    assert auth_login_v2("ericamondy@gmail.com", "1234567") == {'token': token4, 'auth_user_id': 1,}

# tests the case when the inputted email is of invalid format
def test_auth_login_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
        auth_login_v2("caricoleman.com", "1234567")

# tests the case when the inputted email does not correspond to a registerd user
def test_auth_login_invalid_not_registered_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
        auth_login_v2("caricolema@gmail.com", "1234567") 
        auth_login_v2("ericamondy@gmail.com", "1234567")  

# tests the case when there are no users registered and a auth_login is attempted to be called
def test_auth_login_invalid_empty():
    clear_v1()
    with pytest.raises(InputError):        
        auth_login_v2("caricolema@gmail.com", "1234567") 

# tests the case when the inputted password does not match the password of the user corresponding to 
# the inputted email
def test_auth_login_invalid_incorrect_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
        auth_login_v2("caricoleman@gmail.com", "12345")

# tests the return value of an auth_register with valid input (email, password, first name, last name)
def test_auth_register_valid():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman") == {'token': token, 'auth_user_id': 0,}

# tests the return value of an auth_register with valid input (email, password, first name, last name) for
# multiple users
def test_auth_register_valid_multiple():
    clear_v1()
    token1 = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    token2 = encode({'session_id': 0, 'user_id': 1}, SECRET, algorithm='HS256')
    token3 = encode({'session_id': 0, 'user_id': 2}, SECRET, algorithm='HS256')
    token4 = encode({'session_id': 0, 'user_id': 3}, SECRET, algorithm='HS256')
    token5 = encode({'session_id': 0, 'user_id': 4}, SECRET, algorithm='HS256')
    
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman") == {'token': token1, 'auth_user_id': 0,}
    assert auth_register_v2("ericamondy@gmail.com", "1234567", "erica", "mondy") == {'token': token2, 'auth_user_id': 1,}
    assert auth_register_v2("hilarybently@gmail.com", "1234567", "hilary", "bently") == {'token': token3, 'auth_user_id': 2,}
    assert auth_register_v2("kentonwatkins@gmail.com", "1234567", "kenton", "watkins") == {'token': token4, 'auth_user_id': 3,}
    assert auth_register_v2("claudiamarley@gmail.com", "1234567", "claudia", "marley") == {'token': token5, 'auth_user_id': 4,}    

# tests the handle string of users that have identical first and last name (identical handle strings)
def test_auth_register_valid_same_name():
    clear_v1()
    token1 = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    token2 = encode({'session_id': 0, 'user_id': 1}, SECRET, algorithm='HS256')
    
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman") == {'token': token1, 'auth_user_id': 0,}
    assert auth_register_v2("caricoleman@hotmail.com", "1234567", "cari", "coleman") == {'token': token2, 'auth_user_id': 1,}

    assert user_profile_v2(token2, 1) == { 
        'user':
            {
            'u_id': 1, 
            'email': "caricoleman@hotmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman0',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

    assert user_profile_v2(token1, 0) == { 
        'user':
            {
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests the handle string of users that have identical first and last name (identical handle strings) 
# for multiple users 
def test_auth_register_valid_same_name_multiple():
    clear_v1()
    token1 = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    token2 = encode({'session_id': 0, 'user_id': 1}, SECRET, algorithm='HS256')
    token3 = encode({'session_id': 0, 'user_id': 2}, SECRET, algorithm='HS256')
    token4 = encode({'session_id': 0, 'user_id': 3}, SECRET, algorithm='HS256')
    
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman") == {'token': token1, 'auth_user_id': 0,}
    assert auth_register_v2("caricoleman@hotmail.com", "1234567", "cari", "coleman") == {'token': token2, 'auth_user_id': 1,}
    assert auth_register_v2("caricoleman@yahoo.com", "1234567", "cari", "coleman") == {'token': token3, 'auth_user_id': 2,}
    assert auth_register_v2("caricoleman@bing.com", "1234567", "cari", "coleman") == {'token': token4, 'auth_user_id': 3,}

# tests the handle string of the user when the first and last names of the user are capatilised
def test_auth_register_valid_front_capatilised():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "Cari", "Coleman") == {'token': token, 'auth_user_id': 0, }

# tests the handle string of the user when the first and last names of the user contain capatilised characters     
def test_auth_register_valid_random_capatilised():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "CaRi", "coLemaN") == {'token': token, 'auth_user_id': 0, }

# tests the handle string of the user when the first and last names of the user contains white space
def test_auth_register_valid_whitespace():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", " cari", "coleman ") == {'token': token, 'auth_user_id': 0, }

# tests the handle string of the user when the first and last names of the user contains the '@' symbol
def test_auth_register_valid_at_symbol():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari@", "coleman") == {'token': token, 'auth_user_id': 0, }

# tests the handle string of the user when the total amount of characters in the first and last name exceed the 20 character limit
def test_auth_register_valid_long_name():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cariiiiiiiiiiiiiii", "coleman") == {'token': token, 'auth_user_id': 0,}
    
    assert user_profile_v2(token, 0) == { 
        'user':
            {
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cariiiiiiiiiiiiiii', 
            'name_last': 'coleman', 
            'handle_str': 'cariiiiiiiiiiiiiiico',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests the handle string of the user when the amount of characters in the first name exceed the 20 character limit
def test_auth_register_valid_long_first_name():
    clear_v1()
    token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cariiiiiiiiiiiiiiiiiii", "coleman") == {'token': token, 'auth_user_id': 0,}

    assert user_profile_v2(token, 0) == { 
        'user':
            {
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cariiiiiiiiiiiiiiiiiii', 
            'name_last': 'coleman', 
            'handle_str': 'cariiiiiiiiiiiiiiiiii',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests the handle string of the user when the total amount of characters in the first and last name exceed the 20 character limit
# for multiple users with the same first and last names
def test_auth_register_valid_long_name_multiple():
    clear_v1()
    token1 = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
    token2 = encode({'session_id': 0, 'user_id': 1}, SECRET, algorithm='HS256')
    
    assert auth_register_v2("caricoleman@gmail.com", "1234567", "cariiiiiiiiiiiiiii", "coleman") == {'token': token1, 'auth_user_id': 0, }
    assert auth_register_v2("caricoleman@hotmail.com", "1234567", "cariiiiiiiiiiiiiii", "coleman") == {'token': token2, 'auth_user_id': 1, }

    assert user_profile_v2(token1, 0) == { 
        'user':
            {
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cariiiiiiiiiiiiiii', 
            'name_last': 'coleman', 
            'handle_str': 'cariiiiiiiiiiiiiiico',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

    assert user_profile_v2(token2, 1) == { 
        'user':
            {
            'u_id': 1, 
            'email': "caricoleman@hotmail.com", 
            'name_first': 'cariiiiiiiiiiiiiii', 
            'name_last': 'coleman', 
            'handle_str': 'cariiiiiiiiiiiiiiico0',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests the case when the inputted email is of invalid format 
def test_auth_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman.com", "1234567", "cari", "coleman") 

# tests the case when the inputted email is already used by a registered user  
def test_auth_register_invalid_same_email():
    clear_v1()
    with pytest.raises(InputError):
        token = encode({'session_id': 0, 'user_id': 0}, SECRET, algorithm='HS256')
        assert auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman") == {'token': token, 'auth_user_id': 0,}
        auth_register_v2("caricoleman@gmail.com", "1234567", "erica", "mondy")

# tests the case when the inputted password has less than 6 characters
def test_auth_register_invalid_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234", "cari", "coleman") 

# tests the case when the inputted first name exceeds the 50 character limit
def test_auth_register_invalid_long_first_name():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cariiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", "coleman") 

# tests the case when the inputted last name exceeds the 50 character limit
def test_auth_register_invalid_long_last_name():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "colemaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaan") 

# tests the case when the inputted first name is empty
def test_auth_register_invalid_no_first_name():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "", "coleman") 

# tests the case when the inputted last name is empty
def test_auth_register_invalid_no_last_name():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "") 

# tests for the existence of session ids and validity of tokens after a logout is called by a user
def test_auth_logout_v1_valid():
    clear_v1()
    user_data_1 = auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    token_1 = user_data_1['token']
    user_data_2 = auth_login_v2("caricoleman@gmail.com", "1234567")
    token_2 = user_data_2['token']
    auth_login_v2("caricoleman@gmail.com", "1234567")
    user_data_2['token']
    
    assert auth_logout_v1(token_1) == {'is_success': True}
    
    with pytest.raises(AccessError):
        check_session(user_data_1['auth_user_id'], 0)

    assert auth_logout_v1(token_2) == {'is_success': True}
    
    with pytest.raises(AccessError):
        check_session(user_data_1['auth_user_id'], 1)

# tests for the case when a token with an invalid session_id is inputted
def test_auth_logout_v1_invalid():    
    clear_v1()
    with pytest.raises(AccessError):
        user_data_1 = auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
        auth_logout_v1(user_data_1['token'])
        auth_logout_v1(user_data_1['token'])
def test_auth_passwordreset_request():
    clear_v1()
    #* Test for the case when email passed in doesn't correspond to any known user
    with pytest.raises(InputError):
        auth_passwordreset_request_v1("InvalidEmail")

    user1 = auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    auth_passwordreset_request_v1(get_user(user1['auth_user_id'])['email'])
    #* Test that a reset code exists for the registered email
    assert get_reset_code(get_user(user1['auth_user_id'])['email']) is not None

#* Test that when reseting multiple times, a new code is generated every time and invalidates old one
def test_auth_passwordreset_request_multiple():
    clear_v1()
    user1 = auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    
    auth_passwordreset_request_v1(get_user(user1['auth_user_id'])['email'])
    code1 = get_reset_code(get_user(user1['auth_user_id'])['email'])

    auth_passwordreset_request_v1(get_user(user1['auth_user_id'])['email'])
    code2 = get_reset_code(get_user(user1['auth_user_id'])['email'])

    assert code1 != code2

def test_auth_passwordreset_reset():
    clear_v1()
    #* Test that an invalid reset code raises an InputError
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(-1, "newpassword")

    user1 = auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")
    user2 = auth_register_v2("ericamondy@gmail.com", "1234567", "erica", "mondy")
    
    auth_passwordreset_request_v1(get_user(user1['auth_user_id'])['email'])
    auth_passwordreset_request_v1(get_user(user2['auth_user_id'])['email'])

    reset = get_reset_code(get_user(user2['auth_user_id'])['email'])
    #* Test that an invalid password raises an InputError
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(reset, "short")
    
    new_password = 'CrocodileLikesStrawberries'

    auth_passwordreset_reset_v1(reset, new_password)
    auth_login_v2(get_user(user2['auth_user_id'])['email'], new_password)