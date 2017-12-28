from ffmpy import FFmpeg, FFprobe
import os
import subprocess
from pymediainfo import MediaInfo

cwd = os.getcwd() #gets the working directory
os.environ['PATH'] = os.path.dirname(cwd+'\\Mediainfo.dll') + ';' + os.environ['PATH']

os.chdir('F:\\testing')
cwd = os.getcwd()

video = False

for file in os.listdir(cwd):
    fileInfo = MediaInfo.parse(file)
    video = False
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            video = True

    if video == True:
        fp = FFprobe(inputs={'test.mp4': '-v error -select_streams v:0 -show_entries stream=codec_name,height,width -of default=noprint_wrappers=1:nokey=1'})
        probe = fp.run(stdout=subprocess.PIPE)
        result = probe[0].split('\r\n')
        print result
        if result[2] >= 700 and result[0] != 'h265':
            print 'convert'
            print file.split('.')[0] + '[HEVC].mp4'
            ff = FFmpeg(
                inputs={file: '-hide_banner'},
                #inputs={file: '-hide_banner -hwaccel cuvid'},
                outputs={file.split('.')[0] + '[HEVC].mp4': '-c:a aac -c:v libx265 -preset slow'}
                #outputs={file.split('.')[0] + '[HEVC].mp4': '-c:a aac -c:v hevc_nvenc -preset slow'}
            )
            ff.run()
        else:
            #move file
            shutil.move(file, cwd + '\\converted\\' + file)


