from selenium import webdriver
from PyQt5.QtWidgets import QMainWindow, QTextEdit

import time, json


class PanicBuying():
    def __init__(self):
        self.start_kg = False
        self.close_all = False

    def start(self, name, driver, ms, url, items, time_wait, wait, refresh):
        '''
        开始自动多线程抢购
        '''
        try:
            # 超时
            driver.set_page_load_timeout(5000)  # 防止页面加载个没完
            driver.get(url)
            textTrues = []  # 存已经找到的目标
            # 判断是否需要等待
            if wait == True:
                # 如果需要则循环等待这个时间到来,注意了这是电脑时间
                ms.log_add.emit(f'浏览器:{name} 启动时间为:{time_wait},别忘记了点全部开始')
                while True:
                    time.sleep(0.1)
                    if time.strftime("%H:%M:%S", time.localtime()) == time_wait:
                        ms.log_add.emit(f'浏览器:{name} 时间到达!开始运行!')
                        break

            # 判断是否需要刷新
            if refresh == True:
                ms.log_add.emit(f'浏览器:{name} 刷新!')
                driver.refresh()

            def element_css(selector_text: str, wz_text: str):
                '''
                利用css寻找目标,然后操作
                :return:
                '''
                an = driver.find_element_by_css_selector(selector_text)
                # 判断操作类型
                if wz_text.find('$$') != -1:
                    # 输入文字
                    wz = wz_text.replace('$$', '')
                    if wz_text not in textTrues:
                        an.send_keys(wz)
                        ms.log_add.emit(f'浏览器:{name} 成功帮忙输入了{wz}')
                        return True

                else:
                    # 点击按钮
                    an.click()
                    if wz_text not in textTrues :
                        ms.log_add.emit(f'浏览器:{name} 通过CSS定位到{wz_text}按钮')
                        textTrues.append(wz_text)
                return False


            def element_text(selector_text: str):
                '''
                利用text寻找目标,然后进行操作
                :return:
                '''
                an = driver.find_element_by_xpath(f"//*[text()='{selector_text}']")
                an.click()
                if selector_text not in textTrues:
                    ms.log_add.emit(f'浏览器:{name} 通过名字定位到{selector_text}按钮')
                    textTrues.append(selector_text)

            def find_isTrue(wz_text: str):
                '''
                判断是否是成功
                :return:
                '''
                #如果在点击成功列表里面,则发出点击成功信号
                if wz_text in textTrues:
                    ms.log_add.emit(f'浏览器:{name} 点击{wz_text}按钮成功!')
                    return True
                else:
                    return False
            # 正式开始
            for item in items:
                print(item)
                #如果暂停了,就卡死不动
                while self.start_kg == False:
                    # 判断是否要退出
                    if self.close_all == True:
                        ms.log_add.emit(f'浏览器:{name} 已被强制关闭!')
                        return
                time.sleep(0.2)
                # 优先用css来定位
                if item['css'] != '' and item['css'] != None:
                    # 尝试用css定位,如果定位成功则点击,如果定位失败则尝试使用text
                    # 直到点击成功后再下一个目标
                    while True:
                        time.sleep(0.2)
                        # 如果暂停了,就卡死不动
                        while self.start_kg == False:
                            # 判断是否要退出
                            if self.close_all == True:
                                ms.log_add.emit(f'浏览器:{name} 已被强制关闭!')
                                return
                            time.sleep(0.2)
                        try:
                            # 尝试寻找并且尝试操作 如果是输入框,,输入完成后就跳出
                            if element_css(item['css'], item['text'])==True:
                                break
                        except:
                            try:
                                # 尝试寻找并且尝试操作
                                element_text(item['text'])
                            except:#操作失败,可能是没找到或者是已经点成功了
                                # 判断是否是成功
                                if find_isTrue(item['text']) == True:
                                    break
                # 如果没有css则考虑直接使用text来搜索定位.
                elif item['text'] != '' and item['text'] != None:
                    while True:
                        # 如果暂停了,就卡死不动
                        while self.start_kg == False:
                            # 判断是否要退出
                            if self.close_all == True:
                                ms.log_add.emit(f'浏览器:{name} 已被强制关闭!')
                                return
                            time.sleep(0.2)
                        time.sleep(0.2)
                        try:
                            # 尝试寻找并且尝试操作
                            element_text(item['text'])
                        except:#操作失败,可能是没找到或者是已经点成功了
                            # 判断是否是点击成功
                            if find_isTrue(item['text']) == True:
                                break
        except:
            ms.log_add.emit(f'浏览器:{name} 意外关闭!')
