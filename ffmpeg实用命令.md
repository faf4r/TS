# ffmpeg实用命令

```shell
ffmpeg -i input.mp4 output.mp3 # 从视频中抽取音频
ffmpeg -i input.mp4 -ss 00:01:20 -c copy -t 10 output.mp4 #从00:01:20开始截取10s钟视频输出
ffmpeg -i input.mp4 -c:v copy -an input-no-audio.mp4 #去除视频中音频
ffmpeg -i input-no-audio.mp4 -i input.mp3 -c copy output.mp4 #合并音视频
```



## ffmpeg直接下载m3u8（网上的）

#### 下载视频所有的ts切片文件

​        一般的思路是，想办法把所有的ts切片文件下载下来，然后合成一个完整的视频。
​		然而，配合`xx.m3u8`播放列表文件，我们可以直接用`ffmpeg`在线下载播放列表中所有的视频，然后直接用ffmpeg合并为一个视频。
我们就直接执行这一句命令即可：

```shell
$ ffmpeg -i <m3u8-path> -c copy OUTPUT.mp4

$ ffmpeg -i <m3u8-path> -vcodec copy -acodec copy OUTPUT.mp4

# 例如：
$ ffmpeg -i https://v6.438vip.com/2018/10/17/3JAHPTdvPhQb9LrE/playlist.m3u8 -c copy  OUTPUT.mp4
```

## 更简洁的直接下载方法

**当然了，最简单的办法当然是直接从网上获取视频，免去下载视频流的步骤，命令如下**

**-i后面指定m3u8文件的URI**

**out.mp4是生成文件名，默认是命令行的当前目录，可以通过绝对路径指定具体位置，如G:\abc\xxx.mp4**

```
ffmpeg -i https://abc.net/xx/xx/1000kb/hls/index.m3u8 out.mp4
```



### TS流视频合并


下载完所有 ts 流文件之后，开始合成，祭出大杀器：ffmpeg，利用 mpeg concat 分离器，先在 ts 文件目录下创建一个文本文件 filelist.txt，即 ts 流文件的顺序列表：

file ‘out000.ts’
file ‘out001.ts’
file ‘out002.ts’
…
file ‘out1349.ts’

```shell
ffmpeg -f concat -i filelist.txt -c copy output.mkv
```

`filelist`是ts文件合并的顺序

