# 因为ffmpeg自动下载太慢了，所以这个程序试试多线程下载所以ts，然后再用ffmpeg合并
# 该爬虫用于下载 https://swo.qjll.fun/cn/home/web/ 的视频

import os
import re
import requests
from lxml import etree
from threading import Thread
import subprocess


class TS:
    """
    该类用于下载host中的视频，需要传入视频播放页的URL。
    该类会自动解析找到正确的m3u8链接，并多线程下载ts流视频，最后调用ffmpeg合并。
    下载视频会创建视频名的文件夹，下载成功的视频会以#开头放在里面（里面还有很多ts流文件，可以忽略）
    使用条件：
        安装requests第三方库
        安装ffmpeg并配置环境变量  安装地址：http://ffmpeg.org/
    对象属性：
        html_url:传入的播放页地址
        headers:默认的User-Agent
        domain:m3u8的域名，每个ts文件或key什么的都要加上domain合成完整的URL
        m3u8_url:解析出的正确的m3u8 URL
        title：从网页解析出的视频标题，文件和文件夹以此命名
        key_url:m3u8会加密，ffmpeg需要key解密，这个key_url就是解析出来的key的地址
        log:这是下载ts流时记录下载失败的列表，之后可以重新下载或手动下载
    """
    host = 'https://swo.qjll.fun/cn/home/web/'

    def __init__(self, html_url):
        self.html_url = html_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
        self.domain, self.m3u8_url, self.title = self.m3u8()
        self.key_url = self.key()
        os.chdir(self.title)  # 注意放这里会将工作目录改变到ts流文件处
        self.log = []

    def m3u8(self):
        """
        初始化过程中解析网页找到正确的m3u8 url和domain、title
        :return: domain, m3u8_url, title
        """
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
        """
        初始化过程中解析key的地址
        :return: 完整的key URL
        """
        r = requests.get(self.m3u8_url, self.headers)
        # print(r.text)
        key_url = re.findall('#EXT-X-KEY:METHOD=.*?,URI="(.*?)"', r.text)[0]
        return self.domain + key_url

    def init(self):  # 先试试不讲uri改成网络地址的方法
        """
        手动调用的初始化，
        该过程会下载m3u8文件并命名为index.m3u8（习惯命名），下载key.key并重命名为key.m3u8（因为ffmpeg只识别这个）
        下载的m3u8会将网络请求到的key的URI替换为本地的key文件，即key.m3u8
        注意：因为这些文件里面的ts流文件命名以及key文件命名都是相对路径，所以才会有把文件工作路径转到目标文件夹里面去
        :return: None
        """
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
        """
        请求m3u8并解析出所有的ts流文件的url
        :return: 完整的所有的ts流文件的url的列表
        """
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
        """
        下载一个列表中所以ts文件的函数，列表中可以不是全部URL，该函数用于构成多线程
        这里下载失败的URL会存入log属性的列表中
        :param urls: 一个包含ts文件URL的列表
        :param thread_id: 因为是要多线程下载，所以这里就要给线程命个名，便于查看下载进度
        :return: None
        """
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
        """
        多线程下载器，这里会将完整的全部URL的列表拆分成指定线程数，然后进行多线程下载
        下载完成后会重新下载log里面下载失败的URL
        :param thread_num: 需要的线程数，默认为5，根据自己电脑配置决定
        :return: None
        """
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
        """
        这是重新下载下载log中失败的URL
        :return: None
        """
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
        """
        这里调用cmd使用ffmpeg对所有ts流合并，要确保里面有index.m3u8和key.m3u8
        :return: None
        """
        cmd = f'ffmpeg -allowed_extensions ALL -i index.m3u8 -c copy "#{self.title}.mp4"'
        subprocess.call(cmd)


if __name__ == '__main__':
    basic_url = 'https://swo.qjll.fun/cn/home/web/index.php/vod/play/id/70111/sid/1/nid/1.html#'
    # 下面这些是处理过程的中间URL，没用，看看就好了
    url1 = 'https://videozm.whqhyg.com:8091/20210706/MOoEYW3x/index.m3u8'
    url2 = 'https://videozm.whqhyg.com:8091/20210706/MOoEYW3x/1000kb/hls/index.m3u8'

    # 调用的时候记得一定要先调用init()
    ts = TS(basic_url)
    ts.init()
    ts.download_thread()
    ts.cmd()
