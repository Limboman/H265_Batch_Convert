from ffmpy import FFmpeg, FFprobe
import os
import subprocess
import shutil
from pymediainfo import MediaInfo

cwd = os.getcwd()  # gets the working directory
os.environ['PATH'] = os.path.dirname(cwd+'\\Mediainfo.dll') + ';' + os.environ['PATH']

os.chdir('E:\\testing')
cwd = os.getcwd()

video = False

for files in os.listdir(cwd):
    fileInfo = MediaInfo.parse(files)
    video = False
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            video = True

    if video:

        fp = FFprobe(inputs={'test.mp4': '-v error -select_streams v:0 -show_entries stream=codec_name,height,width -of default=noprint_wrappers=1:nokey=1'})
        probe = fp.run(stdout=subprocess.PIPE)
        result = probe[0].split('\r\n')
        print result
        if result[2] >= 700 and result[0] != 'h265':
            if not os.path.exists(cwd + '\\converted\\'):
                os.mkdir(cwd + '\\converted\\')
            print 'convert'
            print files.split('.')[0] + '[HEVC].mp4'
            ff = FFmpeg(
                inputs={files: '-hide_banner'},
                # inputs={files: '-hide_banner -hwaccel cuvid'},
                outputs={files.split('.')[0] + '[HEVC].mp4': '-c:a aac -c:v libx265 -preset slow'}
                # outputs={files.split('.')[0] + '[HEVC].mp4': '-c:a aac -c:v hevc_nvenc -preset slow'}
            )
            ff.run()
            shutil.move(files, cwd + '\\converted\\' + files)
        else:
            if not os.path.exists(cwd + '\\to_small_to_convert\\'):
                os.mkdir(cwd + '\\to_small_to_convert\\')
            # move file
            shutil.move(files, cwd + '\\to_small_to_convert\\' + files)


