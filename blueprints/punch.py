from flask import Blueprint, request, jsonify, session, g, render_template ,Response
from exts import db
from models import Punch, User
import calendar
import datetime
from .forms import RecordDays
import json
from decorators import login_required
from camera import PoseDetector
bp = Blueprint("punch", __name__, url_prefix="/record")


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


def gen(camera):
    while Start:
        frame = camera.get_video()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@bp.route('/video_detection')
def video_detection():
    global Start
    global Camera
    Start = True
    Camera.run()
    return Response(gen(Camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/start')
def start():
    global Camera
    Camera.start()
    return jsonify({"code": 200, "message": "开始", "data": 0})


@bp.route('/stop')
def stop():
    global Start
    global Camera
    Start = False
    Camera.stop()
    # setattr(g, "count", int(Camera.count))
    print(int(Camera.count))
    return jsonify({"code": 200, "message": "结束", "data": int(Camera.count)})

@bp.route("/getRecordDays", methods=['GET', 'POST'])
def get_record_days():
    uid = g.user.uid
    time_now = datetime.datetime.now()
    if request.method == 'GET':
        return render_template("days.html")
    else:
        monthdays = calendar.monthrange(time_now.year, time_now.month)[1]
        records = []
        for i in range(1, monthdays+1):
            if datetime.datetime.today().day < i:
                records.append(0)
            else:
                result = Punch.query.filter(Punch.user_id == uid,
                                            datetime.datetime(time_now.year, time_now.month, i) <= Punch.punch_time,
                                            Punch.punch_time <= datetime.datetime(time_now.year,
                                                                                  time_now.month, i + 1)).first()

                if result:
                    records.append(1)
                else:
                    records.append(0)
        return jsonify({"code": 200, "message": "查询成功！", "data": records})


@bp.route("/getRecordMessages", methods=['GET', 'POST'])
@login_required
def get_record_messages():
    uid = session['uid']
    time_now = datetime.datetime.now()
    if request.method == 'GET':
        return render_template("days.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        day = json_data.get("day")
        results = Punch.query.filter(Punch.user_id == uid,
                                     datetime.datetime(time_now.year, time_now.month, day) <= Punch.punch_time,
                                     Punch.punch_time <= datetime.datetime(time_now.year, time_now.month, day + 1)). \
            order_by(Punch.id.desc()).all()
        exercise = 0
        total = 0
        compete = []
        for result in results:
            total += result.number
            if result.type == 1:
                exercise += result.number
            else:
                compete.append(result.number)
        print(datetime.date(time_now.year, time_now.month, day))
        return jsonify({"code": 200, "message": "查询成功！", "data": {
            "date": datetime.date(time_now.year, time_now.month, day),
            "TotalNumber": total,
            "ExerciseNumber": exercise,
            "CompeteNumber": compete
        }})


@bp.route("/exercise", methods=['GET', 'POST'])
@login_required
def exercise_record():
    uid = g.user.uid
    time_now = datetime.datetime.now()
    date_now = datetime.date.today()
    setattr(g, "type", 0)
    if request.method == 'GET':
        return render_template("exercise.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        number = json_data.get("Number")
        result = Punch.query.filter(Punch.user_id == uid,
                                    datetime.datetime(time_now.year, time_now.month, time_now.day) <= Punch.punch_time,
                                    Punch.punch_time <= datetime.datetime(time_now.year,
                                                                          time_now.month,
                                                                          time_now.day + 1),
                                    Punch.type == 0). \
            order_by(Punch.id.desc()).first()
        user = User.query.filter(User.uid == uid).first()
        # print("目标"+number)
        # print(user.target)
        if int(number) < user.target:
            return jsonify({"code": 200, "message": "打卡失败，未达到目标！", "data": 0})
        else:
            if user.isRecorded == 0:
                if user.LastDay == date_now - datetime.timedelta(days=1):
                    user.ContinuousDay += 1
                else:
                    user.ContinuousDay = 1
                user.LastDay = date_now
                user.TotalDay += 1
                user.isRecorded = 1
            user.TotalNumber += int(number)
            if not result:
                punch = Punch(user_id=uid, type=0, number=int(number))
                db.session.add(punch)
            else:
                result.number += int(number)
            db.session.commit()
            return jsonify({"code": 200, "message": "打卡成功！", "data": 0})


@bp.route("/compete", methods=['GET', 'POST'])
@login_required
def compete_record():
    uid = g.user.uid
    date_now = datetime.date.today()
    setattr(g, "type", 1)
    if request.method == 'GET':
        return render_template("compete.html")
    else:
        data = request.get_data()
        json_data = json.loads(data.decode("UTF-8"))
        number = json_data.get("Number")
        user = User.query.filter(User.uid == uid).first()
        if not user.isRecorded:
            if user.LastDay == date_now - datetime.timedelta(days=1):
                user.ContinuousDay += 1
            else:
                user.ContinuousDay = 1
            user.LastDay = date_now
            user.TotalDay += 1
            user.isRecorded = True
        user.TotalNumber += int(number)
        punch = Punch(user_id=uid, type=1, number=int(number))
        db.session.add(punch)
        db.session.commit()
        return jsonify({"code": 200, "message": "打卡成功！", "data": 0})


Start = False
Camera = PoseDetector()


