# -- coding: UTF-8 --
import os

'''
文件夹下面所有的HTML文件后缀名改为 doc
'''
def htmlToDoc(path):
    files = os.listdir(path)
    for f in files:
        # 调试代码的方法：关键地方打上print语句，判断这一步是不是执行成功
        # print(f)
        if f.endswith(".html"):
            print("原来的文件名字是:{}".format(f))
            # 找到老的文件所在的位置
            old_file = os.path.join(path, f)
            print("old_file is {}".format(old_file))
            # 指定新文件的位置，如果没有使用这个方法，则新文件名生成在本项目的目录中
            new_name = f[:-5] + '.doc'
            new_file = os.path.join(path, new_name)
            print("File will be renamed as:{}".format(new_file))
            os.rename(old_file, new_file)
            # print("修改后的文件名是:{}".format(f))

def docToHtml(path):
    files = os.listdir(path)
    for f in files:
        # 调试代码的方法：关键地方打上print语句，判断这一步是不是执行成功
        # print(f)
        if f.endswith(".doc"):
            print("原来的文件名字是:{}".format(f))
            # 找到老的文件所在的位置
            old_file = os.path.join(path, f)
            print("old_file is {}".format(old_file))
            # 指定新文件的位置，如果没有使用这个方法，则新文件名生成在本项目的目录中
            new_name = f[:-4] + '.html'
            new_file = os.path.join(path, new_name)
            print("File will be renamed as:{}".format(new_file))
            os.rename(old_file, new_file)
            # print("修改后的文件名是:{}".format(f))

path = "C://Users//最冷月光//Desktop//资料//20191203回测报告"
docToHtml(path)