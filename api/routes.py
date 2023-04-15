#server
from flask import render_template, request, Response, jsonify, Blueprint
from sejong_univ_auth import ClassicSession, auth
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from .db import db, User
#from .model import answer

main = Blueprint('main', __name__)

#user info
@main.route("/user", methods=['GET'])
@jwt_required()
def get_userinfo():
    user_id = get_jwt_identity()
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

#login page
@main.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method =='POST':
        uid = request.form.get("id")
        upw = request.form.get("pw")
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
            print(access_token)
            return jsonify({"user":user_info, "access_token":access_token}), result.status_code
        else: #login fail
            return Response(result.code, 401)

'''
@main.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    token = request.args.get('access_token')
    #if success
    result = {'success': True, 
              'message': 'logout success'}
    return jsonify(result), 200
    #else

#chatbot page
@main.route("/chat")    
def chat():
    return

#predict test page
@main.route("/predict")
def test():
    return str(answer)

'''