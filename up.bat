git add . 
git commit -m "%*" 
git push
ssh -i C:\Users\robin\.ssh\id_videoflix_server robingerth21@34.65.68.132 "cd projects && cd Videoflix-Backend && sudo git pull && sudo ./env/bin/pip install -r requirements.txt"