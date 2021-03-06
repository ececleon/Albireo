# -*- coding: utf-8 -*-
from flask import request, Blueprint

from utils.exceptions import ClientError
from utils.http import json_resp
import json
from service.user import UserCredential
from flask_login import login_user, logout_user, login_required, fresh_login_required, current_user
from service.auth import auth_user
from domain.User import User


user_api = Blueprint('user', __name__)

@user_api.route('/login', methods=['POST'])
def login():
    '''
    login a user
    :return: response
    '''
    content = request.get_data(True, as_text=True)
    login_data = json.loads(content)
    if ('name' in login_data) and ('password' in login_data):
        name = login_data['name']
        password = login_data['password']
        remember = login_data['remember'] if 'remember' in login_data else False
        credential = UserCredential.login_user(name, password)
        login_user(credential, remember=remember)
        return json_resp({'msg': 'OK'})
    else:
        raise ClientError(ClientError.INVALID_REQUEST)


@user_api.route('/logout', methods=['POST'])
@login_required
def logout():
    '''
    logout a user
    :return: response
    '''
    logout_user()
    return json_resp({'msg': 'ok'})


@user_api.route('/register', methods=['POST'])
def register():
    '''
    register a new user using invite code, note that a newly registered user is not administrator, you need to
    use an admin user to promote it
    :return: response
    '''
    content = request.get_data(True, as_text=True)
    register_data = json.loads(content)
    if ('name' in register_data) and ('password' in register_data) and ('password_repeat' in register_data) and ('invite_code' in register_data):
        name = register_data['name']
        password = register_data['password']
        password_repeat = register_data['password_repeat']
        invite_code = register_data['invite_code']
        if password != password_repeat:
            raise ClientError(ClientError.PASSWORD_MISMATCH)
        if UserCredential.register_user(name, password, invite_code):
            return json_resp({'msg': 'OK'})
    else:
        raise ClientError(ClientError.INVALID_REQUEST)


@user_api.route('/update_pass', methods=['POST'])
@fresh_login_required
def update_pass():
    '''
    update a user password, the original password is needed
    :return: response
    '''
    content = request.get_data(True, as_text=True)
    user_data = json.loads(content)
    if ('new_password' in user_data) and ('new_password_repeat' in user_data) and ('password' in user_data):
        if(user_data['new_password'] != user_data['new_password_repeat']):
            raise ClientError('password not match')
        current_user.update_password(user_data['password'], user_data['new_password'])

        return logout()


@user_api.route('/reset_pass', methods=['POST'])
def reset_pass():
    '''
    reset a user password, invite_code is required
    :return:
    '''
    content = request.get_data(True, as_text=True)
    user_data = json.loads(content)
    if ('name' in user_data) and ('password' in user_data) and ('password_repeat' in user_data) and ('invite_code' in user_data):
        name = user_data['name']
        password = user_data['password']
        password_repeat = user_data['password_repeat']
        invite_code = user_data['invite_code']
        if password != password_repeat:
            raise ClientError('password not match')
        if UserCredential.reset_pass(name, password, invite_code):
            return json_resp({'msg': 'OK'})
    else:
        raise ClientError('invalid parameters')

@user_api.route('/promote_user', methods=['POST'])
@fresh_login_required
@auth_user(User.LEVEL_SUPER_USER)
def promote_user():
    '''
    promote user as administrator
    :return: response
    '''
    pass


@user_api.route('/info', methods=['GET'])
@login_required
def get_user_info():
    '''
    get current user name and level
    :return: response
    '''
    user_info = {}
    user_info['name'] = current_user.name
    user_info['level'] = current_user.level
    return json_resp({'data': user_info})
