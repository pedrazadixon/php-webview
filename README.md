# deploy

1. setup venv with python 3.8 ```py -3.8 -m venv .```
2. activate venv
3. pip install -r requirements.txt
4. python test.exe

# build exe distributable

1. pyinstaller --noconsole --onefile test.py
2. move dist\test.exe to root project
