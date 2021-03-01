import pyautogui as py
from time import sleep
import tkinter as tk

NeedControl = False

def clicker(times=100, wait2start = 5):
    sleep(wait2start)
    counter = 1
    while counter <= times:
        py.press('enter')
        sleep(0.01)
        counter += 1


if __name__ == '__main__':
    clicker(8)



def stop_moving():
    global NeedControl
    NeedControl = False

class Operator:
    def __init__(self, sleeptime = 0.5):
        self.__sleeptime = sleeptime
    def action(self):
        # py.press('down', presses=2)
        py.moveRel(-5,0,0.1)
        py.moveRel(5,0,0.1)
        py.press('space', presses=3)
    def wait(self):
        sleep(self.__sleeptime)

# yeQiuQuan = Operator(5)
# sleep(5)
# for i in range(200):
#     print(i)
#     yeQiuQuan.action()
#     yeQiuQuan.wait()


class Operator1(Operator):
    def action(self):
        py.press('space', presses=100)

# oper1 = Operator1()
# sleep(5)
# oper1.action()
# sleep(1)
# oper1.action()
# sleep(1)
# oper1.action()
















