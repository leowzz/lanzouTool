# lanzouTool v1.0

<img src="https://pc.woozooo.com/img/logo2.gif" width="200">

### Powered By [LanZouCloud-API](https://github.com/zaxtyson/LanZouCloud-API) ![](https://camo.githubusercontent.com/78d53b4ac8106d2546d97b1f2248ce7e69b369b04dc23ae702e777ccd6d11dc3/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f762f72656c656173652f7a61787479736f6e2f4c616e5a6f75436c6f75642d4150492e7376673f6c6f676f3d69436c6f7564)

------

本项目使用python调用 lanzou-api 实现遍历文件夹 上传到蓝奏云,

旨在自动化上传大量工具, 并将分享链接统一生成到markdown, 同时支持上传后设置默认密码

> ## 免责声明
> - 本项目仅供个人学习使用，严禁用于商业用途
> - **本项目没有任何担保**，如果您使用这些代码，您必需承担其带来的风险

------

# 开始使用

## 安装依赖

```
pip install lanzou-api
```

## 注册蓝奏云

[蓝奏云注册](https://pc.woozooo.com/account.php?action=register)

## 获取蓝奏云cookie

#### 大概步骤:

- 打开浏览器调试界面(按F12), 选择网络(Network)

<img src="https://github.com/3181538941/lanzouTool/blob/main/pic/img.png" alt=""/>

- 选择account.php, 在响应头中查看cookie

<img src="https://github.com/3181538941/lanzouTool/blob/main/pic/login.png" alt=""/>

或使用其他方式获取cookie

Cookie 位置:

- `woozooo.com -> Cookie -> ylogin`
- `pc.woozooo.com -> Cookie -> phpdisk_info`

## 配置基本参数

打开`lanzouTool.py`, 在文件中修改配置区域代码:

```python
# 配置区域 begin
# 要扫描的目录
scanPath = r'B:\01_软件,环境\01_工具'
# cookie内的登录信息, cookie中获取的信息
cookie131 = {
    'ylogin'      : '*******',
    'phpdisk_info': 'AjOwBhVhAA......',
}
# 日志生成目录, 运行后会生成:
# 1. .md文件: 用于记录文件名称, 蓝奏云链接, 并自动生成一个引用行用于日后增添文件介绍
# 2. bigFiles.txt: 因为大小超过100MB而略过的文件, 记录其路径
# 3. .log: 程序运行日志
log_dir = r'./log'
# 文件默认密码, 上传文件或者新建文件夹后会设置成默认密码
default_password = '****'
# 配置区域 end
```

## 执行文件

日志信息以及生成的md文件在log目录下, 如果设置其他路径, 请自行访问

# 调用其他api请参考: [api文档](https://github.com/zaxtyson/LanZouCloud-API/wiki)

另行开发请注明出处, 如果有更好的方案, 请提交issue

# 版本

- V1.1 将文件已上传的判断方式由**计算文件MD5并存储**更改为**上传前获取目标文件夹内所有文件名再判断**

