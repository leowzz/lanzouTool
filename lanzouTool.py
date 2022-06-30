#!/usr/bin/env python
# coding: utf-8

import os
import time
import hashlib

from lanzou.api import LanZouCloud

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

# 脚本初始化区域
fileNameUrlDict = {}
# md_path = r'D:\0a.dataout\test\lanzouTool\fileNameUrl.md'
except_dir = ['便携工具', '插件包', '脚本']
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
time_ = time.strftime('%Y-%m-%d_%H%M%S', time.localtime(time.time()))
md_path = time_ + '.md'
big_rec = time_ + 'bigFiles.txt'
log_path = time_ + '.txt'
md_path = os.path.join(log_dir, md_path)  # markdown文件
big_rec = os.path.join(log_dir, big_rec)  # 大文件记录
log_path = os.path.join(log_dir, log_path)  # 日志路径
ignore_info = f'\n\n[{"*" * 30} 文件过大，跳过 {"*" * 30}]\n\n'
BIG_FILE = -1
FILE_EXISTS = -2
FILE_NOT_EXISTS = -3
lzy = LanZouCloud()
# 使用131的cookie登录
lzy.login_by_cookie(cookie131)


def split_name_type(file_path):
    """分割文件路径, 返回文件类型, 文件名, 文件夹路径"""
    splitext = os.path.splitext(file_path)
    file_name = os.path.basename(splitext[0])
    file_type = splitext[1][1:]
    return file_name, file_type


def writeToFile(file_path, content):
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
        return BIG_FILE
    else:
        file_size_MB = f'{file_size_MB:.2f}'
        return file_size_MB


def getFullFileMd5(file_path):
    # 计算文件md5
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def getFileMd5(file_path):
    # 计算文件md5
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        data = f.read(4096)
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


def workingWithFolders(dir_path, parent_dir_id=-1, passwd=default_password):
    """
    获取所有文件夹, 存在则获取信息, 不存在则创建
    :param dir_path: 文件夹路径
    :param parent_dir_id: 父文件夹id
    :param passwd: 默认密码
    :return: 文件夹编号, 文件夹链接
    """
    folder_name = os.path.basename(dir_path)
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


def upload_local_file(lz_files, dir_id, file_path, ):
    file_name = os.path.basename(file_path)
    lz_info = lz_files.find_by_name(file_name)  # 判断目标文件夹下是否已有同名文件
    if lz_info is not None:
        handler(lz_info.id, True)
        return FILE_EXISTS
    file_size = isBigFile(file_path)
    # 大文件 存储日志, 直接跳过
    if file_size == BIG_FILE:
        return BIG_FILE
    upload_flag = lzy.upload_file(
        file_path,
        folder_id=dir_id,
        callback=show_progress,  # 显示上传信息回调函数
        uploaded_handler=handler  # 上传完成回调函数
    )
    return upload_flag
    # return LanZouCloud.SUCCESS


def scanDir(dir_path, parent_dir_id=-1, level='#'):
    """
    遍历文件夹, 并上传文件
    :param dir_path: 文件夹路径
    :param parent_dir_id: 文件夹id
    :param level: 文件夹等级, 用于输出到md时的标题等级
    """
    # 获取目录名
    folder_name = os.path.basename(dir_path)
    dir_id, dir_url = workingWithFolders(folder_name, parent_dir_id)
    lz_files = lzy.get_file_list(dir_id)
    # 将父目录名写入markdown
    writeToFile(md_path, f'{level} [{folder_name}]({dir_url})\n\n')
    # 文件名-链接 字典初始化
    global fileNameUrlDict
    fileNameUrlDict = {}
    dir_list = []  # 待处理文件夹列表
    for _file in os.listdir(dir_path):
        # 处理文件路径
        file_path = os.path.join(dir_path, _file)
        # 文件
        if os.path.isfile(file_path):
            upload_flag = upload_local_file(lz_files, dir_id, file_path)
            if LanZouCloud.SUCCESS == upload_flag:
                Log(f'{_file} 上传成功✔')
            elif BIG_FILE == upload_flag:
                writeToFile(big_rec, f"{file_path}\n")
            elif FILE_EXISTS == upload_flag:
                Log(f'{_file} 已存在')
            elif LanZouCloud.FAILED == upload_flag:
                Log(f'{"*" * 20} {_file} 未上传, Error: 上传失败')
            elif LanZouCloud.NETWORK_ERROR == upload_flag:
                Log(f'{"*" * 20} {_file} 未上传, Error: 网络异常')
            elif LanZouCloud.PATH_ERROR == upload_flag:
                Log(f'{"*" * 20} {_file} 未上传, Error: 路径错误')
        # 文件夹入队, 处理完文件后统一处理
        if os.path.isdir(file_path):
            # 排除部分指定文件夹
            if _file in except_dir:
                continue
            toDealDirPath = os.path.join(dir_path, _file)
            dir_list.append(toDealDirPath)
    # 文件上传完成后, 将fileNameUrlDict写入markdown文件
    writeDictToMd()
    # 处理文件后处理文件夹
    for _dir_path in dir_list:
        scanDir(_dir_path, dir_id, level + '#')


if __name__ == '__main__':
    scanDir(scanPath, -1, '#')
    Log(ignore_info)  # 将因为文件过大而忽略的文件记录到日志
    # scanDir(r'F:\01_软件,环境\03_压缩', 5506472)
    ...
