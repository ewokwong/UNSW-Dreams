from src.error import AccessError, InputError
from src.other import decode, get_channel, get_user, data_load
import json
import jwt
from datetime import datetime

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
allMems = 'all_members'
Name    = 'name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'
token   = 'token'

def channels_list_v2(token):
    '''
    Provides a list of all channels (and their associated details) that the authorised user is part of

    Arguments:
        token (str): JWT containing { u_id, session_id }

    Exceptions:
        AccessError - Raised when the token passed in is not valid

    Return Value:
        Returns dictionary of a list of channels mapped to the key string 'channels'
        Each channel is represented by a dictionary containing types { channel_id, name }
    '''
    auth_user_id, _ = decode(token)

    data = data_load()
    output = []
    for chanD in data['channels']:
        if auth_user_id in chanD['all_members']:
            channel = {}
            channel[cID] = chanD[cID]
            channel[Name] = chanD[Name]
            output.append(channel)

    return {
        'channels': output
    }

def channels_listall_v2(token):
    '''
    Provides a list of all channels (and their associated details)
    Channels are provided irrespective of whether the member is part of the channel
    Both public and private channels are provided

    Arguments:
        token (str): JWT containing { u_id, session_id }

    Exceptions:
        AccessError - Raised when the token passed in is not valid

    Return Value:
        Returns dictionary of a list of channels mapped to the key string 'channels'
        Each channel is represented by a dictionary containing types { channel_id, name }
    '''
    decode(token)
    
    data = data_load()
    output = []
    for d in data['channels']:
        channel = {}
        channel[cID] = d[cID]
        channel[Name] = d[Name]
        output.append(channel)
    return {
        'channels': output
    }

def channels_create_v1(token, name, is_public):
    '''
    Creates a channel and adds the user into that channel as both an owner and member

    Arguments:
        token               - The token id of the user that wants to create a channel
        name         (str)  - The name of the channel that the user wants to create, comes as one string
        is_public    (bool) - The boolean value of whether this channel is to be public or private
                                True  --> Channel is to be public
                                False --> Channel is to be private

    Exceptions:
        InputError  - Occurs when the intended length of the channel name is too long (21 chars or greater)
        AccessError - Occurs when the auth_user_id inputted does not belong to any user in the database

    Return Value:
        Returns a dictionary with the key being 'channel_id' and the value of the newly created channel's id
    '''
    auth_user_id, _ = decode(token)
    
    # Ensure an InputError when the channel name is 
    # more than 20 characters long
    if len(name) > 20:
        raise InputError

    data = data_load()
    # Time to find the user details
    userFound = False
    j = 0
    while not userFound:
        if data['users'][j][uID] == auth_user_id:
            userFound = True
        j += 1

    j -= 1      # Undo extra increment

    # Identify the new channel ID
    # Which is an increment of the most recent channel id
    if not len(data['channels']):
        newID = len(data['channels'])
    else:
        newID = data['channels'][-1][cID] + 1


    # Add this new channel into the channels data list
    # The only member is the auth user that created this channel
    data['channels'].append(
        {
            'channel_id': newID,
            'is_public': is_public,
            'name': name,
            'owner_members': [data['users'][j][uID]],
            'all_members': [data['users'][j][uID]],
        }
    )

    updated_num_channels = data['dreams_analytics']['channels_exist'][-1]['num_channels_exist'] + 1
    data['dreams_analytics']['channels_exist'].append({
        'num_channels_exist': updated_num_channels,
        'time_stamp': int(datetime.now().strftime("%s"))
    })
    
    #* update analytics

    channelsJoinedPrev = data["user_analytics"][f"{auth_user_id}"]['channels_joined'][-1]["num_channels_joined"]
    data["user_analytics"][f"{auth_user_id}"]['channels_joined'].append(
        {
            "num_channels_joined": channelsJoinedPrev + 1,
            "time_stamp": int(datetime.now().strftime("%s"))
        }
    )   

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    # Return a dictionary containing the new channel ID 
    return {
        'channel_id': newID,
    }
