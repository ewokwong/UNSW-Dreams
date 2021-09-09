from src.error import AccessError, InputError
import src.auth
from src.other import decode, get_channel, get_user, get_dm, get_user_permissions, push_tagged_notifications, push_reacted_notifications, generate_new_message_id, data_load
from datetime import timezone, datetime
import json
import threading, time
from random import getrandbits
from src.user import users_stats_v1

AuID      = 'auth_user_id'
uID       = 'u_id'
cID       = 'channel_id'
creatorID = 'creator_id'
allMems   = 'all_members'
Name      = 'name'
fName     = 'name_first'
lName     = 'name_last'
chans     = 'channels'
handle    = 'handle_string'
dmID      = 'dm_id'
seshID    = 'session_id'
mID       = 'message_id'
rID       = 'react_id'
thumbsUp  = 1 

def message_send_v1(token, channel_id, message):
    '''
    Takes in a user's token, a channel's id and a string and sends a message 
    from that user into the channel.
    --> Note: Messages cannot be more 1000 chars

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int) - The id of the channel that the message is being sent to
        message      (str) - The string of the message being sent

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The channel_id doesn't belong to any channel
                            3) The message is too long (exceeds 1000 chars)
        AccessError - Occurs when:
                            1) When the user's token contains wrong session id
                            2) The token doesn't belong to a member of the channel

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    # Decode the token
    auth_user_id, _ = decode(token)

    # If the message is too long, raise InputError
    if len(message) > 1000:
        raise InputError

    # Check if user is in channel
    if auth_user_id not in get_channel(channel_id)['all_members']:
        raise AccessError

    now = datetime.now()
    time_created = int(now.strftime("%s"))
    newID = generate_new_message_id()

    data = data_load()

    # User is in the channel (which exists) & message is appropriate length
    #* Time to send a message
    data['messages_log'].append(
        {
            'channel_id'    : channel_id,
            'dm_id'         : -1,
            'u_id'          : get_user(auth_user_id)['u_id'],
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

    return {
        'message_id': newID,
    }

def message_remove_v1(token, message_id):
    '''
    Takes in a user's token and a message's id and removes that message.

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to remove the message
        message_id   (int) - The id of the message that is to be removed

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The message_id doesn't belong to any message
        AccessError - Occurs when:
                            1) When the user's token contains wrong session id
                            2) The token doesn't belong to a member of the channel
                            3) The token doesn't belong to an owner of the channel
                            4) The token doesn't belong to an owner of *Dreams*

    Return Value:
        Returns an empty dictionary
    '''
    #* Decode the token
    auth_user_id, _ = decode(token)

    data = data_load()

    #* Get message dictionary in data
    messageFound = False
    i = 0
    while not messageFound:
        if i >= len(data['messages_log']):
            raise InputError
        if data['messages_log'][i]['message_id'] == message_id:
            messageFound = True
        i += 1

    i -= 1              # Remove extra increment

    if data['messages_log'][i][cID] != -1:
        #* If message is in a channel
        #* Check if the user is the writer, channel owner or owner of Dreams
        # Get the channel the message belongs to
        channel = get_channel(data['messages_log'][i]['channel_id'])
        if auth_user_id is not data['messages_log'][i]['u_id'] and auth_user_id not in channel['owner_members'] and get_user_permissions(auth_user_id) != 1:
            raise AccessError
    else:
        if auth_user_id is not data['messages_log'][i]['u_id'] and get_user_permissions(auth_user_id) != 1:
            raise AccessError

    #* Remove the message
    data['messages_log'].remove(data['messages_log'][i])

    updated_num_message = data['dreams_analytics']['messages_exist'][-1]['num_messages_exist'] - 1
    data['dreams_analytics']['messages_exist'].append({
        'num_messages_exist': updated_num_message,
        'time_stamp': int(datetime.now().strftime("%s"))
    })
    #* update analytics
    messageSentPrev = data["user_analytics"][f"{auth_user_id}"]['messages_sent'][-1]["num_messages_sent"]
    data["user_analytics"][f"{auth_user_id}"]['messages_sent'].append(
        {
            "num_messages_sent": messageSentPrev - 1,
            "time_stamp": int(datetime.now().strftime("%s"))
        }
    )
    
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    return {
    }

def message_edit_v1(token, message_id, message):
    '''
    Takes in a user's token, a message's id and message string 
    and replaces the message with the message string.
        --> Note: When the message is an empty string, the message is removed

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to edit the message
        message_id   (int) - The id of the message that is to be removed
        message      (str) - The string for the message that will replace the old message

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The message_id doesn't belong to any message
        AccessError - Occurs when:
                            1) When the user's token contains wrong session id
                            2) The token doesn't belong to a member of the channel
                            3) The token doesn't belong to an owner of the channel
                            4) The token doesn't belong to an owner of *Dreams*

    Return Value:
        Returns an empty dictionary
    '''
    #* Decode the token
    auth_user_id, _ = decode(token)

    data = data_load()

    #* Get message dictionary in data
    messageFound = False
    i = 0
    while not messageFound:
        if i >= len(data['messages_log']):
            raise InputError
        elif data['messages_log'][i]['message_id'] == message_id:
            messageFound = True
        i += 1

    i -= 1          # Undo extra increment

    #* Check if the user is the writer, channel owner or owner of Dreams
    # Get the channel the message belongs to
    if data['messages_log'][i][cID] != -1:
        channel = get_channel(data['messages_log'][i]['channel_id'])
        if auth_user_id is not data['messages_log'][i]['u_id'] and auth_user_id not in channel['owner_members'] and get_user_permissions(auth_user_id) != 1:
            raise AccessError
    else:
        get_dm(data['messages_log'][i]['dm_id'])
        if auth_user_id is not data['messages_log'][i]['u_id']:
            raise AccessError

    if len(message) > 1000:  # If the message is too long, raise InputError
        raise InputError
    elif message == '':      #* If new message is empty string --> remove message
        data['messages_log'].remove(data['messages_log'][i])
        with open('data.json', 'w') as FILE:
            json.dump(data, FILE)
        return {
        }
    else:                       # Else 
        data['messages_log'][i]['message'] = message
    
    with open('data.json', 'w') as FILE:
        json.dump(data, FILE)

    if data['messages_log'][i]['channel_id'] != -1:     #* If message is in a channel
        push_tagged_notifications(auth_user_id, data['messages_log'][i]['channel_id'], -1, message)
    else:
        push_tagged_notifications(auth_user_id, -1, data['messages_log'][i]['dm_id'], message)

    return {
    }

def message_senddm_v1(token, dm_id, message):
    '''
    Takes in a user's token, a dm_id and a string and sends a message 
    from that user into the dm.
    --> Note: Messages cannot be more 1000 chars

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is sending the message
        dm_id        (int) - The id of the dm that the message is being sent to
        message      (str) - The string of the message being sent

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The dm_id doesn't belong to any dm
                            3) The message is too long (exceeds 1000 chars)
        AccessError - Occurs when:
                            1) When the user's token is invalid
                            2) The token doesn't belong to a member of the dm

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    auth_user_id, _ = decode(token)
    dmMembers = get_dm(dm_id)[allMems]
    if auth_user_id not in dmMembers:
        raise AccessError
    if len(message) > 1000:
        raise InputError
    message_id = generate_new_message_id()
    
    data = data_load()

    now = datetime.now()
    time_created = int(now.strftime("%s"))
    
    data['messages_log'].append({
        cID: -1,
        dmID: dm_id,
        'message_id': message_id,
        uID: auth_user_id,
        'message': message, 
        'time_created': time_created,
        'reacts': [],
        'is_pinned': False
    })

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

    push_tagged_notifications(auth_user_id, -1, dm_id, message)
    return {
        'message_id': message_id,
    }

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    message_share_v1 searches for an existing message id to be forwarded or shared to either
    a channel or a DM. There is also an option to append a extra message when the message is shared.
    
    Arguments:
        token (str)- JWT containing { u_id, session_id }
        og_message_id (int) - The id of the desired message in message log
        message (str) - An optional message to be sent when message is shared, it is '' if empty.
        channel_id (int) - The id of the desired channel for message to be shared, it is -1 if message is shared to a DM instead
        dm_id (int) - The id of the desired DM for message to be shared, it is -1 if message is shared to a channel instead
    Exceptions:
        AccessError - Raised when the token does not belong to a user who is authorised, eg. the user has not joined the channel or DM they are sharing to.
    
    Return Value:
        Dictionary with a shared_message_id : (int)
    '''
    auth_user_id, _ = decode(token)

    data = data_load()
    # put message with optional message first,
    newMessage = ''
    for msg in data['messages_log']:
        if msg["message_id"] == og_message_id:
            if message != '':
                newMessage = msg["message"] + " | " + message
            else:
                newMessage = msg["message"] 
    # Use both message/send and message/senddm to share message
    if dm_id == -1:
        for chans in data['channels']:
            if chans["channel_id"] == channel_id:
                userAuth = False
                for users in chans["all_members"]:
                    if users == auth_user_id:
                        userAuth = True
                if not userAuth:
                    raise AccessError
        with open('data.json', 'w') as FILE:
            json.dump(data, FILE)
        shared_message_id = message_send_v1(token, channel_id, newMessage)
        
    if channel_id == -1:
        for dm in data['dms']:
            if dm['dm_id'] == dm_id:
                userAuth = False
                for users in dm['all_members']:
                    if users == auth_user_id:
                        userAuth = True
                if not userAuth:
                    raise AccessError
        with open('data.json', 'w') as FILE:
            json.dump(data, FILE)
        shared_message_id = message_senddm_v1(token, dm_id, newMessage)
        
    if dm_id == -1:
        push_tagged_notifications(auth_user_id, channel_id, -1, newMessage)
    elif channel_id == -1: 
        push_tagged_notifications(auth_user_id, -1, dm_id, newMessage)

    return {"shared_message_id" : shared_message_id["message_id"]}

def message_pin_v1(token, message_id):
    auth_user_id, _ = decode(token)
    data = data_load()

    for message in data['messages_log']:
        if message[mID] == message_id:
            if message[dmID] == -1 and auth_user_id not in get_channel(message[cID])[allMems]:
                raise AccessError
            elif message[cID] == -1 and auth_user_id not in get_dm(message[dmID])[allMems]:
                raise AccessError
            elif message['is_pinned']:
                raise InputError
            else:
                message['is_pinned'] = True
                with open('data.json', 'w') as FILE:
                    json.dump(data, FILE)
                return {}
    raise InputError

def message_unpin_v1(token, message_id):
    auth_user_id, _ = decode(token)
    data = data_load()

    for message in data['messages_log']:
        if message[mID] == message_id:
            if message[dmID] == -1 and auth_user_id not in get_channel(message[cID])[allMems]:
                raise AccessError
            elif message[cID] == -1 and auth_user_id not in get_dm(message[dmID])[allMems]:
                raise AccessError
            elif not message['is_pinned']:
                raise InputError
            else:
                message['is_pinned'] = False
                with open('data.json', 'w') as FILE:
                    json.dump(data, FILE)
                return {}
    raise InputError

#Iteration 3    
def message_react_v1(token, message_id, react_id):
    '''
    For a given channel or DM, add a "react" to a particular message 
    NOTE: Assuming that the only react ID that is valid is 1: Thumbs up. 

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        message_id   (int) - The id of the message that the user wants to react to 
        react_id     (int) - The type of react to the message 

    Exceptions:
        InputError - Occurs when:
                            1) When message_id is not a valid message within a channel or DM that authorised user has joined 
                            2) react_id is not a valid React ID
                            3) Message with message_id already contains an active react with the same react_id from authorised user 
                            
        AccessError - Occurs when:
                            1) The authorised user is not a member of channel or DM that the message is in 

    Return Value:
        Returns an empty dictionary {}
    '''
    auth_user_id, _ = decode(token)
    data = data_load()
    
    if react_id != thumbsUp:
        raise InputError
        
    message_found = False 
    
    for message in data['messages_log']: 
        if message[mID] == message_id:
            #AccessError if user not a part of channel or DM
            if message[dmID] == -1 and auth_user_id not in get_channel(message[cID])[allMems]:
                raise AccessError
            elif message[cID] == -1 and auth_user_id not in get_dm(message[dmID])[allMems]:
                raise AccessError
            message_found = True 
            #Case 1: First react for that message 
            if len(message['reacts']) == 0:
                result = {
                    'react_id': react_id,
                    'u_ids': [auth_user_id],
                    'is_this_user_reacted': None,
                
                    }
                message['reacts'].append(result)
            #Case 2: Reacting to a message which already has a react
            elif len(message['reacts']) == 1:
                for current_react in message['reacts']:
                    if current_react[rID] == react_id: 
                        if auth_user_id in current_react['u_ids']:
                            raise InputError
                        else:
                            current_react['u_ids'].append(auth_user_id)
        
            with open('data.json', 'w') as FILE:
                json.dump(data, FILE)  
            #Now can push to notifs 
            #If message in channel 
            if message['channel_id'] != -1:  
                push_reacted_notifications(auth_user_id, message['u_id'], message[cID], -1)
            #If message is in DM
            else: 
                push_reacted_notifications(auth_user_id, message['u_id'], -1, message[dmID])
    
    #If gets to end of messages log without finding message with same mID then mID not valid  
    if message_found == False:
        raise InputError
    
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    For a given channel or DM, remove a "react" to a particular message 
    NOTE: Assuming that the only react ID that is valid is 1: Thumbs up and that notification for initial react will not be deleted 

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to send the message
        message_id   (int) - The id of the message that the user wants to react to 
        react_id     (int) - The type of react to the message 

    Exceptions:
        InputError - Occurs when:
                            1) When message_id is not a valid message within a channel or DM that authorised user has joined 
                            2) react_id is not a valid React ID
                            3) Message with message_id does not contain an active react with the same react_id from authorised user 
                            
        AccessError - Occurs when:
                            1) The authorised user is not a member of channel or DM that the message is in 

    Return Value:
        Returns an empty dictionary {}
    '''
    
    auth_user_id, _ = decode(token)
    data = data_load()
    
    if react_id != thumbsUp:
        raise InputError
            
    for message in data['messages_log']: 
        if message[mID] == message_id:
            #AccessError if user not a part of channel or DM
            if message[dmID] == -1 and auth_user_id not in get_channel(message[cID])[allMems]:
                raise AccessError
            elif message[cID] == -1 and auth_user_id not in get_dm(message[dmID])[allMems]:
                raise AccessError           
           
            #For unreact, delete the list with same react_id, if its not found then the message doesn't have a react and thus raises InputError
            for react in range(len(message['reacts'])):
                if message['reacts'][react]['react_id'] == react_id:
                    message['reacts'].pop(react)
                    with open('data.json', 'w') as FILE:
                        json.dump(data, FILE)     
                    return {} 
            
    #If gets to here means message not found or react not found 
    raise InputError
    
def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Takes in a user's token, a channel's id, a string and a unix timestamp
    and sends a message at that given unix timestamp from that user into the channel.
    --> Note: Messages cannot be more 1000 chars

    Arguments:
        token        (str)   - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int)   - The id of the channel that the message is being sent to
        message      (str)   - The string of the message being sent
        time_sent    (float) - The Unix Timestamp of which the message is to be sent

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The channel_id doesn't belong to any channel
                            3) The message is too long (exceeds 1000 chars)
                            4) The time_sent is actually in the past
        AccessError - Occurs when:
                            1) When the user's token contains wrong session id
                            2) The token doesn't belong to a member of the channel

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    # Decode the token
    auth_user_id, _ = decode(token)

    # If the message is too long, raise InputError
    if len(message) > 1000:
        raise InputError

    # Check if time_sent is in the past
    if time_sent < datetime.now().replace(tzinfo=timezone.utc).timestamp():
        raise InputError

    # Check if user is in channel
    if auth_user_id not in get_channel(channel_id)['all_members']:
        raise AccessError

    newID = generate_new_message_id()
    timeTillSend = time_sent - datetime.now().replace(tzinfo=timezone.utc).timestamp()
    newID = 0
    threading.Timer(timeTillSend, sendlater_send, args=(token, channel_id, message, time_sent, newID)).start()
    return {
        'message_id': newID
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Takes in a user's token, a dm's id, a string and a unix timestamp
    and sends a message at that given unix timestamp from that user into the channel.
    --> Note: Messages cannot be more 1000 chars

    Arguments:
        token        (str)   - The JWT containing user_id and session_id of the user that is to send the message
        dm_id        (int)   - The id of the dm that the message is being sent to
        message      (str)   - The string of the message being sent
        time_sent    (float) - The Unix Timestamp of which the message is to be sent

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user
                            2) The dm_id doesn't belong to any dm
                            3) The message is too long (exceeds 1000 chars)
                            4) The time_sent is actually in the past
        AccessError - Occurs when:
                            1) When the user's token contains wrong session id
                            2) The token doesn't belong to a member of the dm

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    # Decode the token
    auth_user_id, _ = decode(token)

    # If the message is too long, raise InputError
    if len(message) > 1000:
        raise InputError

    # Check if time_sent is in the past
    if time_sent < datetime.now().replace(tzinfo=timezone.utc).timestamp():
        raise InputError

    # Check if user is in channel
    if auth_user_id not in get_dm(dm_id)['all_members']:
        raise AccessError

    newID = generate_new_message_id()
    timeTillSend = time_sent - datetime.now().replace(tzinfo=timezone.utc).timestamp()
    newID = 0
    threading.Timer(timeTillSend, sendlaterdm_send, args=(token, dm_id, message, time_sent, newID)).start()
    return {
        'message_id': newID
    }

def sendlater_send(token, channel_id, message, time_sent, newID):
    '''
    HELPER FUNCTION FOR: message_sendlater_v1
    Takes in a user's token, a channel's id, a string, a unix timestamp and a new message ID
    and executes the actual sending of the message in message_sendlater_v1

    Arguments:
        token        (str)   - The JWT containing user_id and session_id of the user that is to send the message
        channel_id   (int)   - The id of the channel that the message is being sent to
        message      (str)   - The string of the message being sent
        time_sent    (float) - The Unix Timestamp of which the message is to be sent
        newID        (int)   - The new message ID of the message (already generated in message_sendlater_v1)

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    # Decode the token
    auth_user_id, _ = decode(token)

    data = data_load()

    # User is in the channel (which exists) & message is appropriate length
    #* Time to send a message
    data['messages_log'].append(
        {
            'channel_id'    : channel_id,
            'dm_id'         : -1,
            'u_id'          : auth_user_id,
            'time_created'  : time_sent,
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

def sendlaterdm_send(token, dm_id, message, time_sent, newID):
    '''
    HELPER FUNCTION FOR: message_sendlaterdm_v1
    Takes in a user's token, a dm's id, a string, a unix timestamp and a new message ID
    and executes the actual sending of the message in message_sendlaterdm_v1

    Arguments:
        token        (str)   - The JWT containing user_id and session_id of the user that is to send the message
        dm_id        (int)   - The id of the dm that the message is being sent to
        message      (str)   - The string of the message being sent
        time_sent    (float) - The Unix Timestamp of which the message is to be sent
        newID        (int)   - The new message ID of the message (already generated in message_sendlater_v1)

    Exceptions:
        InputError - Occurs when:
                            1) When the user id doesn't belong to any user

    Return Value:
        Returns a dictionary with key 'message_id' to the new message's message_id
    '''
    # Decode the token
    auth_user_id, _ = decode(token)

    data = data_load()

    # User is in the dm (which exists) & message is appropriate length
    #* Time to send a message
    data['messages_log'].append(
        {
            'channel_id'    : -1,
            'dm_id'         : dm_id,
            'u_id'          : auth_user_id,
            'time_created'  : time_sent,
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
    push_tagged_notifications(auth_user_id, -1, dm_id, message)
