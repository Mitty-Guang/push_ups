# push_ups
 俯卧撑计数，好友排名小程序

[![1.png](https://i.postimg.cc/DZhgV85y/1.png)](https://postimg.cc/t1rPWRLL)
[![2.png](https://i.postimg.cc/141RM1sT/2.png)](https://postimg.cc/2LTf8JqF)
[![3.png](https://i.postimg.cc/523Lrbj8/3.png)](https://postimg.cc/gxxxX9V0)
[![4.png](https://i.postimg.cc/7h856Wfx/4.png)](https://postimg.cc/dk6sNn2X)
 
**项目功能**

该项目为广大使用者提供了一个俯卧撑训练打卡平台，该平台可以用于俯卧撑教学监督、日常练习等场景中，我们希望使用者可以在该平台的帮助下，规范、长期、有效地进行俯卧撑训练。

1. 登陆注册：使用者可以创建自己的个人账号，该平台使用账号密码的方式进行注册与登录，新用户注册后会自动跳转至登录页面

2. 打卡：用户每天运动可以进行打卡，每天的打卡记录平台将进行保存，用户可以在首页看到自己的连续打卡纪录、打卡总天数、最后打卡时间等，点击打卡日历可以看到打卡历史。打卡历史以日历的形式展示，有打卡记录的日期用红色表示，点击对应日期可以看到当日打卡明细（包括打卡时间、训练情况）。所有用户的打卡情况会进行统计，根据总个数进行排名，排名情况可以通过点击首页的"排行榜"查看。

3. 俯卧撑计数：训练分为竞速模式和训练模式。竞速模式限时一分钟，中间无法暂停，训练模式没有时间限制，训练期间用户可以通过左手的位置控制计时的暂停和继续。做俯卧撑期间，全程均有语音提示（例如开始、暂停、继续、最后10秒、结束等提示视频中会显示当前完成的俯卧撑个数，若动作不规范，则会有相应的提示，出现错误的身体部位会被用红圈标出。通过动作不规范的提示，可以使用户掌握动作要领，科学规范地进行训练。

**实现思路**

俯卧撑计数项目的主要功能分为训练和竞速，训练模式用户可以通过设置目标个数开始训练，未完成目标不进行加入到总个数；竞速模式是通过设置1分钟计时，并将结果加入到总个数中。

一、数据存储

为了存储用户信息和锻炼信息，我们在远程数据库中创建了user表和punch表

对于user表，主要记录用户信息并展现在首页。u\_id是自增长的，作为主键区分不同用户；password采用sha256算法进行加密，使用flask的generate\_password\_hash进行加密，采用check\_password\_hash的方法进行解密和判断；head存储用户头像，为每个用户设置默认头像，后续将实现用户自己上传头像；target是针对训练模式的目标个数，用户可进行多次训练target值随之更新；isRecorded判断今日是否打卡，ContinuousDay判断上次连续打卡的天数；TotalDay记录总共打卡天数；LastDay记录上次打卡的日期；TotalNumber记录总个数。

对于punch表，主要是记录训练的数据。id是自增长的，作为主键区分不同训练数据。user\_id记录提交用户；punch\_time提交时间；number记录训练个数；type记录类型，0代表训练模式，1代表竞速模式。

在与数据库交互过程中，由于使用flask技术，我们不使用pymsql直接写SQL语句去操作数据库，而是通过SQLAlchemy提供的ORM技术，像操作Python对象一样实现数据库的增删改查，一个ORM模型对应数据库中的一个表，ORM的类属性对应数据库的一个字段，ORM每个实例对象对应数据库一条记录，具体对应models的User类和Punch类。

二、俯卧撑计数

使用了mediapipe，创建PoseDetector类，其中创建类属性count来记录训练个数。

通过确定类方法run，可以捕捉摄像头，主要目的是再创建PoseDetector类对象的时候，已经开启摄像头和计数，此时可以如果用户选择开始训练的时候，需要将计数置0，原来未点击开始训练前的数据不进行存储。start方法在点击开始训练时调用，将计数置0。end方法在结束训练时调用，释放摄像头。

定义find\_pose方法检测姿势，其中pose.process(imgRGB) 会识别这帧图片中的人体姿势数据，保存到self.results中，定义find\_positions方法获取姿势数据，定义find\_angle方法获取角度并将角度和连线画出来，方便后面用角度来判断是否完成俯卧撑以及俯卧撑是否标准

在get\_video进行检测和计数

然后将完成次数和不规范动作的提示输出到画面中

最后通过图像编码的方式，将图像编码到缓存中，并以比特流形式返回。


1. 日常打卡蓝图实现思路

1. 用户信息的后端绑定：

用户信息存储在session中，在代码中定义钩子函数my\_before\_request()，获取user\_id后在数据库中检查id是否存在，随后将其绑定在全局对象中setattr(g, "user", user)，若不存在则绑定全局对象的用户名user为None。此外，还手动实现了一个装饰器login\_required，用于验证登录状态，否则就跳回到登录界面，因为只对特定的视图函数进行装饰，所以没有写在before\_request中。

1. 上下文处理器：

实现在函数my\_context\_processor()中，用于返回用户数据等重要信息。将我们的定义变量在所有模板中可见。

1. 全局变量：

Start 用于判断是否开始摄像行为的bool 对象

Camera 姿势识别类（定义在camera.py中）对象，用于传递俯卧撑个数信息等以及传递每帧的图像信息并存储在对象属性中或返回。

1. 全局函数：

gen(camera) 用于传递每一帧图像

实现机制：通过全局变量Start来决定是否执行camera的获取当前帧的图像的类方法，并将结果存储在frame变量中，而后通过yield将所得图像逐帧传递。

1. 接口函数：
  1. video\_detection()

作用：向前端传递gen(camera)产生的视频流。

实现机制：将全局变量Start置为True，通过调用Camera全局变量的类方法Camera.run()开启摄像头，传递视频流。

  1. start()

作用：用于开启摄像头记录功能并向前端传递相应提示信息。

实现机制：通过调用Camera全局变量的类方法Camera.start()重置记录值并开启计数功能，传递提示信息。

  1. stop()

作用：用于停止摄像头及其记录功能并向前端传递提示信息与所记录数目。

实现机制：将全局变量Start置为False，通过调用Camera全局变量的类方法Camera.stop()，关闭摄像头并停止计数功能，传递提示信息与所记录数目。

  1. get\_record\_days()

作用：get方法用于渲染页面，post方法用于返回一个月内的打卡数据。

实现机制：通过calendar模块的monthrange函数获取当月的天数。创建records，用于存储一个月内的打卡数据，0为未打卡，1为已打卡。创建循环，for i in range(1, monthdays + 1): i即位具体的某一天，判断i的值是否比今天datetime.datetime.today().day的值大，若如此，则向list中加入0（视为没打卡），否则，通过Punch.query.filter查询符合条件（用户名匹配，日期匹配）的结果，存在结果则向list中加入1，反之加入0。在循环结束后，向前端传递records。

  1. get\_record\_messages()

作用：get方法用于渲染页面，post方法用于返回一个月内某一天的具体打卡信息。

实现机制：将前端传递的具体日期day的值存储于变量day中，查询数据库中打卡表的符合这一日期的打卡记录，并根据用户id过滤。创建exercise为训练数，compete为竞赛数list，total为二者总数。遍历上一步中获取的结果，根据结果的不同种类（训练或竞赛）执行不同操作：若为竞赛，则执行总数追加，并将结果加入compete中；若为训练，则执行训练数追加与总数追加。最终，向前端传递日期、总数、训练数、竞赛列表。

  1. exercise\_record()

作用：get方法用于渲染页面，post方法用于产生训练打卡记录并传递相应提示信息。

实现机制：将前端传递的训练数Number的值存储于变量number中，并根据当前时间与用户id查询数据库中相应记录存储于result中，根据用户id查询用户记录存储于user中。判断本次训练值是否大于等于用户所设目标：若不大于，则打卡失败，返回相应提示信息；否则判断用户今日是否打卡，若未打卡，则执行连续打卡天数、上次打卡时间、打卡总数、是否打卡等信息的更新，然后判断是否存在打卡记录，若存在则追加打卡，若不存在则直接打卡，并将修改提交于数据库。最后返回打卡成功的提示信息。

  1. compete\_record()

作用：get方法用于渲染页面，post方法用于产生竞赛打卡记录并传递相应提示信息。

实现机制：将前端传递的训练数Number的值存储于变量number中，并根据当前时间与用户id查询数据库中相应记录存储于result中，根据用户id查询用户记录存储于user中。判断用户今日是否打卡，若未打卡，则执行连续打卡天数、上次打卡时间、打卡总数、是否打卡等信息的更新。生成打卡数据并添加到数据库中，最后返回打卡成功的提示信息。

  1. register()

作用：get方法用于渲染页面，post方法用于提交注册信息并存储到数据库中。

实现机制：通过接受前端传来的username和password，由于username是唯一的，所以要先在数据库中查询是否存在用户名，不存在则创建一条新的用户记录，否则注册不成功。

  1. login()

作用：get方法用于渲染页面，post方法用于判断用户是否存在、密码是否正确。

实现机制：通过接受前端传来的username和password，在数据库中查询username 是否存在，不存在返回"用户名不存在"，若存在，则比较密码是否正确，不正确返回"密码错误"，否则，返回"登录成功"。

  1. index()

作用：get方法用于渲染页面，post方法用于从数据库中获取用户锻炼的相关信息。

实现机制：通过判断用户的状态，决定返回用户锻炼的相关信息。

  1. exercise\_index()

作用：get方法用于渲染页面，post方法用于判断用户训练个数是否在[1,50]之间。

实现机制：通过接受前端传来的target，判断是否在[1,50]之间，如果是，将其储存在target字段，返回"合法输入"，否则，返回"不合法输入"。

  1. compete\_index()

作用：get方法用于渲染页面。

  1. rankings()

作用：get方法用于渲染页面，post方法用于在数据库中排序并返回前十名的锻炼信息。

实现机制：通过SQLAlchemy的查询操作返回前十名的锻炼信息。

**技术栈**

本项目前端使用html+css+javascript 绘制并装饰界面，使用ajax用于与后端的接口交互，使用vue框架简化开发。

本项目后端使用Flask框架用于python后端的开发，Flask\_SQLAlchemy用于数据库的交互。

**环境**

本项目是一个网页，可以在本地调用摄像头进行训练。

**交互**

本项目十分注重用户的体验。

首先实现了登录注册功能，方便一个用户拥有一个账号，用于进行个人信息的储存，保证可以检查到自己之前的打卡信息，以及自己之前的锻炼内容。

其次实现了对于过去打卡记录的查看，以及对于自己之前运动量的查看，方便查看自己是否有哪天忘记打卡，可以根据自己之前的运动量制定自己之后的运动计划。

再次将功能分为了两个部分，分别为竞速模式和训练模式，可以合理安排自己的的运动方式，并且可以查看其他人的运动情况，方便自己进行比较，并且可以激发自己的运动动力。

最后实现了运动排行榜的功能，运动排行榜功能可以深刻的体会到自己在使用这款软件的人群所排的位置，可以提高自己运动的积极性，激发自己运动的动力。

**测试**

1. 项目背景：

俯卧撑计数项目是一款面向广大俯卧撑爱好者、练习者的平台。当前社会俯卧撑是运动者的普遍难题，主打运动监督的软件有很多，但实现实时计数的平台较少，本项目意在为使用者提供一个俯卧撑教学、监督、练习、规范一体化的平台，通过实时计数来达到监督的目的。

1. 编写目的：

该测试文档的目的是研究俯卧撑计数平台的总体需求、背景。对开发结果、开发评价进行分析，得出经验与教训。

1. 测试用例设计

（1）登录注册操作

表1 注册第一组测试用例

| 测试用例编号 | Enroll\_01 |
| --- | --- |
| 测试项目 | 用户注册 |
| 重要级别 | 高 |
| 预设条件 | 系统不存在该用户 |
| 输入 | 用户：lisa 密码：1234567 |
| 操作步骤 | 点击注册新用户-输入用户名-输入密码-确认密码 |
| 预期输出 | 密码输入时被隐藏，显示注册成功 |

表2 注册第2组测试用例

| 测试用例编号 | Enroll\_02 |
| --- | --- |
| 测试项目 | 用户注册 |
| 重要级别 | 高 |
| 预设条件 | 系统不存在该用户 |
| 输入 | 用户：lisa 密码：987654 |
| 操作步骤 | 点击注册新用户-输入用户名-输入密码-确认密码 |
| 预期输出 | 密码输入时被隐藏，显示注册失败 |

表3 登录第1组测试用例

| 测试用例编号 | signin\_01 |
| --- | --- |
| 测试项目 | 用户登录 |
| 重要级别 | 高 |
| 预设条件 | 系统存在该用户 |
| 输入 | 用户：lisa 密码：1234567 |
| 操作步骤 | 点击登录-输入用户名-输入密码-确认 |
| 预期输出 | 密码输入时被隐藏，显示登录成功 |

表4 登录第2组测试用例

| 测试用例编号 | signin\_02 |
| --- | --- |
| 测试项目 | 用户登录 |
| 重要级别 | 高 |
| 预设条件 | 系统存在该用户 |
| 输入 | 用户：debug 密码：123123123 |
| 操作步骤 | 点击登录-输入用户名-输入密码-确认 |
| 预期输出 | 密码输入时被隐藏，显示登录成功 |

（2）查看打卡记录

表5 查看打卡日历

| 测试用例编号 | check\_01 |
| --- | --- |
| 测试项目 | 查看打卡日历 |
| 重要级别 | 中 |
| 预设条件 | 用户已登录 |
| 输入 | 无 |
| 操作步骤 | 点击打卡日历以及日期 |
| 预期输出 | 显示对应日期的打卡记录 |

表6 查看排行榜

| 测试用例编号 | check\_02 |
| --- | --- |
| 测试项目 | 查看排行榜 |
| 重要级别 | 中 |
| 预设条件 | 用户已登录 |
| 输入 | 无 |
| 操作步骤 | 点击排行榜 |
| 预期输出 | 显示完成俯卧撑的总个数排名 |

（3）俯卧撑计数操作

表7训练模式测试用例

| 测试用例编号 | train\_01 |
| --- | --- |
| 测试项目 | 俯卧撑训练 |
| 重要级别 | 高 |
| 预设条件 | 用户已登录 |
| 输入 | 训练个数：2 |
| 操作步骤 | 点击训练模式-输入个数-开始训练 |
| 预期输出 | 完成规定个数，打卡成功 |

表8 竞速模式测试用例

| 测试用例编号 | train\_02 |
| --- | --- |
| 测试项目 | 俯卧撑竞速 |
| 重要级别 | 高 |
| 预设条件 | 用户已登录 |
| 输入 | 无 |
| 操作步骤 | 点击竞速模式-开始训练 |
| 预期输出 | 完成个数，打卡成功 |


**部署**

1. 前提环境

| 名称 | 版本 |
| --- | --- |
| Python | 3.8 |
| Mysql | 8.0.25 |

依赖：

alembic==1.9.1

Flask==2.2.2

Flask\_Migrate==4.0.0

Flask\_SQLAlchemy==2.5.1

mediapipe==0.8.11

numpy==1.23.1

opencv\_python==4.6.0.66

Pillow==9.4.0

SQLAlchemy==1.4.40

Werkzeug==2.2.2

WTForms==3.0.1

1. **部署步骤**

   将项目解压，在python环境中进入项目目录

   安装依赖

pip install -r requirements.txt

Mysql配置

首先修改config.py文件，将HOSTNAME改为自己的MySQL数据库ip，将密码改为自己的账号密码：

然后打开一个数据库管理软件，以navicat为例，

点击连接

选择MySQL

填入刚才修改的ip和密码并连接，其中连接名可以自己随意取

然后打开python\_user中的表格便可查看数据库信息

4、运行项目

python app.py

5、运行完项目后在浏览器中进入[http://127.0.0.1:5000](http://127.0.0.1:5000/)，便可访问项目首页
