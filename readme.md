# 浙江大学科学打卡

脚本原理是复制上一次旧信息作为今日信息提交。如果需要更新位置等信息，在每日自动打卡前先手动打卡，或停止服务并手动打卡。

##### 2022年8月26日 更新特性
- 打卡成功或失败时通过微信发送提示消息
- 打卡地点的经纬度增加了随机偏移量
- 支持action自动打卡

### 1 方式一：离线使用

#### 1.1 申请iyuu序列号

微信提示的功能通过爱语飞飞接口实现。进入[http://iyuu.cn/]()根据提示关注公众号，扫描二维码可以生成序列号（iyuu-token）。

#### 1.2 本地运行

打卡的主函数在文件`main.py`中，包括以下3个命令行参数。

``` py
python main.py <学号> <密码> <iyuu-token>
```

### 2 方式二：使用action自动打卡

该项目配置了github action任务，启用前请参考1.1申请iyuu序列号。

#### 2.1 启用action

1. 将项目fork到自己账号下

2. 新增secret

secret包括以下三个内容：

- ACCOUNT：学号
- PASSWORD：密码
- TOKEN：爱语飞飞序列号

![](https://github.com/Chen-Carl/daily-ZJU/raw/main/images/readme-1.png)

成功配置后，在repository secrets下应显示

![](https://github.com/Chen-Carl/daily-ZJU/raw/main/images/readme-2.png)

3. 启用action

在Action界面启动预先配置的ClockIn任务。

![](https://github.com/Chen-Carl/daily-ZJU/raw/main/images/readme-3.png)

#### 2.2 任务异常说明

以下情况将导致任务异常退出，并且通过微信显示异常信息：
- 登录失败
- 获取旧信息失败
- 提交信息失败
- 其他异常

同时，将会收到github报错邮件。任务异常时，需要手动重启action。

注：使用该脚本多次提交将收到“今日已提交”信息，并且任务不会失败。