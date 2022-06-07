# use ffmpeg to async read video file (async)
## As files are outputted rename them and keep track of count
### Double check if renaming causes issues
## After ffmpeg/file renaming start timer or new ffmpeg starting based off of previous image count


Should check quality of ffmpeg image output with ocr (is it better/worse than cv2)

Keep in mind to track timing of processing vs readying of frames. Can change rate if issue