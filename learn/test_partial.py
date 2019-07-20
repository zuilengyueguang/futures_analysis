from functools import partial
def add(*args,**kwargs):
    for n in args:
        print(n)
    for k,v in kwargs.items():
        print('%s,%s'%(k,v))
add(1,3,4,v1=10,v2=20)
print(20*'*')
add100=partial(add,100,k1=10,k2=20)
add100(1,3,4,k1=20)
print(20*'*')
add100(1,3,4,k3=20)

class A:
    a=__module__

print(A().a)

'''
partial 是 functools 的内部方法，叫做偏函数，是原有函数的一种扩展
1. partial 第一个参数是原有的函数
2. partial 第二个参数是扩展的自定义参数，也是新函数自带的默认参数
3. partial 第三个参数是用来扩展dict类型参数，如果新函数输入了参数，可以覆盖的

module 如果是顶层模块，输出的是main
    如果是底层模块，输出的是模块名称，也就是包名
'''