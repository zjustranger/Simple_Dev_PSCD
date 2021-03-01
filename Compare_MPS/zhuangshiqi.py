# test:装饰器的使用

def add_logfile(logfile='log1.txt'):
    def zhuangshi(func):
        def cailiao(*args):
            print('plan to be started!')
            print('the logfile is {}'.format(logfile))
            func(args)
            print('finished!')
        return cailiao
    return zhuangshi

@add_logfile('log2.txt')
def func1(*args):
    print('now func1 is running', args)

if __name__ == '__main__':
    func1('hello', 'hello2',['hello3', 'hello4'])