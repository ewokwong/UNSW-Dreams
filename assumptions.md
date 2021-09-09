#########################################################################################
###                                                                                   ###
###                                    Assumptions                                    ###
###                                                                                   ###
#########################################################################################

#########################################################################################
###                                                                                   ###
###  W13B Cactus - Ethan Kwong, Jeffrey Meng, Nicholas Lam, Nicholas Liu, Vincent Le  ###
###                 z5308489     z5311921      z5310204      z5310207      z5310000   ###
###                                                                                   ###
#########################################################################################

|---------------------------------------------------------------------------------------|
|------------------------------------- Iteration One -----------------------------------|
|---------------------------------------------------------------------------------------|

In src/auth.py,
    For auth_register_v1:
        - Apart from "@" and " ", all characters can be in valid names
            e.g.      "Kim Jong-un"        is a valid name
                        "Ja'mie"           is a valid name
                 "Shai Gildrous-Alexander" is also a valid name
                       "X Æ A-12"          is also a valid name
        - Aside from the length of the password is greater than 5, no other requirements 
          for a valid password
        - Apart from "@" and " ", all characters may appear in handle strings
    For auth_login_v1:
        - Nothing much

In src/channel.py,
    For channel_messages_v1:
        - messages_send_v1 has been properly implemented 
           (even though we still in iteration one)
    For channel_invite_v1:
        - Regardless of it is a private or public channel, as long as the authorised user
           (i.e. the user inviting) is in the channel, the invitee will join the channel
        - If the invitee is already in the channel, then nothing happens 
           (i.e. no Exception raised, or anything printed out)
    For channel_details_v1:
        - Only prints out public details of a channel (see more in channel_join_v1)
           (i.e. ignores passwords of users in the channel)
    For channel_join_v1:
        - Assumes that the id being entered is of a member that isn't already in the 
          channel

In src/channels.py,
    For channels_create_v1:
        - At this stage, can't delete a channel from the database
        - The user who creates the channel automatically joins it and becomes the
          owner member
    For channels_list_v1:
        - If the list is empty, you don't return an empty dictionary inside the list
    For channels_listall_v1:
        - If the list is empty, you don't return an empty dictionary inside the list

|---------------------------------------------------------------------------------------|
|------------------------------------- Iteration Two -----------------------------------|
|---------------------------------------------------------------------------------------|

***      NOTE: All assumptions from Iteration One carries on to this iteration        ***

For persistence,


In src/admin.py,
    For admin/user/remove/v1:
        - A removed user cannot be removed again
        - Removed users cannot access any routes
        - Removed users' u_id's are kept in the data (i.e. doesn't remove the u_ids)
    For admin/userpermission/change/v1:
        - The user permission can only strictly be 1 or 2 and not anything else
        - i.e. user permission cannot changed to 0 through this (i.e. removed user)
        - You can change the permission of the original *Dreams* Owner

In src/auth.py,
    For auth/login/v2:
        - N/A
    For auth/register/v2:
        - N/A
    For auth/logout/v1:
        - Can't log out if you haven't logged in
    For auth/passwordreset/request/v1:
        - No time limit for the reset code
        - When you request multiple times, only the most recent is valid
    For auth/passwordreset/reset/v1:
        - You can reset the old password to an identical new password
        - Reset code is type int
        - When resetting a password, all sessions of the user are invalidated

In src/channel.py,
    For channel/invite/v2:
        - You cannot invite removed users
    For channel/details/v2:
        - N/A 
    For channel/messages/v2:
        - The value of start denotes how many messages we skipped starting from the most 
          recent message
    For channel/join/v2:
        - *Dreams* Owners can join private servers
    For channel/addowner/v1:
        - You can add an owner who's already not a member of a channel
            --> Non-member owner will be automatically invited into the channel
    For channel/removeowner/v1:
        - N/A
    For channel/leave/v1:
        - If you are the only owner, you cannot leave

In src/channels.py,
    For channels/list/v2:
        - N/A
    For channels/listall/v2:
        - Returns all channels including channels that are private
    For channels/create/v2:
        - N/A

In src/dm.py,
    For dm/details/v1:
        - The output with key 'members' orders the dictionary in the other in which they 
          are added to the dm with the creator being listed first
    For dm/list/v1:
        - N/A
    For dm/create/v1:
        - The first dm in the data always has dm_id 0
        - Every dm_id afterwards would come in increments of the previous data
        - The name of the dm is only autogenerated when created
            --> Doesn't change when you add/remove members
        - The creator of the dm must at least direct it to one other user
            --> The list of members cannot be empty & cannot include creator
        - Able to create multiple dms with same members + same name
            --> Only the dm_ids will be different
    For dm/remove/v1:
        - Rest of dms retain the same dm_ids when a dm is removed
    For dm/invite/v1:
        - Do not need to add new user into dm_name
        - Can't invite users who are already in the dm
    For dm/leave/v1:
        - Name of the dm doesn't change when the user leave
        - The owner of the dm cannot leave (nothing happens)
    For dm/messages/v1:
        - The value of start denotes how many messages we skipped starting from the most 
          recent message

In src/message.py,
    For message/send/v2:
        - You can send an empty message, but cannot edit a message into an empty string
    For message/edit/v2:
        - Everytime a message that mentions people is edited, it pops notifications for
          everyone mentioned in the post-edited version, even if they've already been 
          mentioned already
    For message/remove/v1:
        - Data for that message is completely removed without any traces
        - message_id for a removed message is never re-used for a new message
    For message/share/v1:
        - Assumes that channel_id and dm_id cannot be -1 simultaneously
    For message/senddm/v1:
        - An invalid dm_id raise an input error
    For message/sendlater/v1 and message/senddmlater/v1:
        - Uncapped time for a message sent later
        - Cannot cancel a message sent for later
        - Can still tag
        - The message can still be editted, removed etc.
    For message/react/v1:
        - The only react ID that is valid is 1: Thumbs up
    For message/unreact/v1:
        - The only react ID that is valid is 1: Thumbs up and that notification for initial react will not be deleted when message is unreacted to

In src/notifications.py,
    For notifications/get/v1:
        - N/A

In src/other.py,
    For clear/v1:
        - The data is completely cleared empty lists for every data structure
    For search/v2:
        - The query string is not case-sensitive
            --> e.g. "jOE bIDEN" would return messages "Joe Biden", "joE BidEn", etc.

In src/user.py,
    For user/profile/v2:
        - N/A
    For user/profile/setname/v2:
        - You cannot change the name of a removed user
    For user/profile/setemail/v2:
        - You cannot change the email of a removed user
    For user/profile/sethandle/v1:
        - You cannot change the handle of a removed user
    For users/all/v1:
        - Removed users are still in the list
        - Anyone can call this route aside from removed users
    For user/stats/v1 and users/stats/v1:
        - Removed users do not affect the calculations of the time-series data and rates
        - Stats only commence when the first user registers into the Dream
        - No negative stats
    For user/uploadphoto/v1:
        - Does not accept local jpgs and only takes jpgs from http urls
        - The resolution of the image does not matter
        - If the coordinates of the start and end of the crop are switched, raises InputError
        - Can reupload same photo

In src/standup.py
    For standup/start/v1:
        - A stand-up has no time restrictions
        - The stand-up message sent at the end can still be editted, removed etc.
    For standup/active/v1:
        - Cannot be interrupted once it is active
        - Authorised user does not have to be in channel to call standup_active and see details of channel
    For standup/send/v1:
        - Can tag people in the stand-up message and a notification will still be sent
        - Notification is sent from the person who started the stand-up
        - Normal channel messages cannot be sent during this time
