# 这是我的初级想法，把每个ts下载下来，直接添加的文件末尾，结果是不行的，因为他有加密
# 目前最简单的方法是直接用ffmpeg下载：ffmpeg -i https://abc.net/xx/xx/1000kb/hls/index.m3u8 out.mp4

import re
import requests
from lxml import etree

basic_url = 'https://swo.qjll.fun/cn/home/web/index.php/vod/play/id/70111/sid/1/nid/1.html#'
xpath = '//*[@id="bof"]/div[2]/script[1]/text()'

url1 = 'https://videozm.whqhyg.com:8091/20210706/MOoEYW3x/index.m3u8'
url2 = 'https://videozm.whqhyg.com:8091/20210706/MOoEYW3x/1000kb/hls/index.m3u8'


class TS:
    def __init__(self, html_url):
        self.html_url = html_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }

    def m3u8(self):
        r = requests.get(self.html_url, self.headers)
        html = etree.HTML(r.text)
        data = html.xpath('//div[@id="bof"]/div[2]/script[1]/text()')

        title = html.xpath('//*[@id="bof"]/div[1]/h2/text()')[0]
        print('title:', title)
        m3u8_url = re.findall('"url":"(.*?)"', data[0])[0]
        # print(m3u8_url)
        m3u8_url = m3u8_url.replace('\\', '')
        # print(m3u8_url)
        r = requests.get(m3u8_url, self.headers)
        # print(r.text)
        domain = m3u8_url.strip('index.m3u8')
        target = r.text.split('\n')[2]
        m3u8_url = domain + target
        print('m3u8 url:', m3u8_url)
        domain = m3u8_url.strip('index.m3u8')
        return domain, m3u8_url, title

    def get_all_url(self):
        domain, m3u8, title = self.m3u8()
        r = requests.get(m3u8, self.headers)
        # print(r.text)
        data = re.findall('\n(.*?.ts)', r.text)
        # print(data)
        urls = []
        for i in data:
            url = domain + i
            urls.append(url)
        # print(urls)
        return title, urls

    def run(self):
        title, urls = self.get_all_url()
        i = 1
        num = len(urls)
        with open(title + '.ts', 'ab') as f:
            for url in urls:
                print(f'\rdownloading...{i}/{num}', end='')
                r = requests.get(url, self.headers)
                f.write(r.content)
                i += 1
        print()
        print(urls[0].split('/')[-4] + '.ts    下载完成')


if __name__ == '__main__':
    ts = TS(basic_url)
    ts.run()
