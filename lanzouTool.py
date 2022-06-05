#!/usr/bin/env python
# coding: utf-8

# 是否使用mysql存储文件md5等信息, 主要用来检测文件是否已经上传过
# 如过没有相关环境或不想使用, 则下面的config字典也可以忽略
UseMysql = False
# cookie内的登录信息, cookie中获取的信息
cookie131 = {
    'ylogin'      : '*******',
    'phpdisk_info': 'AjRWATUAOwBhDGJTAAVhAA......',
}
# 默认日志生成路径
log_dir = r'./log'
# 文件默认密码, 上传文件或者新建文件夹后会设置成默认密码
default_password = '****'
# 数据库配置参数, UseMysql = False 时忽略
config = {
    'host'    : "localhost",
    'port'    : 3306,
    'user'    : "root",
    'passwd'  : "******",
    'charset' : 'utf8',
    'database': 'mydata',
}

import os
import time
from lanzou.api import LanZouCloud

if writeToMysql:
    import hashlib
    import pymysql

fileNameUrlDict = {}
# 获取时间
log_path = time.strftime('%Y-%m-%d_%H%M%S.txt', time.localtime(time.time()))
md_path = time.strftime('%Y-%m-%d_%H%M%S.md', time.localtime(time.time()))
# 创建日志目录
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
# 拼接日志文件路径
log_path = os.path.join(log_dir, log_path)
md_path = os.path.join(log_dir, md_path)
# 初始化忽略文件信息, 脚本执行完会添加到日志末尾
ignore_info = f'\n\n[{"*" * 30} 文件过大，跳过 {"*" * 30}]\n\n'

lzy = LanZouCloud()

lzy.login_by_cookie(cookie)


def split_name_type(file_path):
    """分割文件路径, 返回文件类型, 文件名, 文件夹路径"""
    splitext = os.path.splitext(file_path)
    file_name = os.path.basename(splitext[0])
    file_type = splitext[1][1:]
    return file_name, file_type


def writeToMd(file_path, content):
    """将内容写入文件"""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)


def Log(content):
    """写入日志"""
    global log_path
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(content + '\n')


def isBigFile(file_path, size_limit=100):
    """
    判断文件大小是否大于size_limit
    :param file_path: 需要判断的文件路径
    :param size_limit: 大小限制
    :return: 大于size_limit返回-1, 否则返回文件大小
    """
    # 文件大于100MB
    global ignore_info
    file_bytes = os.path.getsize(file_path)
    file_size_MB = file_bytes / 1048576
    if file_size_MB > size_limit:
        file_name = os.path.basename(file_path)
        ignore_info += f'[{file_name}]({file_path}) 大小: {file_size_MB:.2f}MB\n\n'
        return -1
    else:
        file_size_MB = f'{file_size_MB:.2f}'
        return file_size_MB


def getFileMd5(file_path):
    # 计算文件md5
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def writeDictToMd():
    """将文件名和文件路径写入文件"""
    with open(md_path, 'a', encoding='utf-8') as f:
        for key, value in fileNameUrlDict.items():
            f.write(f"[{key}]({value})\n\n>\n\n")


def show_progress(file_name, total_size, now_size):
    """显示进度的回调函数"""
    percent = now_size / total_size
    bar_len = 40  # 进度条总长度
    bar_str = '#' * round(bar_len * percent) + '=' * round(bar_len * (1 - percent))
    print('\r{:.2f}%\t[{}] {:.1f}/{:.1f}MB | {} '.format(
        percent * 100, bar_str, now_size / 1048576, total_size / 1048576, file_name), end='')
    if total_size == now_size:
        print('')  # 下载完成换行


def handler(fid, is_file):
    """上传完成回调函数"""
    if is_file:
        lzy.set_passwd(fid, default_password)
        # 获取文件链接
        share_info = lzy.get_share_info(fid, is_file=True)
        # 存储文件名和链接
        file_name = split_name_type(share_info.name)[0]
        fileNameUrlDict[file_name] = share_info.url


def workingWithFolders(folder_path, parent_dir_id=-1, passwd=default_password):
    """
    获取所有文件夹, 存在则获取信息, 不存在则创建
    :param folder_path: 文件夹路径
    :param parent_dir_id: 父文件夹id
    :param passwd: 默认密码
    :return: 文件夹编号, 文件夹链接
    """
    folder_name = os.path.basename(folder_path)
    Log(f'{"-" * 30}开始处理文件夹: {folder_name}{"-" * 30}')
    # 获取蓝奏云账号下所有文件夹信息
    all_dirs = lzy.get_move_folders()
    # 获取文件夹id, 不存在为None
    dir_info = all_dirs.find_by_name(folder_name)
    if dir_info:
        Log(f'文件夹已存在, id为{dir_info.id}')
        dir_id = dir_info.id  # 获取已存在文件夹id
        dir_share_info = lzy.get_share_info(dir_id, is_file=False)
        # 获取已存在文件夹的分享链接
        dir_url = dir_share_info.url
    else:
        Log(f'文件夹不存在, 创建之')
        dir_id = lzy.mkdir(parent_dir_id, folder_name)
        dir_url = lzy.get_share_info(dir_id, is_file=False).url
        lzy.set_passwd(dir_id, passwd, is_file=False)
    return dir_id, dir_url


def needToUploadSelectByMysql(_cursor, file_path: str):
    file_md5 = getFileMd5(file_path)
    # 判断文件在数据库内是否已存在
    _cursor.execute(f"select md5_value from mydata.tool_md5 where md5_value=%s", file_md5)
    cursor_fetchall = _cursor.fetchall()
    # 文件不存在, 将数据写入数据库
    if cursor_fetchall == ():
        _cursor.execute(f"insert into mydata.tool_md5(md5_value, tool_name, tool_size, tool_path) values(%s, %s, %s, %s)",
                        (file_md5, _file, file_size, dir_path))
        return True
    return False


def recordError(uploadFlag):
    if LanZouCloud.FAILED == uploadFlag:
        Log(f'{"*" * 20} {_file} 未上传, Error: 上传失败')
    elif LanZouCloud.NETWORK_ERROR == uploadFlag:
        Log(f'{"*" * 20} {_file} 未上传, Error: 网络异常')
    elif LanZouCloud.PATH_ERROR == uploadFlag:
        Log(f'{"*" * 20} {_file} 未上传, Error: 路径错误')


def scanDir(dir_path, parent_dir_id=-1, writeToMysql=None):
    """
    遍历文件夹, 并上传文件
    :param dir_path: 文件夹路径
    :param parent_dir_id: 蓝奏云文件夹id, 默认-1, 代表根路径
    :param writeToMysql: 是否需要使用mysql记录数据, 默认为空, 需要则传递游标
    """
    # 获取目录名
    folder_name = os.path.basename(dir_path)
    dir_id, dir_url = workingWithFolders(folder_name, parent_dir_id)
    # 将父目录名写入markdown
    writeToMd(md_path, f'# [{folder_name}]({dir_url})\n\n')
    # 文件名-链接字典初始化
    global fileNameUrlDict
    fileNameUrlDict = {}
    # 待处理文件夹列表初始化
    dir_list = []
    for _file in os.listdir(dir_path):
        # 处理拼接文件路径
        file_path = os.path.join(dir_path, _file)
        # 文件, 大小合理 存储后上传
        if os.path.isfile(file_path):
            file_size = isBigFile(file_path)
            # 大文件 存储日志, 直接跳过
            if file_size == -1:
                continue
            if writeToMysql is not None:
                if needToUploadSelectByMysql(writeToMysql, file_path):
                    uploadFlag = lzy.upload_file(
                        file_path,
                        folder_id=dir_id,
                        callback=show_progress,  # 显示上传信息回调函数
                        uploaded_handler=handler  # 上传完成回调函数
                    )
                    if LanZouCloud.SUCCESS != uploadFlag:
                        recordError(uploadFlag)
                else:
                    Log(f'{_file} 已存在')
            else:
                uploadFlag = lzy.upload_file(
                    file_path,
                    folder_id=dir_id,
                    callback=show_progress,  # 显示上传信息回调函数
                    uploaded_handler=handler  # 上传完成回调函数
                )
                if LanZouCloud.SUCCESS != uploadFlag:
                    recordError(uploadFlag)
            continue
        # 文件夹入队, 处理完文件后统一处理
        if os.path.isdir(file_path):
            toDealDirPath = os.path.join(dir_path, _file)
            dir_list.append(toDealDirPath)
    # 文件上传完成后, 将数据写入markdown文件
    writeDictToMd()
    # 处理文件后处理文件夹
    for _dir_path in dir_list:
        scanDir(_dir_path, dir_id)


if __name__ == '__main__':
    if UseMysql:
        # 连接数据库, 获取游标
        connect = pymysql.connect(**config)
        cursor = connect.cursor()
        scanDir(r'F:\01_软件,环境\01_工具', -1, writeToMysql=cursor)
        connect.commit()
        cursor.close()
        connect.close()
    else:
        scanDir(r'F:\01_软件,环境\01_工具', -1)
        # scanDir(r'F:\01_软件,环境\03_压缩', 5506472)
    Log(ignore_info)  # 将因为文件过大而忽略的文件记录到日志
    ...
    # 测试

# In[41]:

# 提交MySQL命令
# _cursor.execute("insert into mydata.soft(name, url) values(%s, %s)", (soft_name, soft_url))
# _cursor.execute("select url from mydata.soft where name=%s", ('WinRAR',))
# print(_cursor)
# print(_cursor.fetchone()[0])
# _cursor.execute("select url from mydata.soft where name=%s", ('Wi2nRAR',))
# print(_cursor)
# print(_cursor.fetchall())

# dir_path = r'F:\01_软件,环境\01_工具'
# parent_folder_name = os.path.basename(os.path.dirname(dir_path))
# print(parent_folder_name)
# print(os.path.basename(dir_path))
# print(os.path.dirname(dir_path))

# In[35]:


# a = [1, 2, 3, 4, 5]
# while len(a) > 0:
#     print(a)
#     print(a.pop(0))

# # 之前处理逻辑
# ```python
# for root, dirs, files in os.walk(dir_path):
#     for _file in files:
#         file_path = os.path.join(root, _file)
#         # 上传文件, 在回调函数中获取链接, 存储到全局变量内
#         lzy.upload_file(
#             file_path,
#             folder_id=5479523,
#             callback=show_progress,
#             uploaded_handler=handler
#         )
# ```

# In[21]:


# for file in lzy.get_file_list(5479523):
#     print(file.name)

# createFlag = lzy.mkdir(-1, 'test')
# if createFlag == LanZouCloud.SUCCESS:
#     print('创建成功')
# else:
#     print('创建失败')

# lzy.rename_dir(5479523, '操作')
# print(lzy.get_dir_list())

# os.path.getsize(r'D:\0a.dataout\test\soft\soft.html') / 1024
# # lzy.upload_file()
