# TS流爬虫
下载TS流视频，主要是https://swo.qjll.fun/cn/home/web/ 里面的视频

- 可以用ffmpeg直接下载m3u8链接（注意要找到完整的m3u8），他会自动解密，但是速度很慢
- cmd命令：ffmpeg -i https://abc.net/xx/xx/1000kb/hls/index.m3u8 out.mp4
- markdown：https://github.com/TMFfa/TS/blob/main/ffmpeg下载m3u8.md

- 该爬虫（注意成功案例是`下载后合并.py`，`spider.py`是失败案列，下载后还是乱码）先将ts流文件下载下来，index.m3u8和key.key也下载（key.key要改为key.m3u8），然后用ffmpeg合并
- cmd命令：ffmpeg -allowed_extensions ALL -i index.m3u8 -c copy out.mp4
- markdown：[ffmpeg合并M3U8加密的视频 ts 合并为 mp4.md](https://github.com/TMFfa/TS/blob/main/ffmpeg%E5%90%88%E5%B9%B6M3U8%E5%8A%A0%E5%AF%86%E7%9A%84%E8%A7%86%E9%A2%91%20ts%20%E5%90%88%E5%B9%B6%E4%B8%BA%20mp4.md)
