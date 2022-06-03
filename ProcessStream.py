import cv2
import streamlink
import os
import time
import threading
import subprocess
import shutil

saved_stdout = open("my_output", "w")

wanted_stream = '1080p60'

for file in os.listdir("./data"):
    os.remove(os.path.join("./data", file))

for file in os.listdir("./mp4"):
    os.remove(os.path.join("./mp4", file))

if os.path.exists("./temp.mp4"):
    os.remove("./temp.mp4")


def get_max_seconds(cam):
    print("Received Values", cam.get(cv2.CAP_PROP_FRAME_COUNT), cam.get(cv2.CAP_PROP_FPS), file=saved_stdout, flush=True)
    total_frames = cam.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_rate = cam.get(cv2.CAP_PROP_FPS)
    return 0 if frame_rate == 0 else total_frames // frame_rate
    #
    # target_frame = (total_frames // frame_rate) * frame_rate
    # print(target_frame)
    # cam.set(cv2.CAP_PROP_POS_FRAMES, int(target_frame) -1)


def read_frame(cam, name):
    ret, frame = cam.read()
    if ret:
        print('Creating...' + name, file=saved_stdout, flush=True)
        cv2.imwrite(name, frame)
    else:
        print('SKIPPED...' + name, file=saved_stdout, flush=True)


def save_frame_at_second(cam, second):
    frame_rate = max(1, cam.get(cv2.CAP_PROP_FPS))
    target_frame = second * frame_rate
    cam.set(cv2.CAP_PROP_POS_FRAMES, int(target_frame) - 1)
    read_frame(cam, './data/frame' + str(second) + '.jpg')


gathered_frame_second = 0
def get_frame():
    global gathered_frame_second
    begin = time.time()
    cv2.setLogLevel(0)
    cam = cv2.VideoCapture(f"./temp.mp4")
    new_frame_boundary = get_max_seconds(cam)
    if new_frame_boundary > gathered_frame_second:
        while gathered_frame_second < new_frame_boundary:
            gathered_frame_second += 1
            save_frame_at_second(cam, gathered_frame_second)

    cam.release()
    cv2.destroyAllWindows()
    after = time.time()
    print("timing:", after - begin, file=saved_stdout, flush=True)


def get_stream_data():
    streams = streamlink.streams("https://twitch.tv/shoot2thr1ll284")

    my_stream = streams[wanted_stream]
    count = 0

    with my_stream.open() as f:
        while True:
            data = f.read(1000000)
            if os.path.isfile("temp.mp4"):
                shutil.copyfile("temp.mp4", os.path.join("mp4", f"stream{count}.mp4"))
            with open("temp.mp4", 'ab') as g:
                g.write(data)
            count += 1


t = threading.Thread(target=get_stream_data)
t.start()

for i in range(30):
    time.sleep(2)
    get_frame()
