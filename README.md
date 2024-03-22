# Youtobe 视频下载器

* 项目使用的 petite-vue + FastAPI + websocket + youtube_dl + cv2

使用方法

1 安装 python3.8+ 依赖，另外需要安装ffmpeg

```
pip install -r requirements.txt 
uvicorn main:app --reload
```

2 打开网页 http://127.0.0.1:8000/

3 输入自定义下载的名字，和 youtube网址