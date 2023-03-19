from flask import Flask, request, render_template 
#render_template: HTML 파일 렌더링 

app = Flask(__name__)

#서버
@app.route("/")
def Hello():
    return "Sejong-ChatBot"

#GET: url에 파라미터 함께 넘김
#POST: http 내부에 데이터 추가(보안)
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        print(uid, upw)
        return "Post success"

if __name__ == '__main__':
    app.debug = True
    app.run()