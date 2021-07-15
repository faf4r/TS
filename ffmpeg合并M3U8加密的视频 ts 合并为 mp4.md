# ffmpeg合并M3U8加密的视频 ts 合并为 mp4

![img](https://csdnimg.cn/release/blogv2/dist/pc/img/original.png)

[Jioho_](https://blog.csdn.net/Jioho_chen) 2020-02-23 22:28:22 ![img](https://csdnimg.cn/release/blogv2/dist/pc/img/articleReadEyes.png) 9545 ![img](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect.png) 收藏 14

分类专栏： [开发工具](https://blog.csdn.net/jioho_chen/category_7791360.html) 文章标签： [ffmpeg](https://www.csdn.net/tags/MtTaEg0sMzMyNDYtYmxvZwO0O0OO0O0O.html) [m3u8](https://www.csdn.net/tags/MtTaEg0sMjMwNjItYmxvZwO0O0OO0O0O.html)

版权

[![img](https://img-blog.csdnimg.cn/20201014180756922.png?x-oss-process=image/resize,m_fixed,h_64,w_64)开发工具](https://blog.csdn.net/jioho_chen/category_7791360.html)专栏收录该内容

44 篇文章0 订阅

订阅专栏

> 文章引用于 [ffmpeg 合并 m3u8 ts key 文件 解决 Invalid data found when 错误](http://www.v218.com/a139)

> 如果文件没加密，可以直接用 ffmpeg -i xxx.m3u8 -vcodec copy -acodec copy xxx.mp4

> 之前也写过一篇文章，使用`ffmpeg`下载 M3U8 资源的视频。今天接着来拓展一下这个下载视频

## 寻找资源

要想下载 M3U8 的资源，最起码得找到下载的链接，可能这个非常好找了，找到控制台的 `NetWork` 查看请求就行了。
可是这有一点非常不好的就是，使用 ffmpeg 去下载，只能一个个资源去请求，并且非常慢，经常还有可能请求失败(资源是可以访问到的，可是 ffmpeg 就卡住了)

> 解决方案：chrome 插件 [猫抓](https://chrome.google.com/webstore/detail/猫抓/jfedfbgedapdagkghmgibemcoggfppbb)
> 当他嗅探到资源后，就会都列出来
> ![https://raw.githubusercontent.com/Jioho/img/master/ffmpeg/20200223220327.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0ppb2hvL2ltZy9tYXN0ZXIvZmZtcGVnLzIwMjAwMjIzMjIwMzI3LnBuZw?x-oss-process=image/format,png)
> 而我通常用 IDM 把列出的资源一下子都下载下来

### 资源合并为 mp4

留意上面的图，这段 m3u8 是一个 key 的文件，就是加密的文件。还好 ffmpeg 可以自动识别 key 文件并且解密文件，可是这一步有点曲折

我们先把 m3u8 的源文件下载下来，把 ts 文件都下载好，放在同一个文件夹
![https://raw.githubusercontent.com/Jioho/img/master/ffmpeg/20200223221735.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0ppb2hvL2ltZy9tYXN0ZXIvZmZtcGVnLzIwMjAwMjIzMjIxNzM1LnBuZw?x-oss-process=image/format,png)

然后打开 `m3u8` 文件，找到 `key.key` 的配置，改为线上的 key，而不是读取本地的 key 。虽然我到现在也没搞懂这是为什么~

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:4
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-KEY:METHOD=AES-128,URI="https://xxxx/key.key" # 注意URI这里，改成线上的key的域名链接
#EXTINF:3.336667,
#EXTINF:1.668333,
clvHz13123499.ts
#EXTINF:2.035367,
clvHz13123500.ts
#EXT-X-ENDLIST
1234567891011
```

### 解密文件，合并 ts 为 mp4

使用命令

```sh
ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i index.m3u8 -c copy out.mp4
1
```

运行后可能会发现报错:
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200227221035211.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0ppb2hvX2NoZW4=,size_16,color_FFFFFF,t_70)
看到这个错误其实只需要在 `protocol_whitelist` 后面补上`https`。后面报错提示什么就补上什么，因为对应的 m3u8 需要这几种下载方式

于是命令改成如下：

```sh
ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp,https" -i index.m3u8 -c copy out.mp4
1
```

如果还发现报错是:`Invalid data found when` 这样的，就是因为你的 key 没有改成线上域名的 key，改了重新试下就行了

然后发现 ffmpeg 合并的飞快，比起直接用 ffmpeg 下载快多了！



### 另一个版本的合并

**如果你的文件是加密的，那么你还需要一个key文件，可以文件下载的方法和m3u8文件类似，你把m3u8.m3u8换成key.key就能下载了。将下载好的所有的ts文件、m3u8.m3u8、key.key放到一个文件夹中，将m3u8.m3u8改名为`index.m3u8`(习惯)，将key.key改名为`key.m3u8`。更改index.m3u8也就是之前的m3u8.m3u8，将URI改为你本地路径的key文件，将所有ts也改为你本地的路径**

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:13
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-KEY:METHOD=AES-128,URI="e:/20180125/key.m3u8"
#EXTINF:12.5,
e:/20180125/GBDYO3576000.ts
#EXTINF:12.5,
e:/20180125/GBDYO3576001.ts
#EXTINF:12.5,
e:/20180125/GBDYO3576002.ts
123456789101112
```

**接下来还需要下载一款工具[ffmpeg](https://ffmpeg.zeranoe.com/builds/)，下载Static的那个版本就可以，然后配置环境变量Path,在Path后面直接添加你ffmpeg的安装目录加上/bin就可以了，安装完成之后重启一下，重启之后打开你index.m3u8所在的文件执行**

```shell
ffmpeg -allowed_extensions ALL -i index.m3u8 -c copy out.mp4
```

#### # 经测试，上述命令为正解，注意是index.m3u8和key.m3u8

如果报错了执行

```shell
ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i index.m3u8 -c copy out.mp4
```

如果这里报错了，那么打开你的index.m3u8文件，修改URI的路径为网络路径（你下载时的路径），然后执行

```shell
ffmpeg -protocol_whitelist "file,http,crypto,tcp" -i index.m3u8 -c copy out.ts
```

