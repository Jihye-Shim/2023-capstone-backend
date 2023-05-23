#server
from flask import current_app, request, render_template, Response, jsonify, Blueprint, send_file
from sejong_univ_auth import ClassicSession, auth
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import and_
from .db import db, User, Management, Button, ButtonRelation, Department, Facilities, UnivSchedule, Log
from .weather import weather
import os, json, redis, datetime, requests

main = Blueprint('main', __name__)

jwt_redis_blocklist = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)
jwt_redis_refresh = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db=1, decode_responses=True)


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

#test login
@main.route("/test/login", methods=['POST'])
def test():
    data = request.get_json()
    uid = data.get('id')  
    upw = data.get('pw')
    #auth(id: str, password: str, methods: Authenticator)
    from sejong_univ_auth import PortalSSOToken, DosejongSession
    result = {}
    result['ClassicSession'] = auth(id=uid, password=upw, methods=ClassicSession)
    #result['DosejongSession'] = auth(id=uid, password=upw, methods=DosejongSession)
    result['PortalSSOToken'] = auth(id=uid, password=upw, methods=PortalSSOToken)
    return jsonify(result)

#login
@main.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    uid = data.get('id')  
    upw = data.get('pw')
    #auth(id: str, password: str, methods: Authenticator)
    result = auth(id=uid, password=upw, methods=ClassicSession)
    print(result)
    print(result.body)
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

@main.route("/button/init", methods=['GET'])
@jwt_required()
def initbutton():
    btn_list = Button.query.filter(Button.btn_id.like("1%0%_001")).with_entities(Button.btn_id, Button.btn_title).all()
    d = dict(btn_list)
    if d:
        return jsonify(d), 200
    else:
        return jsonify({"msg": "button not found"}), 404

@main.route("/button/click/info", methods=['POST'])
@jwt_required()
def info_button():
    user_id = get_jwt_identity()
    data = request.get_json()
    select_btn = data.get("btn_title") # or btn_id
    btn = Button.query.filter_by(btn_title=select_btn).first()
    if not btn:
        return jsonify({"msg": "btn not found"}), 404
    btn_id = btn.btn_id
    sub = {}
    sub_list = ButtonRelation.query.filter_by(btn_id = btn_id).with_entities(ButtonRelation.sub_id).all()
    i = 1
    for list in sub_list:
        id = list[0]
        subbtn = Button.query.filter_by(btn_id = id).first()
        sub[i] = subbtn.btn_title
        i += 1
    input = btn.btn_message
    if btn_id[0] == "9" and btn_id[5:] != "000":
        dpt = Department.query.filter_by(department=btn.btn_title).first()
        if dpt is None:
            string = "학과 정보를 찾을 수 없습니다."
            return jsonify({"msg":string}), 404
        string = dpt.department + " 정보입니다.\n"
        string += "사무실: " + dpt.location + "\n"
        string += "연락처: " + dpt.tel_number + "\n"
        string += "학과 홈페이지: " + dpt.homepage + "\n"
        if dpt.abeek:
            string += "공학인증: " + dpt.abeek + "\n"
        string = string.rstrip("\n")
        output = string
    elif btn_id[3] == "5" and btn_id[5:] > "001":
        fclty = Facilities.query.filter_by(facilities=btn.btn_title).all()
        string = ""
        for f in fclty:
            string += "[" + f.name + "]" + "\n"
            string += "위치: " + f.location + "\n"
            if f.time:
                string = string.rstrip("\n")
                string += ", 운영시간: " + f.time + "\n"
        string = string.rstrip("\n")
        output = string
    elif btn.btn_title == "교내 지도":
        image_path = 'static/map.jpg'
        return send_file(image_path, mimetype='image/jpeg'), 200
    else:
        output = btn.btn_contents
    if len(sub_list) == 0:
        sub = None
        result = {"input": input, "output": output}
    else:
        result = {"input": input, "output": output, "sub": sub}
    time = datetime.datetime.now()
    Log.save_log(user_id, input, output, time, time, sub, None)
    return jsonify(result), 200

@main.route("/button/click/weather", methods=['POST'])
@jwt_required()
def daily_weather():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get("btn_title")
    btn = Button.query.filter_by(btn_title=title).first()
    input = btn.btn_message
    #output = weather(62, 126) #세종대 위치
    output = weather(62, 119) #세종대 위치
    result = {"input": input, "output": output}
    time = datetime.datetime.now()
    Log.save_log(user_id, input, output, time, time, None, None)
    return jsonify(result), 200

@main.route("/button/click/univschedule", methods=['POST'])
@jwt_required()
def univ_schedule():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get("btn_title")
    btn = Button.query.filter_by(btn_title=title).first()
    input = btn.btn_message
    univ = UnivSchedule.query.order_by(UnivSchedule.start.asc()).all()
    list = {}
    for s in univ:
        schedule = {"start": s.start.strftime("%Y-%m-%d"),
                    "end": s.end.strftime("%Y-%m-%d"),
                    "schedule": s.schedule}
        list[s.id]=schedule
    output = btn.btn_contents
    print(list)
    result = {"input": input, "output": output, "schedule": list}
    time = datetime.datetime.now()
    Log.save_log(user_id, input, output, time, time, None, list)
    return jsonify(result), 200


@main.route("/button/click/schedule", methods=['POST'])
@jwt_required()
def smart_button():
    user_id = get_jwt_identity()
    data = request.get_json()
    select_btn = data.get("btn_title") # or btn_id
    btn = Button.query.filter_by(btn_title=select_btn).first()
    if not btn:
        return jsonify({"msg": "btn not found"}), 404
    if select_btn == '일정 등록':
        start = datetime.datetime.strptime(data.get("start"), "%Y-%m-%d")
        end = datetime.datetime.strptime(data.get("end"), "%Y-%m-%d")
        schedule = data.get('schedule')
        if start == end:
            input = start.strftime("%Y-%m-%d") + ": " + schedule
        else:
            input = start.strftime("%Y-%m-%d") + "~" + end.strftime("%Y-%m-%d") + ": " + schedule
        output = btn.btn_contents
        mng = Management(user_id, start, end, schedule)
        db.session.add(mng)
        db.session.commit()
    elif select_btn == '일정 확인':
        start = datetime.datetime.strptime(data.get("start"), "%Y-%m-%d")
        start_date = start.date()
        input = btn.btn_message
        schedule = Management.query.filter(and_(Management.user_id == user_id, Management.start <= start_date, Management.end >= start_date)).all()
        if schedule:
            output = btn.btn_contents + "\n"
            for s in schedule:
                if s.start == s.end:
                    output += str(s.start) + ": "+ str(s.schedule) + "\n"
                else:
                    output += str(s.start) + "~" + str(s.end) + ": "+ s.schedule + "\n"
            output = output.rstrip("\n")
        else:
            output = start.strftime("%Y년 %m월 %d일") + "에 등록된 일정이 없습니다."
    result = {"input": input, "output": output}
    time = datetime.datetime.now()
    Log.save_log(user_id, input, output, time, time, None, None)
    return jsonify(result), 200


@main.route("/log")
@jwt_required()
def log():
    user_id = get_jwt_identity()
    result = Log.get_log(user_id)
    if result is None:
        return 200
    return jsonify(result), 200

#@main.route("/logdelete")
#@jwt_required()
#def log_delete():
#    return 200

'''
@main.route("/blackboard/authorizationcode", methods=['GET'])
def get_auth():
    # 블랙보드 Learn API 호출을 위한 URL
    server = os.getenv('BLACKBOARD_SERVER') 
    auth_url = server + "/learn/api/public/v1/oauth2/authorizationcode"

    params = {
        'response_type': 'code',
        'client_id': os.getenv('BLACKBOARD_ID'),
        'redirect_uri': 'http://localhost:5000/callback'
    }

    response = requests.get(auth_url, params=params)
    if response.status_code != 200:
        return jsonify(response.text, response.status_code)
    else:
        return response.text
    
@main.route("/blackboard/token")
# HTTP POST request to get access token
def get_access_token():
    import base64
    # Authorization header with Base64 encoded key and secret
    key = os.getenv('BLACKBOARD_KEY')
    secret = os.getenv('BLACKBOARD_SECRET')
    credentials = base64.b64encode(f'{key}:{secret}'.encode('ascii')).decode('ascii')
    headers = {'Authorization': f'Basic {credentials}'}

    # Request body
    redirect_uri = 'http://localhost:5000/callback'
    params = {
        'grant_type': 'authorization_code',
        'code': session['code'],
        'redirect_uri': redirect_uri,
        'client_id': key,
        'client_secret': secret
    }
    server = os.getenv('BLACKBOARD_SERVER') 
    token_url = server + "/learn/api/public/v1/oauth2/token"
    # Send request to get access token
    response = requests.post(token_url, headers=headers, params=params)

    # Parse response to get access token
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        return jsonify({"token": access_token})
    else:
        return {(f'Access token request failed with status code ({response.status_code}): {response.text}')}
    

@main.route('/callback')
def callback():
    code = request.args.get('code')
    session['code'] = code
    print(code)
    print("done")
    if code == None:
        return 'code none'
    return 'Authorization code received and stored securely in session.'


@main.route("/blackboard/announcement")
def get_announcement(access_token):
    # 블랙보드 Learn API 호출을 위한 URL
    server = os.getenv('BLACKBOARD_SERVER') 
    announcement_url = server + "/learn/api/public/v1/announcements"
    # API Key와 API Secret
    api_key = os.getenv('BLACKBOARD_KEY')
    api_secret = os.getenv('BLACKBOARD_SECRET')
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    params = {
        'fields': 'id,title,body,availability'
    }
    response = requests.get(announcement_url, headers=headers, params=params)
    if response.status_code != 200:
        raise ValueError('Failed to get announcements')
    else:
        announcements = response.json()['results']
        return announcements

'''

'''
#refresh token 
@main.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token, 'user': user_id}), 200
'''