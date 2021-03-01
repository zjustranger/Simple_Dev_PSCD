import requests
import urllib.parse
from time import sleep

class WeChatPusher:
    '''
        此通用类用于往自己的微信接口测试号上实时推送消息，有两个必填参数。格式范例如下:
        title: '微信推送标题' (Mandatory)
        content: '微信推送内容，支持Markdown语法' (Mandatory)
        usingvolvoproxy: '布尔值，默认True，从内网发起http request需要走代理' (Optional)
    '''
    def __init__(self, title, content, usingvolvoproxy = False):
        self.url_common = 'https://sctapi.ftqq.com/SCT546TUleK318ftXxwbmXw57aQBIc3.send?title={}&desp={}'
        self.proxies = {'http': '10.240.2.200:83', 'https': '10.240.2.200:83'}
        self.title = title
        self.content = content
        self.usingvolvoproxy = usingvolvoproxy
        self.url = self.url_common.format(urllib.parse.quote(self.title), urllib.parse.quote(self.content))
    def send(self):
        if self.usingvolvoproxy:
            self.r = requests.post(self.url, proxies=self.proxies)
        else:
            self.r = requests.post(self.url)


if __name__ == '__main__':
    wechat = WeChatPusher('小伙砸，该喝水啦！！', '离上次喝水时间已过去2小时')
    wechat.send()