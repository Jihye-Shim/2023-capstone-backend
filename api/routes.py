# 서버
from flask import session, render_template, request, redirect, url_for, Blueprint
from sejong_univ_auth import ClassicSession, auth

main = Blueprint('main', __name__)
main.secret_key = "secretkey"  # for session

# main
@main.route("/")
def start():
    if "uid" in session:
        print(session["uid"])
        return redirect(url_for("main.chat"))
    else:
        return redirect(url_for("main.login"))

# 로그인 서버
@main.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    elif request.method == 'POST':
        uid = request.form.get("uid")
        upw = request.form.get("upw")
        #auth(id: str, password: str, methods: Authenticator)
        result = auth(id=uid, password=upw, methods=ClassicSession)
        if result.is_auth:
            session["uid"] = uid
            print("uid:" + session["uid"])
            return redirect(url_for("main.chat"))
        else:
            return redirect(url_for("main.login"))
        
# 채팅 서버
@main.route("/chat")
def chat():
    user = session.get("uid", "")
    if user == "":
        return redirect(url_for("main.login"))
    return render_template('chat.html', user = user)