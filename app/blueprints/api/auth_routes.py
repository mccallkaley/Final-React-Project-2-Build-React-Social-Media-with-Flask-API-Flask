from . import bp as api
from app.models import User
from app.blueprints.auth.auth import basic_auth, token_auth
from flask import g, make_response, request

@api.get('/token')
@basic_auth.login_required()
def get_token():
    user = g.current_user
    token = user.get_token()
    return make_response({"token":token},200)

# makes a user an Admin
# {"id":5}
@api.put('/admin')
@token_auth.login_required()
def make_admin():
    user_id_to_be_admin = request.get_json().get('id')
    if not user_id_to_be_admin:
        return make_response("Invalid payload", 400)
    if not g.current_user.is_admin:
        return make_response("This action requires Admin privs", 403)
    user = User.query.get(user_id_to_be_admin)
    if not user:
        return make_response("User does not exist!", 404)
    user.is_admin = True
    user.save()
    return make_response(f'{user.first_name} {user.last_name} is now an Admin', 200)

@api.get('/admin')
@token_auth.login_required()
def get_admin():
    return make_response({"isAdmin":g.current_user.is_admin or False}, 200)

