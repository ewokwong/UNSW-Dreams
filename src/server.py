import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
import src.auth, src.admin, src.other, src.dm, src.notifications, src.channel, src.channels, src.message, src.user, src.standup
from flask_mail import Mail, Message

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)
mail= Mail(APP)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'W13BCactus@gmail.com'
APP.config['MAIL_PASSWORD'] = 'themarms'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    src.other.clear_v1()
    return {}

#* *********************************************AUTH ROUTES**************************************************
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    payload = request.get_json()
    return src.auth.auth_register_v2(payload['email'], payload['password'], payload['name_first'], payload['name_last'])

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    payload = request.get_json()
    return src.auth.auth_login_v2(payload['email'], payload['password'])

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    payload = request.get_json()
    return src.auth.auth_logout_v1(payload['token'])

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_password_reset_request():
    payload = request.get_json()
    mail.send(src.auth.auth_passwordreset_request_v1(payload['email']))
    return {}

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_password_reset_reset():
    payload = request.get_json()
    src.auth.auth_passwordreset_reset_v1(int(payload['reset_code']),payload['new_password'])
    return {}

#* *************************************************ADMIN ROUTES******************************************
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def userpermission_change():
    payload = request.get_json()
    return src.admin.userpermission_change_v1(payload.get('token'),payload.get('u_id'),payload.get('permission_id'))

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def user_remove():
    payload = request.get_json()
    return src.admin.user_remove_v1(payload.get('token'), payload.get('u_id'))

#* ****************************************************CHANNEL ROUTES***********************************************
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    payload = request.get_json()
    return src.channel.channel_join_v1(payload['token'], payload['channel_id'])

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    payload = request.get_json()
    return src.channel.channel_leave_v1(payload['token'], payload['channel_id'])

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    payload = request.get_json()
    return src.channel.channel_invite_v1(payload.get('token'), payload.get('channel_id'), payload.get('u_id'))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_detail():
    token, channel_id = request.args.get('token'), request.args.get('channel_id')
    return src.channel.channel_details_v1(token, int(channel_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token, channel_id, start = request.args.get('token'), request.args.get('channel_id'), request.args.get('start')
    return src.channel.channel_messages_v1(token, int(channel_id), int(start))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    payload = request.get_json()
    return src.channel.channel_addowner_v1(payload.get('token'), payload.get('channel_id'), payload.get('u_id'))
    
@APP.route("/channel/removeowner/v1", methods= ['POST'])
def channel_removeowner():
    payload = request.get_json()
    return src.channel.channel_removeowner_v1(payload.get('token'), payload.get('channel_id'), payload.get('u_id'))


#* ****************************************************CHANNELS ROUTES*********************************************
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    payload = request.get_json()
    return src.channels.channels_create_v1(payload['token'], payload['name'], payload['is_public'])

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    return src.channels.channels_list_v2(token)

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    return src.channels.channels_listall_v2(token)

#* ***************************************************MESSAGE ROUTES************************************************
@APP.route("/message/send/v2", methods=['POST'])
def message_send():
    payload = request.get_json()
    return src.message.message_send_v1(payload['token'], payload['channel_id'], payload['message'])

@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit():
    payload = request.get_json()
    return src.message.message_edit_v1(payload['token'], payload['message_id'], payload['message'])

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    payload = request.get_json()
    return src.message.message_remove_v1(payload['token'], payload['message_id'])

@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token')
    return src.notifications.notifications_get_v1(token)

@APP.route("/search/v2", methods=['GET'])
def search():
    token, query_str = request.args.get('token'), request.args.get('query_str')
    return src.other.search_v1(token, query_str)

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    payload = request.get_json()
    return src.message.message_share_v1(payload.get('token'), payload.get('og_message_id'), payload.get('message'), payload.get('channel_id'), payload.get('dm_id'))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    payload = request.get_json()
    return src.message.message_senddm_v1(payload['token'], payload['dm_id'], payload['message'])

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    payload = request.get_json()
    return src.message.message_sendlater_v1(payload['token'], payload['channel_id'], payload['message'], payload['time_sent'])

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    payload = request.get_json()
    return src.message.message_sendlaterdm_v1(payload['token'], payload['dm_id'], payload['message'], payload['time_sent'])
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    payload = request.get_json()
    return src.message.message_pin_v1(payload['token'], payload['message_id'])

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    payload = request.get_json()
    return src.message.message_unpin_v1(payload['token'], payload['message_id'])
    
@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    payload = request.get_json()
    return src.message.message_react_v1(payload['token'], payload['message_id'], payload['react_id'])
    
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    payload = request.get_json()
    return src.message.message_unreact_v1(payload['token'], payload['message_id'], payload['react_id'])
    

#* *********************************************DM ROUTES*****************************************
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token, dm_id = request.args.get('token'), request.args.get('dm_id')
    return src.dm.dm_details_v1(token, int(dm_id))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    return src.dm.dm_list_v1(token)

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    payload = request.get_json()
    return src.dm.dm_create_v1(payload.get('token'), payload.get('u_ids'))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    payload = request.get_json()
    return src.dm.dm_remove_v1(payload.get('token'), payload.get('dm_id'))

@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite():
    payload = request.get_json()
    return src.dm.dm_invite_v1(payload.get('token'), payload.get('dm_id'), payload.get('u_id'))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    payload = request.get_json()
    return src.dm.dm_leave_v1(payload.get('token'), payload.get('dm_id'))
    
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token, dm_id, start = request.args.get('token'), request.args.get('dm_id'), request.args.get('start')
    return src.dm.dm_messages_v1(token, int(dm_id), int(start))
    
    
    
#* ***************************************************STANDUP ROUTES***********************************************
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    payload = request.get_json()
    return src.standup.standup_start_v1(payload['token'], payload['channel_id'], payload['length'])

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token, channel_id = request.args.get('token'), request.args.get('channel_id')
    return src.standup.standup_active_v1(token, int(channel_id))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    payload = request.get_json()
    return src.standup.standup_send_v1(payload['token'], payload['channel_id'], payload['message'])

#* ***************************************************USER ROUTES***********************************************
@APP.route("/user/profile/v2", methods=['GET'])
def user_profile():
    token, u_id = request.args.get('token'), request.args.get('u_id')
    return src.user.user_profile_v2(token, int(u_id))

@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_setname():
    payload = request.get_json()
    return src.user.user_setname_v2(payload['token'], payload['name_first'], payload['name_last'])

@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_setemail():
    payload = request.get_json()
    print(payload['email'])
    print(payload['token'])
    return src.user.user_setemail_v2(payload['token'], payload['email'])

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle():
    payload = request.get_json()
    return src.user.user_sethandle_v2(payload['token'], payload['handle_str'])

@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')
    return src.user.users_all(token)

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    token = request.args.get('token')
    return src.user.users_stats_v1(token)
    
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    token = request.args.get('token')
    return src.user.user_stats_v1(token)

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_uploadphoto():
    payload = request.get_json()
    return src.user.user_profile_uploadphoto_v1(payload['token'], payload['img_url'],payload['x_start'],payload['y_start'],payload['x_end'],payload['y_end'])

@APP.route("/static/<path:path>")
def send_js(path):
    return send_from_directory('', path)
#* ------------------------------------------------------------------------------------

#* SERVER RUN
if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port
