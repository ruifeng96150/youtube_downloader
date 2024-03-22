import youtube_dl
import cv2
import os
import datetime
import time


def cv_imwrite(savePath, thumbnail):
    """fixbug:保存带中文路径的图片"""
    cv2.imencode(".jpg", thumbnail)[1].tofile(savePath)  # 保存图片


def get_directory_info(apath):
    """
    获取下载的文件列表
    output_path = "./output"
    data = get_directory_info(output_path)
    data
    """
    directory_info = []

    def parse_note_file(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()

        info = {}
        for line in lines:
            key, value = line.strip().split(": ", 1)
            info[key] = value

        return info

    for root, dirs, files in os.walk(apath):
        for file in files:
            if file == "note.txt":
                file_path = os.path.join(root, file)
                info = parse_note_file(file_path)
                info["path"] = root.replace(apath + "\\", "")
                directory_info.append(info)

    return directory_info


def down_ytb_video(title, url, output_path):
    """
    下载视频
     url="https://www.youtube.com/shorts/mhoolQBAtdM"
     title='hello'
     output_path="./output"
     down_ytb_video(url,title,output_path)

    """
    base_path = f"{output_path}/{title}"
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    else:
        # raise FileExistsError(f"目录{title}已经存在")
        pass

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f"{base_path}/video.%(ext)s",
    }

    thumbnail_path = f"{base_path}/thumbnail.jpg"
    info_path = f"{base_path}/note.txt"

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get("title", None)
        print("get video title", video_title)

        # 下载视频
        ydl.download([url])
        print(f"Video downloaded")
        time.sleep(0.1)

        # 保存视频信息
        video_filename = ydl.prepare_filename(info_dict)
        video_extension = video_filename.split(".")[-1]
        video_path = f"{base_path}/video.{video_extension}"
        video_size = os.path.getsize(video_path) / (1024 * 1024)
        video_duration = info_dict.get("duration", 0)
        video_resolution = info_dict.get("width", 0), info_dict.get("height", 0)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        video_views = info_dict.get("view_count", 0) / 10000

        with open(info_path, "w", encoding="utf-8", errors="ignore") as info_file:
            info_file.write(f"Title: {video_title}\n")
            info_file.write(f"URL: {url}\n")
            info_file.write(
                f"Resolution: {video_resolution[0]}x{video_resolution[1]}\n"
            )
            info_file.write(f"Duration: {video_duration} seconds\n")
            info_file.write(f"Size: {video_size:.2f} MB\n")
            info_file.write(f"Datetime: {current_time}\n")
            info_file.write(f"Views: {video_views}万\n")

        print(f"Video information saved")

        # 生成缩略图
        video_filename = ydl.prepare_filename(info_dict)
        video_capture = cv2.VideoCapture(video_filename)
        success, frame = video_capture.read()
        if success:
            thumbnail = cv2.resize(frame, (360, 640))  # 调整缩略图尺寸
            cv_imwrite(thumbnail_path, thumbnail)
            print(f"Thumbnail saved")
        else:
            print("Failed to extract thumbnail from video.")
        video_capture.release()
