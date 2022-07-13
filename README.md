# deploy

1. clone project
2. setup venv with python 3.8 `py -3.8 -m venv ./venv`
3. activate venv
4. pip install -r requirements.txt
5. `setup.exe --php 7.4.0 arch=x86` (you cant enter a valid php version for setup)
6. python php-webview.py

# build exe distributable

1.  pyinstaller --noconsole --onefile --uac-admin php-webview.py
2.  move dist\php-webview.exe to root project

# fixes

1. admin rights are required for create servers
