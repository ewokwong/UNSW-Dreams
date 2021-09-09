#File for implementation of standup functions 
from src.error import AccessError, InputError
from src.other import decode, get_channel, generate_new_message_id, get_user, data_load, push_tagged_notifications
from datetime import datetime
import json
import threading, time

AuID     = 'auth_user_id'
uID      = 'u_id'
cID      = 'channel_id'
chans    = 'channels'

def standup_start_v1(token, channel_id, length):
    '''
    For a given channel, begin a standup in which messages that are sent will be sent as one string at end of time specified 

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int) - The id of the channel that the standup is being started in
        length      (str) - The length in seconds of the startup 

    Exceptions:
        InputError - Occurs when:
                            1) When Channel ID is invalid 
                            2) An active standup is already running 

        AccessError - Occurs when:
                            1) When the authorised user is not in the channel 

    Return Value:
        Returns a dictionary with key 'time_finish' detailing the time that the standup will be finished 
    '''
    
    auth_user_id, _ = decode(token)
    #* If Channel ID is not a valid channel, then an InputError is raised
    #* If authorised user is not in the channel, an AccessError is raised
    if auth_user_id not in get_channel(channel_id)['all_members']:
        raise AccessError
    elif standup_active_v1(token, channel_id)['is_active']:
        raise InputError

    data = data_load()

    now = datetime.now()
    time_finish = int(now.strftime("%s")) + length

    new_stand_up = {
        'channel_id': channel_id,
        'time_finish': time_finish,
        'messages': []
    }
    data['stand_ups'].append(new_stand_up)
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)
    
    threading.Timer(length, stand_up_push, args=(auth_user_id, channel_id)).start()
    return {
        'time_finish': time_finish
    }

def standup_active_v1(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it or not and the time in which an active standup will be finished 
    NOTE: Assuming that authorised user does not have to be in channel to call standup_active

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int) - The id of the channel that user wants to look for a standup in 

    Exceptions:
        InputError - Occurs when:
                            1) When Channel ID is invalid 

    Return Value:
        Returns a dictionary with key 'is_active' detailing whether or not the standup is active and 'time_finish' detailing the time that the standup will be finished. 'time_finish' will return None if no standup is currently active 
    '''
    _, _ = decode(token)
    #* If Channel ID is not a valid channel, then an InputError is raised
    get_channel(channel_id)
    data = data_load()
    
    for stand_up in data['stand_ups']:
        if channel_id == stand_up[cID]:
            return {
                'is_active': True,
                'time_finish': stand_up['time_finish']
            }
    return {
            'is_active': False,
            'time_finish': None
        }

#* Append string with "handle: message" to stand_up messages
def standup_send_v1(token, channel_id, message):
    '''
    For a given channel, sends a message to a standup queue which will be appended to messages log as one string when standup is finished 

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int) - The id of the channel that user wants to look for a standup in 
        message      (str) - The string of the message being sent

    Exceptions:
        InputError - Occurs when:
                            1) When Channel ID is invalid 
                            2) Message is more than 1000 characters (not including username and colon)
                            3) There is no active standup in channel 
        AccessError - Occurs when:
                            1) Authorised user not a member of channel the standup is within 

    Return Value:
        Returns an empty dictionary {}
    '''
    auth_user_id, _ = decode(token)
    if auth_user_id not in get_channel(channel_id)['all_members']:
        raise AccessError
    elif not standup_active_v1(token, channel_id)['is_active']:
        raise InputError
    elif len(message) > 1000:
        raise InputError

    data = data_load()

    for stand_up in data['stand_ups']:
        if channel_id == stand_up[cID]:
            stand_up['messages'].append(f"{get_user(auth_user_id)['handle_str']}: {message}")

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {}

#* Function which is run at the end of the standup
#* Compiles messages into one big string
#* Removes the stand_up dictionary
def stand_up_push(auth_user_id, channel_id):
    '''
    For a given channel, the function which executes the associated standup functions once the thread for the standup is completed. This includes: compiling the messages queue into one string and removing the stand-up from the dictionary

    Arguments:
        auth_user_id        (int) - The ID of the authorised user
        channel_id   (int) - The id of the channel that user wants to look for a standup in

    Return Value:
        No return values
    '''
    data = data_load()

    message = ''
    for index, stand_up in enumerate(data['stand_ups']):
        if stand_up[cID] == channel_id:
            target = data['stand_ups'].pop(index)
            message = "\n".join(target['messages'])
    
    now = datetime.now()
    time_created = int(now.strftime("%s"))
    newID = generate_new_message_id()

    if message != '':
        data['messages_log'].append(
            {
                'channel_id'    : channel_id,
                'dm_id'         : -1,
                'u_id'          : auth_user_id,
                'time_created'  : time_created,
                'message_id'    : newID,
                'message'       : message,
                'reacts': [],
                'is_pinned': False,
            }
        )
        updated_num_message = data['dreams_analytics']['messages_exist'][-1]['num_messages_exist'] + 1
        data['dreams_analytics']['messages_exist'].append({
            'num_messages_exist': updated_num_message,
            'time_stamp': int(datetime.now().strftime("%s"))
        })
        #* update analytics
        messageSentPrev = data["user_analytics"][f"{auth_user_id}"]['messages_sent'][-1]["num_messages_sent"]
        data["user_analytics"][f"{auth_user_id}"]['messages_sent'].append(
            {
                "num_messages_sent": messageSentPrev + 1,
                "time_stamp": int(datetime.now().strftime("%s"))
            }
        )   

    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

        #* Push notifications if anyone is tagged
    push_tagged_notifications(auth_user_id, channel_id, -1, message)
