# start atom script

export SCREENSHOOTER_DIR='/home/cws/web-screenshooter-API'
export SCREENSHOOTER_IMG='captures/atom-screen.png'
export SCREENSHOOTER_URL='https://dir.bg'
export SCREENSHOOTER_BIN='cli/webscreen.sh'

# cd $SCREENSHOOTER_DIR
mkdir captures | chmod 777 -R captures
python3 -m main.bin.entry
bash $SCREENSHOOTER_BIN capture $SCREENSHOOTER_URL -o $SCREENSHOOTER_IMG