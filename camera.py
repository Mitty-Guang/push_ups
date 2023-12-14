##  视频需要头朝左

import cv2
import mediapipe as mp
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype("simsun.ttc", textSize, encoding="utf-8")
    draw.text(position, text, textColor, font=fontStyle)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


class PoseDetector():
    '''
    人体姿势检测类
    '''

    def __init__(self,
                 static_image_mode=False,
                 upper_body_only=False,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        '''
        初始化
        :param static_image_mode: 是否是静态图片，默认为否
        :param upper_body_only: 是否是上半身，默认为否
        :param smooth_landmarks: 设置为True减少抖动
        :param min_detection_confidence:人员检测模型的最小置信度值，默认为0.5
        :param min_tracking_confidence:姿势可信标记的最小置信度值，默认为0.5
        '''
        self.static_image_mode = static_image_mode
        self.upper_body_only = upper_body_only
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        # 创建一个Pose对象用于检测人体姿势
        self.pose = mp.solutions.pose.Pose(self.static_image_mode, self.upper_body_only, self.smooth_landmarks,
                                           self.enable_segmentation,
                                           self.min_detection_confidence, self.min_tracking_confidence)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.count = 0
        self.dir = 0
        self.cap.release()
        self.iscounted = False

    def run(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.count = 0

    def start(self):
        self.iscounted = True
        self.count = 0

    def stop(self):
        self.iscounted = False
        self.cap.release()

    def find_pose(self, img, draw=True):
        '''
        检测姿势方法
        :param img: 一帧图像
        :param draw: 是否画出人体姿势节点和连接图
        :return: 处理过的图像
        '''
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # pose.process(imgRGB) 会识别这帧图片中的人体姿势数据，保存到self.results中
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                mp.solutions.drawing_utils.draw_landmarks(img, self.results.pose_landmarks,
                                                          mp.solutions.pose.POSE_CONNECTIONS)
        return img

    def find_positions(self, img):
        '''
        获取人体姿势数据
        :param img: 一帧图像
        :param draw: 是否画出人体姿势节点和连接图
        :return: 人体姿势数据列表
        '''
        # 人体姿势数据列表，每个成员由3个数字组成：id, x, y
        # id代表人体的某个关节点，x和y代表坐标位置数据
        self.lmslist = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmslist.append([id, cx, cy])

        return self.lmslist

    def find_angle(self, img, p1, p2, p3, draw=True):
        '''
        获取人体姿势中3个点p1-p2-p3的角度
        :param img: 一帧图像
        :param p1: 第1个点
        :param p2: 第2个点
        :param p3: 第3个点
        :param draw: 是否画出3个点的连接图
        :return: 角度
        '''
        x1, y1 = self.lmslist[p1][1], self.lmslist[p1][2]
        x2, y2 = self.lmslist[p2][1], self.lmslist[p2][2]
        x3, y3 = self.lmslist[p3][1], self.lmslist[p3][2]

        # 使用三角函数公式获取3个点p1-p2-p3，以p2为角的角度值，0-180度之间
        angle = int(math.degrees(math.atan2(y1 - y2, x1 - x2) - math.atan2(y3 - y2, x3 - x2)))
        # if angle < 0:
        #     angle = angle + 360
        # if angle > 180:
        #     angle = 360 - angle
        if angle > 300:
            angle = 360 - angle

        if angle < -250:
            angle = 360 + angle

        if draw:
            # cv2.circle(img, (x1, y1), 20, (0, 255, 255), cv2.FILLED)
            # cv2.circle(img, (x2, y2), 30, (255, 0, 255), cv2.FILLED)
            # cv2.circle(img, (x3, y3), 20, (0, 255, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255, 3))
            cv2.line(img, (x2, y2), (x3, y3), (255, 255, 255, 3))
            cv2.putText(img, str(angle), (x2 - 50, y2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2)

        return angle

    def get_video(self):
        cap = self.cap

        # 视频宽度高度
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # out = cv2.VideoWriter('fuwocheng.mp4', fourcc, 30.0, (width, height))

        stop_duration = 0  # 手放在暂停区域的持续时间
        start_duration = 0  # 手放在开始区域的持续时间
        is_stop = 0  # 是否暂停

        # while True:
        # 读取摄像头，img为每帧图片
        success, img = cap.read()
        img = cv2.flip(img, 1)
        if success:
            h, w, c = img.shape
            # 识别姿势
            img = self.find_pose(img, draw=True)
            # 获取姿势数据
            positions = self.find_positions(img)

            if positions:
                # 如果左手位置在画面的左1/4，上1/3区域停留超过100帧则暂停
                if is_stop == 0 and self.lmslist[19][1] < w // 4 and self.lmslist[19][2] < h // 3:
                    stop_duration += 1
                    # print('stop_duration=', stop_duration)
                    if stop_duration >= 100:  # 超过100帧
                        print('暂停')
                        stop_duration = 0
                        is_stop = 1
                else:
                    stop_duration = 0
                # 如果左手位置在画面的左1/4，下1/3区域停留超过100帧则结束暂停
                if is_stop == 1 and self.lmslist[19][1] < w // 4 and self.lmslist[19][2] > 2 * h // 3:
                    start_duration += 1
                    # print('start_duration=', start_duration)
                    if start_duration >= 100:
                        print('开始')
                        start_duration = 0
                        is_stop = 0
                else:
                    start_duration = 0

                if is_stop == 1:
                    img = cv2AddChineseText(img, '已暂停', (w // 2, h // 2))

                # 获取俯卧撑的角度
                angle1 = self.find_angle(img, 27, 23, 11)
                # angle2 = detector.find_angle(img, 11, 13, 15)
                angle3 = self.find_angle(img, 13, 11, 23)
                angle4 = self.find_angle(img, 15, 27, 11)
                # 大腿、膝盖、小腿
                angle5 = self.find_angle(img, 27, 25, 23)
                result = ''
                isready = False
                delt_x = abs(self.lmslist[12][1] - self.lmslist[28][1])
                delt_y = abs(self.lmslist[12][2] - self.lmslist[28][2])

                if delt_y == 0:
                    isready = True
                elif float(delt_x / delt_y) > 0.5:
                    isready = True

                # 进度条长度
                bar = np.interp(angle4, (0, 20), (w // 2 - 100, w // 2 + 100))
                cv2.rectangle(img, (w // 2 - 100, h - 150), (int(bar), h - 100), (0, 255, 0), cv2.FILLED)
                # 角度小于50度认为撑下
                # if angle2 <= 50 and angle1 >= 165:
                if isready:
                    if angle1 > -165 and angle1 < 165:
                        result = "注意腰部！"
                        x1, y1 = self.lmslist[23][1], self.lmslist[23][2]
                        cv2.circle(img, (x1, y1), 40, (0, 0, 255), cv2.FILLED)
                    else:
                        if angle3 < 30 and angle3 > 3:
                            result = "请胸部靠近地面"
                            x1, y1 = self.lmslist[11][1], self.lmslist[11][2]
                            cv2.circle(img, (x1, y1), 40, (0, 0, 255), cv2.FILLED)

                        if angle5 < 160 and angle5 > -160:
                            result = "请将腿伸直！"
                            x1, y1 = self.lmslist[25][1], self.lmslist[25][2]
                            cv2.circle(img, (x1, y1), 40, (0, 0, 255), cv2.FILLED)

                        if angle3 < 3 and angle4 <= 10:
                            if self.dir == 1:
                                self.count = self.count + 0.5
                                self.dir = 0

                        # if angle3 < 3 and angle4 < 10:
                        #     if dir == 0:
                        #         dir = 1
                        #     if dir == 2:
                        #         dir = 1

                        # 角度大于125度认为撑起
                        # if angle2 >= 125 and angle1 >= 165:
                        if (angle3 > 30 or angle3 < -30) and (angle1 >= 165 or angle1 <= -165) and angle4 >= 10:
                            if self.dir == 0:
                                self.count = self.count + 0.5
                                print("您已做了：", int(self.count), " 个")
                                self.dir = 1
                cv2.putText(img, str(int(self.count)), (w // 2, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255),
                            20, cv2.LINE_AA)
                img = cv2AddChineseText(img, result, (w // 4, h // 4))
                if result:
                    print("动作不规范：", result)

                # return (int(count), result)

            # 打开一个Image窗口显示视频图片
            # cv2.imshow('Image', img)
            _, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tobytes()
            # 录制视频
            # out.write(img)
        return
        # # 如果按下q键，程序退出
        # key = cv2.waitKey(1)
        # if key == ord('q'):
        #     break

        # 关闭视频保存器
        # out.release()
        # 关闭摄像头
        # cap.release()
        # 关闭程序窗口
        # cv2.destroyAllWindows()

#
# def main():
#     PoseDetector.get_video('PoseVideos/fuwocheng1.mp4')
#
# if __name__ == '__main__':
#     main()
