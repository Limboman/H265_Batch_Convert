from ffmpy import FFmpeg, FFprobe
import os
import subprocess
import shutil
from pymediainfo import MediaInfo


def isclose(a, b, rel_tol=0.01, abs_tol=0.0):
	return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


cwd = os.getcwd()  # gets the working directory
os.environ['PATH'] = os.path.dirname(cwd+'\\Mediainfo.dll') + ';' + os.environ['PATH']

# os.chdir('C:\\Users\\Cam\Desktop\\testing\\test')
# cwd = os.getcwd()

orig_dir = cwd

usr_input = raw_input("Root path for conversion: ")
if usr_input != "":
	cwd = usr_input

file_name = usr_input.replace('\\', '')
file_name = file_name.replace(':', '')

try:
	progress_file = open(orig_dir + '\\'+file_name+'.txt', 'r+')
except IOError:
	progress_file = open(orig_dir + '\\'+file_name+'.txt', 'w')
progress_file.close()

progress_file = open(orig_dir + '\\'+file_name+'.txt', 'r+')
file_data = progress_file.readlines()
progress_file.close()

upto = ''

for data_line in file_data:
	upto = data_line

video = False
skip = False
if upto == '':
	found = True
else:
	found = False


for root, directories, filenames in os.walk(cwd):
	print root
	skip = False
	if root != upto and found is False:
		skip = True
	if skip is True:
		# directories[:] = []
		filenames[:] = []
	roottest = str(root)
	if roottest.split('\\')[-1] in ('BigProblem', 'Problem', 'Error'):
		filenames[:] = []
	if found is True:
		progress_file = open(orig_dir + '\\' + file_name + '.txt', 'w')
		progress_file.write(root)
		progress_file.close()
	for filename in filenames:
		found = True
		if os.path.splitext(filename)[1] not in ('.jpg', '.png', '.jpeg', '.bmp', '.swf', '.pdf', '.m3u', '.JPG', '.PNG', '.JPEG', '.BMP', '.SWF', '.PDF', '.M3U'):
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
				print str(result) + ' ' + files
				if result.count > 2:
					if int(result[2]) >= 700 and result[0] != 'hevc':
						print 'convert'
						print files.split('.')[0] + '[HEVC].mp4'
						ff = FFmpeg(
							# inputs={files: '-hide_banner -y'},
							inputs={files: '-hide_banner -y -hwaccel cuvid'},
							# outputs={os.path.splitext(files)[0] + '[HEVC].mp4': '-max_muxing_queue_size 8000 -c:a aac -c:v libx265 -preset slow'}
							outputs={os.path.splitext(files)[0] + '[HEVC].mp4': '-max_muxing_queue_size 8000 -c:a aac -c:v hevc_nvenc -preset slow'}
						)
						try:
							ff.run()
							# Check to see if the duration of the new file is within 0.05% of the old one
							filecheck_orig = MediaInfo.parse(files)
							filecheck_hevc = MediaInfo.parse(os.path.splitext(files)[0] + '[HEVC].mp4')
							orig_check_result = 0
							hevc_check_result = -999
							for track_orig in filecheck_orig.tracks:
								if track_orig.track_type == "Video":
									if track_orig.duration is not None:
										orig_check_result = track_orig.duration
									else:
										orig_check_result = 0
							for track_hevc in filecheck_hevc.tracks:
								if track_hevc.track_type == "Video":
									if track_hevc.duration is not None:
										hevc_check_result = track_hevc.duration
									else:
										hevc_check_result = -999
							if isclose(float(hevc_check_result), float(orig_check_result)):
								print "delete"
								try:
									os.remove(files)
								except OSError:
									pass
							else:
								print "Problem"
								if not os.path.exists(root + '\\Problem\\'):
									os.mkdir(root + '\\Problem\\')
								shutil.move(files, root + '\\Problem\\' + os.path.basename(files))
						except Exception, e:
							# error durring conversion
							print repr(e)
							print "Error Durring Conversion"
							if not os.path.exists(root + '\\Error\\'):
								os.mkdir(root + '\\Error\\')
							if os.path.exists(os.path.splitext(files)[0] + '[HEVC].mp4'):
								os.remove(os.path.splitext(files)[0] + '[HEVC].mp4')
							shutil.move(files, root + '\\Error\\' + os.path.basename(files))
							error_file = open(root + '\\Error\\' + os.path.basename(files) + '.txt', 'w')
							error_file.write(repr(e))
							error_file.close()
					elif result[0] == 'hevc':
						print 'already HEVC'
					else:
						print 'too small'
				else:
					print "BigProblem"
					if not os.path.exists(root + '\\BigProblem\\'):
						os.mkdir(root + '\\BigProblem\\')
					shutil.move(files, root + '\\BigProblem\\' + os.path.basename(files))
