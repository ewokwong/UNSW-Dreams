import jwt
import json
from src.error import AccessError, InputError
from random import getrandbits
import os

AuID      = 'auth_user_id'
uID       = 'u_id'
cID       = 'channel_id'
creatorID = 'creator_id'
allMems   = 'all_members'
Name      = 'name'
fName     = 'name_first'
lName     = 'name_last'
chans     = 'channels'
handle    = 'handle_str'
dmID      = 'dm_id'
seshID    = 'session_id'
SECRET    = 'MENG'

def clear_v1():
    '''
    Clears the entire database

    Arguments: 
        None
    
    Exceptions:
        None

    Return value:
        None
    '''
    with open('data.json', 'w') as FILE:
        json.dump({
            'users': [],
            'channels': [],
            'dms': [],
            'messages_log': [],
            'notifs': {},
            'user_analytics': {},
            'stand_ups': [],
            'reset_codes': []
        }, FILE)

def search_v1(token, query_str):
    '''
    Takes in a user's token and query string to return a list of messages that contains details about the message
    The search is not case-sensitive

    Arguments: 
        token      (str) - The JWT containing user_id and session_id of the user that is to view their notifs
        querty_str (str) - The string which the user inputted to find messages
    
    Exceptions:
        InputError - Occurs when the query_str is greater than 1000 characters

    Return value:
        Returns a dictionary containing a list of notifications with key 'messages'
            Contains:
                message_id,
                user_id,
                message string, and
                time_created.
    '''
    #* Decode the token
    auth_user_id, _ = decode(token)

    # When query_str is >1000 characters, InputError is raised
    if len(query_str) > 1000:
        raise InputError

    data = data_load()

    channelList = []
    #* Check which channels the user is in
    for channel in data['channels']:
        if auth_user_id in channel[allMems]:
            channelList.append(channel[cID])
    
    DMList = []
    #* Check which DMs the user is in
    for dm in data['dms']:
        if auth_user_id in dm[allMems]:
            DMList.append(dm['dm_id'])

    messages = []
    #* Add in every message in the channel/DM that contains query_str
    for message in data['messages_log']:
        if (message[cID] in channelList or message['dm_id'] in DMList) and query_str.lower() in message['message'].lower():
            messages.append(
                {
                    'message_id': message['message_id'],
                    uID: message[uID],
                    'message': message['message'],
                    'time_created': message['time_created'],
                }
            )

    return {
        'messages': messages,
    }

########################################################################################
###                                                                                  ###
###                              Helper Functions below                              ###
###                                                                                  ###
########################################################################################

def decode(token):
    payload = jwt.decode(token, SECRET, algorithms='HS256')
    auth_user_id, session_id = payload.get('user_id'), payload.get('session_id')
    check_session(auth_user_id, session_id)
    return auth_user_id, session_id

def check_session(auth_user_id, session_id):
    data = data_load()

    for user in data['users']:
        if auth_user_id == user[uID] and user['permission_id'] != 0:
            if session_id in user['session_id']:
                return
    raise AccessError

def get_channel(channel_id):
    data = data_load()

    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            with open('data.json', 'w') as FILE:
                json.dump(data, FILE)
            return channel
    raise InputError

def get_user(user_id):
    data = data_load()

    for user in data['users']:
        if user_id == user[uID]:
            return {
                uID: user[uID],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url'],
            }
    raise InputError

def message_count(channel_id, dm_id):
    counter = 0
    data = data_load()

    if dm_id == -1:
        for message in data['messages_log']:
            if channel_id == message[cID]:
                counter += 1
    else:
        for message in data['messages_log']:
            if dm_id == message[dmID]:
                counter += 1
    
    return counter

def get_user_permissions(user_id):
    data = data_load()

    for user in data['users']:
        if user_id == user[uID]:
            return user['permission_id']
    # raise InputError

def get_user_from_handlestring(handlestring):
    data = data_load()

    for user in data['users']:
        if handlestring == user['handle_str']:
            return {
                uID: user[uID],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url'],
            }
    # raise InputError

def get_message(message_id):
    data = data_load()

    for message in data['messages_log']:
        if message_id == message['message_id']:
            return message
    raise InputError

def get_dm(dm_id):
    data = data_load()

    for dm in data['dms']:
        if dm_id == dm['dm_id']:
            return dm
    raise InputError

def push_tagged_notifications(auth_user_id, channel_id, dm_id, message):
    taggerHandle = get_user(auth_user_id)['handle_str']
    if channel_id != -1:
        channelDMname = get_channel(channel_id)['name']
    else:
        channelDMname = get_dm(dm_id)['name']
    messageWords = message.split()
    atHandlesList = []
    for word in messageWords:
        if word.startswith('@') and word != '@':
            atHandlesList.append(word[1:])
    taggedUsersList = []
    for atHandle in atHandlesList:
        try:
            if channel_id != -1:
                if get_user_from_handlestring(atHandle)[uID] in get_channel(channel_id)[allMems]:
                    taggedUsersList.append(get_user_from_handlestring(atHandle)[uID])
            else:
                if get_user_from_handlestring(atHandle)[uID] in get_dm(dm_id)[allMems]:
                    taggedUsersList.append(get_user_from_handlestring(atHandle)[uID])
        except:
            pass
    notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': f"{taggerHandle} tagged you in {channelDMname}: {message[0:20]}"
    }
    data = data_load()
    for taggedUser in taggedUsersList:
        data['notifs'][f"{taggedUser}"].insert(0, notification)

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

def push_added_notifications(auth_user_id, user_id, channel_id, dm_id):
    taggerHandle = get_user(auth_user_id)['handle_str']
    if channel_id != -1:
        channelDMname = get_channel(channel_id)['name']
    else:
        channelDMname = get_dm(dm_id)['name']
    get_user(user_id)       # Checking if user_id is valid
    notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': f"{taggerHandle} added you to {channelDMname}"
    }
    data = data_load()
    data['notifs'][f"{user_id}"].insert(0, notification)
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
        
def push_reacted_notifications(auth_user_id, user_id, channel_id, dm_id):
    users_handle = get_user(auth_user_id)['handle_str']
    if channel_id != -1:
        channelDMname = get_channel(channel_id)['name']
    else:
        channelDMname = get_dm(dm_id)['name']
    #Checking if user_id is valid
    get_user(user_id)
    notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': f"{users_handle} reacted to your message in {channelDMname}",
    }
    data = data_load()
    data['notifs'][f"{user_id}"].insert(0, notification)
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
        

def check_removed(u_id):
    data = data_load()
    for user in data["users"]:
        if user["u_id"] == u_id:
            if user['permission_id'] == 0:
                raise InputError
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

def generate_new_message_id():
    newID = getrandbits(32)
    status = False
    while not status:
        try:
            get_message(newID)
            newID = getrandbits(32)
        except:
            status = True
    return newID

def generate_reset_code():
    reset_code = getrandbits(32)
    return reset_code

def get_reset_code(email):
    data = data_load()

    for code in data['reset_codes']:
        if code['email'] == email:
            return code['reset_code']

def data_load():
    while True:
        try:
            with open('data.json', 'r') as FILE:
                data = json.load(FILE)
            return data
        except:
            pass