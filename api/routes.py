#server
from flask import current_app, request, render_template, Response, jsonify, Blueprint
from sejong_univ_auth import ClassicSession, auth
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import os
import json
import redis
from .db import db, User

main = Blueprint('main', __name__)

jwt_redis_blocklist = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)
jwt_redis_refresh = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db=1, decode_responses=True)

@main.route("/")
def index():
    return render_template("index.html")

#user info: token
@main.route("/user", methods=['GET'])
@jwt_required()
def get_userinfo():
    jti = get_jwt()['jti']
    if jwt_redis_blocklist.exists(jti): #만료된 토큰의 접근 차단
        return jsonify(msg='Token has expired'), 401
    
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user:
        user_info = {'id': user.id,
                'name': user.name,
                'major': user.major,
                'grade': user.grade,
                'status': user.status,
                'read_certification': json.loads(user.read_certification)}
        return jsonify(user_info), 200
    else:
        return jsonify({'error':'user not found'}), 404

'''
#user info: user_id parameter
@main.route("/user/<string:user_id>", methods=['GET'])
def get_userinfo(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user_info = {'id': user.id,
                'name': user.name,
                'major': user.major,
                'grade': user.grade,
                'status': user.status,
                'read_certification': json.loads(user.read_certification)}
        print(user_info)
        return jsonify(user_info), 200
    else:
        return jsonify({'error':'user not found'}), 404
'''

#login
@main.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    uid = data.get('id')  
    upw = data.get('pw')
    #auth(id: str, password: str, methods: Authenticator)
    result = auth(id=uid, password=upw, methods=ClassicSession)
    if result.is_auth:  #oauth login success
        user_info = {'id': uid,
                    'name': result.body['name'],
                    'major': result.body['major'],
                    'grade': result.body['grade'],
                    'status': result.body['status'],
                    'read_certification': result.body['read_certification']}
        record = User.query.filter_by(id=uid).first()
        if not record:
            user = User(uid, user_info['name'], user_info['major'], user_info['grade'], user_info['status'], user_info['read_certification'])
            db.session.add(user)
            db.session.commit()
        access_token = create_access_token(identity=uid)
#        refresh_token = create_refresh_token(identity=uid)
#        jwt_redis_refresh.set(refresh_token, uid, ex=timedelta(days=int(os.getenv('REFRESH_EXPIRES'))))
#        return jsonify({'user':user_info, 'access_token':access_token, 'refresh_token':refresh_token}), result.status_code
        return jsonify({'user':user_info, 'access_token':access_token}), result.status_code
    else: #login fail
        return Response(result.code, 401)

#logout
@main.route("/logout", methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    access_expires = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    if not jwt_redis_blocklist.exists(jti):
        jwt_redis_blocklist.set(jti, "", ex=access_expires)
    return jsonify(msg='Token revoked'), 200
    #else

#chat
@main.route("/chat")
@jwt_required()
def chat():
    jti = get_jwt()['jti']
    if jwt_redis_blocklist.exists(jti): #만료된 토큰 접근 차단
        return jsonify(msg='Unauthorized'), 401
    return 200

'''
#refresh token 
@main.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token, 'user': user_id}), 200
'''