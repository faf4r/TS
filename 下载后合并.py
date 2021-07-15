# 因为ffmpeg自动下载太慢了，所以这个程序试试多线程下载所以ts，然后再用ffmpeg合并
import os
import re
import requests
from lxml import etree
from threading import Thread
import subprocess

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
        self.domain, self.m3u8_url, self.title = self.m3u8()
        self.key_url = self.key()
        os.chdir(self.title)
        self.log = []

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

    def key(self):
        r = requests.get(self.m3u8_url, self.headers)
        # print(r.text)
        key_url = re.findall('#EXT-X-KEY:METHOD=.*?,URI="(.*?)"', r.text)[0]
        return self.domain + key_url

    def init(self):  # 先试试不讲uri改成网络地址的方法
        os.makedirs(self.title, exist_ok=True)
        m3u8 = requests.get(self.m3u8_url, self.headers)
        data = m3u8.text.replace('.key', '.m3u8')
        with open('./'+self.title+'/index.m3u8', 'w') as f:
            f.write(data)
        key = requests.get(self.key_url, self.headers)
        with open('./'+self.title+'/key.m3u8', 'w') as f:
            f.write(key.text)
        print('Initialized\n', '-'*20)

    def get_all_url(self):
        r = requests.get(self.m3u8_url, self.headers)
        # print(r.text)
        data = re.findall('\n(.*?.ts)', r.text)
        # print(data)
        urls = []
        for i in data:
            url = self.domain + i
            urls.append(url)
        # print(urls)
        return urls

    def download_ts(self, urls, thread_id='default thread'):
        start = 1
        end = len(urls)
        for url in urls:
            print(thread_id, f': download {start}/{end}')
            try:
                r = requests.get(url, self.headers)
                with open(url.split('/')[-1], 'wb') as f:
                    f.write(r.content)
            except:
                print(f'failed to download {url}')
                self.log.append(url)
            start += 1

    def download_thread(self, thread_num=5):
        urls = self.get_all_url()
        part = len(urls) // thread_num
        url_list = []
        for i in range(thread_num-1):
            url_list.append(urls[i*part:(i+1)*part])
        url_list.append(urls[(thread_num-1)*part:])
        print(f'There are totally {len(urls)} ts files，and {thread_num}threads.')
        print(url_list)

        threads = []
        for i in range(thread_num):
            t = Thread(target=self.download_ts, args=(url_list[i], f'thread{i+1}'))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print('threads finished')
        if self.log:
            print(f'failed to download {len(self.log)} ts files:')
            for i in self.log:
                print(i)
            print('-'*100)
            self.redownload_log()

    def redownload_log(self):
        start = 1
        end = len(self.log)
        print(f'redownloading failed urls, {end} files...')
        for url in self.log:
            try:
                print(f'\rdownloading...{start}/{end}', end='')
                r = requests.get(url, self.headers)
                with open(url.split('/')[-1], 'wb') as f:
                    f.write(r.content)
                self.log.remove(url)
            except:
                print(f'\nfailed to download {url}')
            start += 1

    def cmd(self):
        cmd = f'ffmpeg -allowed_extensions ALL -i index.m3u8 -c copy "#{self.title}.mp4"'
        subprocess.call(cmd)


if __name__ == '__main__':
    ts = TS(basic_url)
    ts.init()
    ts.cmd()
