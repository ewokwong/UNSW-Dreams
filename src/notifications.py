from src.other import decode, data_load
import json

def notifications_get_v1(token):
    '''
    Takes in a user's token and gets the user's 20 most recent notifications

    Arguments: 
        token  (str) - The JWT containing user_id and session_id of the user that is to view their notifs
    
    Exceptions:
        InputError - Occurs when the user id doesn't belong to any user
        AccessError - Occurs when the user's token contains wrong session id

    Return value:
        Returns a dictionary containing a list of notifications with key 'notifications'
    '''
    #* Decode the taken and get the auth user's id
    auth_user_id, _ = decode(token)

    data = data_load()
    print(data_load()['notifs'][f"{auth_user_id}"])
    notifications = data['notifs'][f"{auth_user_id}"][0:20]

    return {
        'notifications': notifications
    }
