#server
from flask import session, render_template, request, redirect, url_for, Blueprint
from sejong_univ_auth import ClassicSession, auth
from .db import db, User

main = Blueprint('main', __name__)
main.secret_key = "secretkey"  # for session

#main
@main.route("/")
def start():
    if "uid" in session:
        print(session["uid"])
        return redirect(url_for("main.chat"))
    else:
        return redirect(url_for("main.login"))
'''
#test code
#login page
@main.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        uid = request.form.get("uid")
        upw = request.form.get("upw")
        #auth(id: str, password: str, methods: Authenticator)
        result = auth(id=uid, password=upw, methods=ClassicSession)
        if result.is_auth:  #login success
            record = User.query.filter_by(id=uid).first()
            if record:
                pass
            else:
                name = result.body['name']
                major = result.body['major']
                grade = result.body['grade']
                user = User(uid, name, major, grade)
                db.session.add(user)
                db.session.commit()
            if "uid" not in session:
                session["uid"] = uid
            return redirect(url_for("main.chat"))
        else:
            return redirect(url_for("main.login"))
        
#chatbot page
@main.route("/chat")    
def chat():
    user = session.get("uid", "")
    if user == "":
        return redirect(url_for("main.login"))
    return render_template("chat.html", user = user)

'''

#login page
@main.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        uid = request.get_json("uid")
        upw = request.get_json("upw")
        #auth(id: str, password: str, methods: Authenticator)
        result = auth(id=uid, password=upw, methods=ClassicSession)
        if result.is_auth:
            record = User.query.filter_by(id=uid).first()
            if record:
                pass
            else:
                name = result.body['name']
                major = result.body['major']
                grade = result.body['grade']
                user = User(uid, name, major, grade)
                db.session.add(user)
                db.session.commit()
            if "uid" not in session:
                session["uid"] = uid
            return redirect(url_for("main.chat"))
        else:
            return redirect(url_for("main.login"))
        
#chatbot page
@main.route("/chat")    
def chat():
    user = session.get("uid", "")
    if user == "":
        return redirect(url_for("main.login"))
    return render_template("index.html", user = user)
