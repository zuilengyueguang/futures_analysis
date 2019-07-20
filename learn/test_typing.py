from typing import List, Tuple, Dict
def add(a:int, string:str, f:float, b:bool) -> Tuple[List, Tuple, Dict, bool]:
    list1 = list(range(a))
    tup = (string, string, string)
    d = {"a":f}
    bl = b
    return list1, tup, d,bl
print(add(5,"hhhh", 2.3, False))

'''
typing 模块为了解决python函数中基本类型的问题
1. python代码写的多了之后，后续不知道要传入什么参数，返回什么参数
2. 使用typing可以在函数上面定义具体的传入类型和返回值类型
3. 这个功能太好用了，大大的增加了这门语言的可读性
'''

class animal:
    def spreak(self, string:str):
        print("spreak")

# 有了类型，增加了可读性，也让代码变得更加严谨，算是python3.5很不错的更新
def sssp(a:animal):
    a.spreak("123")
a=animal()
sssp(a)