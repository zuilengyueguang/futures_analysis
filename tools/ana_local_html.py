import sys
import os
import os.path

from html.parser import HTMLParser


# 定义HTMLParser的子类,用以复写HTMLParser中的方法
class MyHTMLParser(HTMLParser):
    # 构造方法,定义data数组用来存储html中的数据
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = ''
        self.flag = False
        # self.index = 0

    # 覆盖starttag方法,可以进行一些打印操作
    def handle_starttag(self, tag, attrs):
        # pass
        # print("遇到起始标签:{} 开始处理:{}".format(tag, tag))
        # if tag == 'tr':
        #    self.index = 0
        if tag == 'div':
            for k, v in attrs:  # 遍历div的所有属性以及其值
                if k == 'class' and v == 'cell':  # 确定进入了<div class='cell'>
                    # self.index = self.index + 1
                    self.flag = True
                    self.data = self.data + '"'
                    return

    # 覆盖endtag方法
    def handle_endtag(self, tag):
        # pass
        # print("遇到结束标签:{} 开始处理:{}".format(tag, tag))
        if self.flag == True:
            self.data = self.data + '",'
            self.flag = False
            return
        # 遇到tr结束,增加一个回车
        if tag == 'tr':
            self.data = self.data + '\n'

    # 覆盖handle_data方法,用来处理获取的html数据,这里保存在data数组
    def handle_data(self, data):
        # pass
        # print("遇到数据:{} 开始处理:{}".format(data, data))
        if (self.flag == True):
            data = data.replace('\n', '')  # 替换字段中的回车
            data = data.replace('  ', '')  # 替换字段中的连续两个空格
            self.data = self.data + data


def read_file(filename):
    fp = open(filename, 'r', encoding='gbk')
    content = fp.read()
    fp.close()
    return content


def write_file(filename, content):
    fp = open(filename, 'a+', encoding='gbk')
    fp.write(content)
    fp.close()


def main():
    csv_file = 'D://1.csv'
    # 会员信息
    # write_file(csv_file,'"序号","账号","账号状态","登录IP","最近登录时间","登录次数","上级账号","交易次数","交易流水","账号余额","姓名"\n')
    # 资金账户信息
    write_file(csv_file, '"序号","卡号/账户","开户行/平台","余额","流水","所在地","姓名","用户名","手机号","qq","邮箱","注册IP","注册时间"\n')

    parser = MyHTMLParser()
    for i in range(1, 3):
        html_file = 'D://%d.html' % i
        print(html_file)
        if os.path.exists(html_file) == False:
            print(html_file + '文件不存在!')
            return
        content = read_file(html_file)
        print(content)
        parser.feed(content)
        # 对解析后的数据进行相应操作
        # print(parser.data)
        write_file(csv_file, parser.data)
        parser.close()


#main()

def test1():
    parser = MyHTMLParser()
    html_file='D://1.html'
    content = read_file(html_file)
    print(content)
    parser.feed(content)
    # 对解析后的数据进行相应操作
    #print(parser.data)

test1()