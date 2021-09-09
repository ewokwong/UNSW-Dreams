from src.error import InputError
import re
from src.other import decode, check_session, get_user, data_load
import json
import urllib.request
import requests
from PIL import Image
from src.config import url



def user_profile_v2(token, u_id):
    """ Provided the u_id of an existing user with a valid token, returns information about the user 
        which corresponds with the u_id

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            u_id (int): The user_id of the user whose profile is being returned

        Exceptions:
            InputError : occurs when the inputted u_id does not correspond to a valid user
            AccessError : occurs when the session_id or u_id provided within the token does not 
                          correspond to a valid u_id and session_id
            
        Return Value:
            Returns (dict) containing the information of the user which corresponds to the provided u_id
            The information provided is the user_id, email, first name, last name and handle string of the user 

    """ 

    decode(token)

    return {
        'user': get_user(u_id)
    }

def user_setname_v2(token, name_first, name_last):
    
    """ Provided with a valid token, the first and last names of the user corresponding to the payload of the token are
        changed to the provided first and last name

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            name_first (str): The new first name of the user
            name_last (str): The new last name of the user

        Exceptions:
            InputError : occurs when the inputted first name has a length that is not between 1 and 50 
                         characters inclusively
            InputError : occurs when the inputted last name has a length that is not between 1 and 50 
                         characters inclusively
            AccessError : occurs when the session_id or u_id provided within the token does not 
                          correspond to a valid u_id and session_id
            
        Return Value:
            Returns an empty dictionary 

    """ 
    auth_user_id, _ = decode(token)
    
    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError
        
    data = data_load()

    for user in data['users']:
        if auth_user_id == user['u_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {
    }

def user_setemail_v2(token, email):
    """ Provided with a valid token, the email of the user corresponding to the payload of the token is
        changed to the provided email

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            email (str): The new email of the user
        

        Exceptions:
            InputError : occurs when the inputted email is not a valid email format
            InputError : occurs when the inputted email has already been used by another user
            AccessError : occurs when the session_id or u_id provided within the token does not 
                          correspond to a valid u_id and session_id
            
        Return Value:
            Returns an empty dictionary 

    """ 
    auth_user_id, _ = decode(token)
    
    if not re.search('^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$', email):
        raise InputError

    data = data_load()

    for user in data['users']:
        if email == user['email']:
            raise InputError
            
    for user in data['users']:
        if auth_user_id == user['u_id']:
            user['email'] = email

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
             
    return {
    }

def user_sethandle_v2(token, handle_str):
    """ Provided with a valid token, the handle string of the user corresponding to the payload of the token is
        changed to the provided handle string

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            handle_str (str): The new handle string of the user
        

        Exceptions:
            InputError : occurs when the inputted handle string has a length that is not between 3 and 20 
                         characters inclusively
            InputError : occurs when the inputted handle string has already been used by another user
            AccessError : occurs when the session_id or u_id provided within the token does not 
                          correspond to a valid u_id and session_id
            
        Return Value:
            Returns an empty dictionary 

    """ 
    auth_user_id, _ = decode(token)

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError

    data = data_load()
    
    for user in data['users']:
        if handle_str == user['handle_str']:
            raise InputError
            
    for user in data['users']:
        if auth_user_id == user['u_id']:
            user['handle_str'] = handle_str

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
            
    return {
    }

def users_all(token):
    """ Provided with a valid token, returns a list containing information on all registered users

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
        
        Exceptions:
            None

        Return Value:
            Returns (dict) containing a list of all users which contains dictionaries of information on each user
            The information provided is the user_id, email, first name, last name and handle string of each user 

    """ 
    decode(token)
    
    user_list = []
    data = data_load()

    for user in data['users']:
        if user['permission_id'] != 0:
            user_list.append(get_user(user['u_id']))
        
    return { 'users': user_list
    
    }

def user_stats_v1(token):

    '''
    Fetches the required statistics about this user's use of UNSW Dreams. The statistics are time-series data types for:
    - The number of channels the user is a part of
    - The number of DMs the user is a part of
    - The number of messages the user has sent.

    This will also include the involvement rate of the user 

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function

        Return Values:
            returns a dictionary containing user_stats which includes the user's statistics for which are:
            - The number of channels the user is a part of
            - The number of DMs the user is a part of
            - The number of messages the user has sent.
            This will also include the involvement rate of the user which is defined by this pseudocode: 
            sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_dreams_channels, num_dreams_dms, num_dreams_msgs)
    '''
    auth_user_id, _ = decode(token)

    data = data_load()

    userstat = data["user_analytics"][f"{auth_user_id}"].copy()

    userInvolvement = (userstat["channels_joined"][-1]["num_channels_joined"],userstat["dms_joined"][-1]["num_dms_joined"],userstat["messages_sent"][-1]["num_messages_sent"])
    dreamsNumbers = (len(data["channels"]), len(data["dms"]), len(data["messages_log"]))

    involvementRate = sum(userInvolvement)/sum(dreamsNumbers)

    userstat.update({"involvement_rate": involvementRate})

    return {
        "user_stats": userstat
    }

def users_stats_v1(token):
    
    '''
    Fetches the required statistics about the use of UNSW Dreams, The statistics are time-series data types for:
    - The number of channels that exist currently
    - The number of DMs that exist currently
    - The number of messages that exist currently.

    This will also include the utilization rate of Dreams

        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function

        Return Values:
            returns a dictionary containing dreams_stats which includes some statistics for which are:
            - The number of channels that exist currently
            - The number of DMs that exist currently
            - The number of messages that exist currently.
            This will also include the utilization rate which is defined by this pseudocode: 
            num_users_who_have_joined_at_least_one_channel_or_dm / total_num_users
    '''
    decode(token)

    active_users = {}
    data = data_load()

    for channel in data['channels']:
        for member in channel['all_members']:
            if member not in active_users:
                active_users[member] = 1

    for dm in data['dms']:
        for member in dm['all_members']:
            if member not in active_users:
                active_users[member] = 1

    num_active_users = len(active_users)
    num_users = len(data['users'])
    utilization_rate = num_active_users / num_users
    dream_stats = data['dreams_analytics'].copy()
    dream_stats.update({'utilization_rate': utilization_rate})
    
    return { 
        "dreams_stats": dream_stats
    }

def user_profile_uploadphoto_v1(token, img_url,x_start,y_start,x_end,y_end):
    
    ''' 
    Given an img url from the internet and the starting coordinates and ending coordinates of the image's pixel,
    crops the img and uploads it as the user's new profile picture.
        Arguments:
            token (str): The token containing the user_id and session_id of user that called the function
            img_url (str): the img_url of the desired profile photo to upload

        Exceptions:
            InputError : img_url returns an HTTP status other than 200.
            InputError : any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
            InputError : Image uploaded is not a JPG
            
        Return Value:
            Returns an empty dictionary 
    '''

    auth_user_id, _ = decode(token)

    # Fetch image via URL
    try:  
        requests.get(img_url).status_code
    except Exception as e:
        raise InputError from e

    image_formats = ("image/jpeg", "image/jpg")
    if requests.head(img_url).headers["content-type"] not in image_formats:
        raise InputError
        
    urllib.request.urlretrieve(img_url, f"src/static/{auth_user_id}.jpg")

    # Cropping image
    imageObject = Image.open(f"src/static/{auth_user_id}.jpg")

    width, height = imageObject.size

    if x_end < x_start or y_end < y_start:
        raise InputError

    if x_start < 0 or y_start < 0 or  x_start > width or  y_start > height:
        raise InputError
    elif x_end < 0 or y_end < 0 or  x_end > width or  y_end > height:
        raise InputError
    
    imageObject.crop((x_start, y_start, x_end, y_end)).save(f"src/static/{auth_user_id}.jpg")

    # Serving image
    data = data_load()

    for user in data['users']:
        if user['u_id'] == auth_user_id:
            user['profile_img_url'] = f"{url}static/{auth_user_id}.jpg"

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {}
