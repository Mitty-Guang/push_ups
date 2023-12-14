import json

from flask import Blueprint, request, jsonify, session, redirect, url_for, g, render_template
from exts import db
import string
import random
import config
from models import User
from .forms import RegisterForm, LoginForm, TargetForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from sqlalchemy import desc
import os
from decorators import login_required
import datetime

bp = Blueprint("user", __name__, url_prefix="/user")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 设置可上传图片后缀


def allowed_file(filename):  # 检查上传图片是否在可上传图片允许列表
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.before_request
def my_before_request():
    uid = session.get("uid")
    if uid:
        user = User.query.filter_by(uid=uid).first()
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


@bp.context_processor
def my_context_processor():
    return {"user": g.user}


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        username = json_data.get("username")
        password = json_data.get("password")
        user = User.query.filter(User.username == username).first()
        if not user:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            redirect(url_for('user.login'))
            return jsonify({"code": 200, "message": "注册成功", "data": None})
        else:
            redirect(url_for('user.register'))
            return jsonify({"code": 201, "message": "注册失败，用户名已存在", "data": None})


@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        username = json_data.get("username")
        password = json_data.get("password")
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"code": 201, "message": "用户名不存在", "data": None})
        if check_password_hash(user.password, password):
            session['username'] = user.username
            session['uid'] = user.uid
            redirect(url_for('user.index'))
            return jsonify({"code": 200, "message": "登录成功", "data": None})
        else:
            return jsonify({"code": 200, "message": "密码错误", "data": None})


@bp.route("/index", methods=['GET', 'POST'])
def index():
    date_now = datetime.date.today()
    if request.method == 'GET':
        return render_template("index.html")
    else:
        if not g.user:
            data = {}
            data["head"] = None
            data["username"] = None
            data["isRecorded"] = None
            data["ContinuousDay"] = None
            data["TotalDay"] = None
            data["LastDay"] = None
            return jsonify({"code": 200, "message": "尚未登录", "data": data})
        else:
            data = {}
            data["head"] = g.user.head
            data["username"] = g.user.username
            data["ContinuousDay"] = g.user.ContinuousDay
            data["TotalDay"] = g.user.TotalDay
            data["LastDay"] = str(g.user.LastDay)
            if data["LastDay"] != date_now:
                g.user.isRecorded = 0
                user = User.query.filter(User.uid == g.user.uid).first()
                user.isRecorded = 0
                db.session.commit()
            data["isRecorded"] = g.user.isRecorded
            return jsonify({"code": 200, "message": "已经登录", "data": data})


#

@bp.route("/exercise/index", methods=['GET', 'POST'])
@login_required
def exercise_index():
    if request.method == 'GET':

        return render_template("exercise_index.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        target =int(json_data.get("target"))
        if 1 <= target <= 50:
            g.user.target = target
            db.session.flush()
            db.session.commit()
            return jsonify({"code": 200, "message": "合法输入", "data": None})
        else:
            return jsonify({"code": 201, "message": "不合法输入", "data": None})


@bp.route("/compete/index", methods=['GET', 'POST'])
@login_required
def compete_index():
    if request.method == 'GET':
        return render_template("compete_index.html")

#
# @bp.route("/chooseClass", methods=['GET', 'POST'])
# @login_required
# def chooseClass():
#     if request.method == 'GET':
#         return render_template("chooseClass.html")
#     else:
#         if g.user.classroom == 0:
#             data = request.get_data()
#             json_data = json.loads(data.decode("UTF-8"))
#             classroom = json_data.get("classroom")
#             # classroom = request.form['classroom']
#             g.user.classroom = classroom
#             db.session.flush()
#             db.session.commit()
#             return redirect(url_for("user.index"))
#         else:
#             return jsonify({"code": 200, "message": "已加入班级，不能重复加入", "data": None})


@bp.route("/rankings", methods=['GET', 'POST'])
@login_required
def rankings():
    if request.method == 'GET':
        return render_template("rankings.html")
    else:
        u = User.query.order_by(User.TotalNumber.desc()).all()
        ranking = 0
        a = 0
        # for i in u:
        #     print(i.username,i.TotalNumber)
        for i in u:
            if g.user.username == i.username:
                ranking = a + 1
                break
            a += 1
        # , User.query.order_by(User.TotalNumber.desc()).limit(10)
        u_User = User.query.order_by(User.TotalNumber.desc()).limit(10).all()
        users = [g.user]
        for u_user in u_User:
            users.append(u_user)
        # print(users)
        user_list = []
        for user in users:
            user_list.append(user.to_json())

        data = {}
        data["ranking"] = ranking
        data["users"] = user_list

        return jsonify({"code": 200, "message": "成功查看", "data": data})


@bp.route('/gravatar', methods=['GET', 'POST'])
def edit_gravatar():
    uid = session['uid']
    if request.method == 'GET':
        return
    else:
        if 'photo' not in request.files:
            return jsonify({"code": 200, "message": "上传失败", "data": 1})
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"code": 200, "message": "上传失败", "data": 2})
        if file and allowed_file(file.filename):
            filename = str(uid) + "." + file.filename.rsplit('.', 1)[1]
            file_path = config.UPLOAD_FOLDER
            file.save(os.path.join(file_path, filename))
            user = User.query.filter(User.uid == uid).first()
            # user.head = config.UPLOAD_FOLDER + filename
            user.head = config.IMAGE + filename
            db.session.commit()
            return jsonify({"code": 200, "message": "上传成功", "data": 0})
        return jsonify({"code": 200, "message": "上传失败", "data": 3})
