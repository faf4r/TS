# 直接用调用cmd用ffmpeg直接下载
# cmd命令：ffmpeg -i https://abc.net/xx/xx/1000kb/hls/index.m3u8 out.mp4

import subprocess

url = 'https://swo.qjll.fun/cn/home/web/index.php/vod/play/id/70111/sid/1/nid/1.html#'
out_name = 'out.mp3'
cmd = f'ffmpeg -i {url} "{out_name}"'
subprocess.call(cmd)
