from ffmpy import FFmpeg, FFprobe
import os
import subprocess
import shutil
from pymediainfo import MediaInfo


def isclose(a, b, rel_tol=0.005, abs_tol=0.0):
	return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


cwd = os.getcwd()  # gets the working directory
os.environ['PATH'] = os.path.dirname(cwd+'\\Mediainfo.dll') + ';' + os.environ['PATH']

os.chdir('C:\\Users\\Cam\Desktop\\testing\\test')
cwd = os.getcwd()

video = False

for root, directories, filenames in os.walk(cwd):
	for filename in filenames:
		files = os.path.join(root, filename)
		fileInfo = MediaInfo.parse(files)
		video = False
		for track in fileInfo.tracks:
			if track.track_type == "Video":
				video = True
		if video:
			fp = FFprobe(inputs={files: '-v error -select_streams v:0 -show_entries stream=codec_name,height,width -of default=noprint_wrappers=1:nokey=1'})
			probe = fp.run(stdout=subprocess.PIPE)
			result = probe[0].split('\r\n')
			print result
			if int(result[2]) >= 700 and result[0] != 'hevc':
				if not os.path.exists(root + '\\Problem\\'):
					os.mkdir(root + '\\Problem\\')
				print 'convert'
				print files.split('.')[0] + '[HEVC].mp4'
				ff = FFmpeg(
					# inputs={files: '-hide_banner'},
					inputs={files: '-hide_banner -hwaccel cuvid'},
					# outputs={os.path.splitext(files)[0] + '[HEVC].mp4': '-max_muxing_queue_size 8000 -c:a aac -c:v libx265 -preset slow'}
					outputs={os.path.splitext(files)[0] + '[HEVC].mp4': '-max_muxing_queue_size 8000 -c:a aac -c:v hevc_nvenc -preset slow'}
				)
				ff.run()
				# Check to see if the duration of the new file is within 0.05% of the old one
				fp = FFprobe(inputs={files: '-v error -select_streams v:0 -show_entries stream=duration,codec_name,height,width -of default=noprint_wrappers=1:nokey=1'})
				probe = fp.run(stdout=subprocess.PIPE)
				result = probe[0].split('\r\n')
				fp2 = FFprobe(inputs={os.path.splitext(files)[0] + '[HEVC].mp4': '-v error -select_streams v:0 -show_entries stream=duration,codec_name,height,width -of default=noprint_wrappers=1:nokey=1'})
				probe2 = fp2.run(stdout=subprocess.PIPE)
				result2 = probe2[0].split('\r\n')
				if isclose(float(result2[3]), float(result[3])):
					print "delete"
					try:
						os.remove(files)
					except OSError:
						pass
				else:
					print "move"
					shutil.move(files, root + '\\Problem\\' + os.path.basename(files))
			elif result[0] == 'hevc':
				print 'already HEVC'
			else:
				print 'too small'
				# if not os.path.exists(root + '\\to_small_to_convert\\'):
				#    os.mkdir(root + '\\to_small_to_convert\\')
				# move file
				# shutil.move(files, root + '\\to_small_to_convert\\' + os.path.basename(files))
