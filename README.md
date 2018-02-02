# h265 Batch Convert Script

This python script searches through all the files and folders within its working directory and if the file is 720p or greater and not already HEVC it converts it to HEVC using nvenc.
it will then check to see that the conversion created a file with a duration within a few secconds of the original and if so it deletes the original.
