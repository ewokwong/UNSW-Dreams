from datetime import datetime
from src.error import AccessError, InputError
import re
from jwt import encode
import json
from src.other import SECRET, generate_reset_code, get_user, decode, data_load
import hashlib
from datetime import datetime
import urllib.request
from src.config import url
from flask_mail import Message

def auth_register_v1(email, password, name_first, name_last):
    """ With the inputted data (email, password, name_first, name_last), checks whether the format of the data are valid. 
        If the data is valid, inserts (registers) the inputted information into a dictionary containing all users information
        and appends that information onto the user data list. Also creates a formatted handlestring which consists of the users first and last name which has a maximum character length 
        of 20 characters unless there are duplicates. 

        Arguments:
            email (str): The email of the user
            password (str): The password of the user
            name_first (str): The first name of the user
            name_last (str): The last name of the user 

        Exceptions:
            InputError : occurs when the inputted email is not a valid email format
            InputError : occurs when the inputted email has already been used to register another user
            InputError : occurs when the inputted password has a length less than 6 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters

        Return Value:
            Returns (dict) containing user_id corresponding to the inputted email, password, name_first and name_last

    """
    data = data_load()

    #** Storing name_first & name_list so original names 
    #** unaffected by handle generation
    nameF = name_first
    nameL = name_last

    #* setting all characters to lowercase
    name_first = name_first.lower()
    name_last = name_last.lower()

    #* removing whitespace from name_first and name_last
    name_first = name_first.split()
    name_first = ''.join(name_first)
    name_last = name_last.split()
    name_last = ''.join(name_last)
    
    #* removing the '@' from name_first and name_last
    name_first = name_first.replace("@", "")
    name_last = name_last.replace("@", "")
    
    #* checking if inputted email is valid
    if re.search('^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$', email):
        pass    
    else: 
        raise InputError

    #* checking if inputted email is already being used by another user
    for user in data['users']:
        if email == user['email']:
            raise InputError

    #* checking if password is valid 
    if len(password) < 6:
        raise InputError        

    #* checking if first_name ranges between 1 - 50
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError

    #* checking if last_name ranges between 1 - 50
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError

    #* constructing the handlestring from first and last name     
    #* checking for total length of first and last name 
    if len(name_first) > 20:
        handle_string = name_first[0:21]
        
    elif len(name_first) + len(name_last) > 20:
        cutoff_len = 20 - len(name_first)
        handle_string = name_first + name_last[0:cutoff_len]
    else:    
        handle_string = name_first + name_last
    
    if check_handle(handle_string):
    
        trailing_int = 0 
        
        #* checking for duplicated names and appends the handle_string
        #* with the smallest number
        for user in data['users']:
            if check_handle(handle_string + str(trailing_int)):
                trailing_int += 1
        
        handle_string = handle_string + str(trailing_int)

    #* sets the user_id as the length of the users list
    user_id = len(data['users'])

    #* sets the permission_id to 2 which denotes a member 
    #* for the first member of Dreams, their permission_id is set 
    #* to 1 which denotes an owner
    permissionID = 2
    if len(data['users']) == 0:
        permissionID = 1
        data['dreams_analytics'] = {
            'channels_exist': [
                {
                    'num_channels_exist': 0,
                    'time_stamp': int(datetime.now().strftime("%s"))
                },
            ],
            'dms_exist': [
                {
                    'num_dms_exist': 0,
                    'time_stamp': int(datetime.now().strftime("%s"))
                },
            ],
            'messages_exist': [
                {
                    'num_messages_exist': 0,
                    'time_stamp': int(datetime.now().strftime("%s"))
                },
            ],
        }

    #* appending the user dictionary into the users list
    data['users'].append({
        'email' : email,
        'password' : hashlib.sha256(password.encode()).hexdigest(),
        'name_first' : nameF,
        'name_last' : nameL,
        'u_id' : user_id,
        'handle_str' : handle_string,
        'permission_id': permissionID,
        'session_id': [0],
        'profile_img_url': f"{url}static/default.jpg",
    })

    
    #* create an empty notification list
    data['notifs'][f"{user_id}"] = [] 

    now = datetime.now()
    time_created = int(now.strftime("%s"))
    #* create an empty user_analytics
    data['user_analytics'][f"{user_id}"] = {
        "channels_joined" : [
            {
                "num_channels_joined" : 0,
                "time_stamp" : time_created
            }
        ],
        "dms_joined" : [
            {
                "num_dms_joined" : 0,
                "time_stamp" : time_created
            }
        ],
        "messages_sent" : [
            {
                "num_messages_sent" : 0,
                "time_stamp" : time_created
            }
        ]
    }

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {
        'auth_user_id': user_id
    }

def check_handle(handle_string):
    """ Checks if inputted handle string is already being used by another registered user 

        Arguments:
            handle_string (str): The handle string of the user

        Exceptions:
            None

        Return Value:
            Returns (bool) depending on whether the provided handle string is already in use
                - true if in use 
                - false if not in use

    """ 
    data = data_load()
    for user in data['users']:
        if handle_string == user['handle_str']:
            return True
    return False

def auth_login_v2(email, password): 
    """ Checks if inputted email is present within the registered users
        If email is present, checks that the inputted password matches the password stored for 
        that particular registered email. 

        Arguments:
            email (str): The email of the user
            password (str): The password of the user

        Exceptions:
            InputError : occurs when the inputted email isn't present within the registered users
            InputError : occurs when the inputted password does not match the password stored for that particular inputted email

        Return Value:
            Returns (dict) containing user_id corresponding to the inputted email and password 

    """ 
    data = data_load()
    for user in data['users']:
        if email == user.get('email') and hashlib.sha256(password.encode()).hexdigest() == user.get('password'):
            if len(user['session_id']) != 0: 
                new_session_id = user['session_id'][-1] + 1
            else:
                new_session_id = 0
                
            user['session_id'].append(new_session_id)
            token = encode({'session_id': new_session_id, 'user_id': user['u_id']}, SECRET, algorithm='HS256')

            with open('data.json', 'w') as FILE:
                json.dump(data, FILE)

            return {
                'token': token,
                'auth_user_id': user['u_id'],
            }

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    raise InputError    

def auth_register_v2(email, password, name_first, name_last):
    """ This function is a wrapper for auth_register_v1. With the return value of auth_register_v1, a token containing
        a payload of the session id and user id is created.

        Arguments:
            email (str): The email of the user
            password (str): The password of the user
            name_first (str): The first name of the user
            name_last (str): The last name of the user 

        Exceptions:
            InputError : occurs when the inputted email is not a valid email format
            InputError : occurs when the inputted email has already been used to register another user
            InputError : occurs when the inputted password has a length less than 6 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters

        Return Value:
            Returns (dict) containing auth_user_id and token corresponding to the 
            inputted email, password, name_first and name_last 

    """
    data_structure = auth_register_v1(email, password, name_first, name_last)
    auth_user_id = data_structure['auth_user_id']
    token = encode({'session_id': 0, 'user_id': auth_user_id}, SECRET, algorithm='HS256')

    return {
        'token': token,
        'auth_user_id': auth_user_id
    }

def auth_logout_v1(token):
    """ 
        Provided a valid token, logs out the corresponding user session (invalidates session id and token) 

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            
        Exceptions:

        Return Value:
            Returns (dict) containing an 'is_success' key which contains true when the provided token 
            has been successfully logged out otherwise false

    """
    auth_user_id, session_id = decode(token)

    data = data_load()
    for user in data['users']:
        if user['u_id'] == auth_user_id:
            if session_id in user['session_id']:
                user['session_id'].remove(session_id)
                with open('data.json', 'w') as FILE:
                    json.dump(data, FILE)
                return {'is_success': True}

def auth_passwordreset_request_v1(email):
    '''
    Provided an email that matches a registered user's email, sends and email containing a password reset code

    Arguments:
        email (str): Email of the user trying to reset their password

    Exceptions:
        InputError : Raised if inputted email does not match a registered user's email

    Return Value:
        Upon sucess, returns the message to be sent in the email
    '''
    data = data_load()
    for user in data['users']:
        if user['email'] == email:
            reset_code = generate_reset_code()
            msg = Message('UNSW Dreams Password Reset', sender = 'W13BCactus@gmail.com', recipients = [f"{email}"])
            msg.body = f"We've received your request for a password reset. Please use the following code to reset your password: \n {reset_code}"
            for index, code in enumerate(data['reset_codes']):
                if user['email'] == code['email']:
                    data['reset_codes'].pop(index)
            data['reset_codes'].append({
                'email': user['email'],
                'reset_code': reset_code
            })
            with open('data.json', 'w') as FILE:
                json.dump(data, FILE)
            return msg
    raise InputError

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Provided a valid reset code, changes the corresponding user's password to new_password

    Arguments:
        reset_code (int): Reset code provided to the user's email
        new_password (str): New password of the user

    Exceptions:
        InputError : Raised if reset code is invalid
        InputError : Raised if new_password has a length less than 6 characters

    Return Value:
        Upon sucess, returns an empty dictionary
    '''
    if len(new_password) < 6:
        raise InputError
    
    data = data_load()
    for index, code in enumerate(data['reset_codes']):
        if reset_code == code['reset_code']:
            data['reset_codes'].pop(index)
            for user in data['users']:
                if user['email'] == code['email']:
                    user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
                    user['session_id'] = []
                    with open('data.json', 'w') as FILE:
                        json.dump(data, FILE)
                    return {}
    raise InputError
