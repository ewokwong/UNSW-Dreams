from src.error import AccessError, InputError
import jwt
import json
from src.other import decode, get_channel, get_user, get_user_permissions, check_removed, data_load


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


def user_remove_v1(token, u_id):

    get_user(u_id)

    data = data_load()

    dream_owner = 0
    for users in data['users']:
        if users['permission_id'] == 1:
            dream_owner += 1

    auth_user_id, _ = decode(token)

    if not get_user_permissions(auth_user_id) == 1:
        raise AccessError

    if dream_owner == 1 and get_user_permissions(u_id) == 1:   
        raise InputError
    
    for users in data['users']:
        if users['u_id'] == u_id:
            users['name_first'] = 'Removed '
            users['name_last'] = 'user'
            users['permission_id'] = 0

    for messages in data['messages_log']:
        if messages['u_id'] == u_id:
            messages['message'] = 'Removed user'

    for channel in data['channels']:
        if u_id in channel['all_members']:       
            channel['all_members'].remove(u_id)
        if u_id in channel['owner_members']:
            channel['owner_members'].remove(u_id)

    for dm in data['dms']:
        if u_id in dm['all_members']:       
            dm['all_members'].remove(u_id)
        if u_id == dm['creator_id']:
            dm['creator_id'] == []

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
    
    return {
    }

def userpermission_change_v1(token, u_id, permission_id):
    '''
    userpermission_change_v1 works when an authorised user (Dreams Owner) has the ability to change a user with u_id to grant or revoke
    their permissions by changing permission_id

    Arguments:
        token (str) - JWT containing { u_id, session_id }
        u_id (int) - The id of desired user we want to change permission of.
        permission_id (int) - The id of which we want to set the user's permission to, it is 1 for Dreams Owners and 2 for all other members.
    Exceptions:
        InputError - Raise when the u_id does not refer to a valid user, user does not exist
        InputError - Raised when an invalid permission_id is given, eg. not 1 or 2
        AccessError - Raised when the token does not belong to a Dreams owner with permission_id 1.
    
    Return Value:
        Empty dictionary
    '''

    data = data_load()
    auth_user_id, _ = decode(token)

    validUser = False
    validOwner = False
    for user in data['users']:
        if user[uID] == u_id:
            validUser = True
        if user[uID] == auth_user_id:
            if user['permission_id'] == 1:
                validOwner = True
    if not validOwner:
        raise AccessError
    if not validUser:
        raise InputError
    check_removed(u_id)

    if permission_id != 1 and permission_id != 2:
        raise InputError

    for user in data['users']:
        if user[uID] == u_id:
            user['permission_id'] = permission_id
    
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {
    }









