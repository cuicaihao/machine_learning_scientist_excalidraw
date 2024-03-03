# Create the file size.sh to list all the *.png files in the current directory and display

du -sh *.png | sort -rh > file_size.log