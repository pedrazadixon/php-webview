# deploy

1. clone project
2. setup venv with python 3.8 `py -3.8 -m venv ./venv`
3. activate venv
4. pip install -r requirements.txt
5. python test.py

# build exe distributable

1.  pyinstaller --noconsole --onefile --uac-admin test.py
2.  move dist\test.exe to root project

# fixes

1. admin rights are required for create servers
