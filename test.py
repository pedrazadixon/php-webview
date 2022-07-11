import os
import subprocess
import webview

# shorthands
nw = subprocess.CREATE_NO_WINDOW

# paths
work_dir = os.getcwd()
php_bin = os.path.join(work_dir, 'bin', 'php-bin', 'php.exe')
mysql_install_db_bin = os.path.join(
    work_dir, 'bin', 'mariadb-bin', 'bin', 'mysql_install_db.exe')
mariadbd_bin = os.path.join(
    work_dir, 'bin', 'mariadb-bin', 'bin', 'mariadbd.exe')
mysql_data_dir = os.path.join(work_dir, 'bin', 'mariadb-bin', 'data')
www_dir = os.path.join(work_dir, 'www')

# initialize mysql data
if os.path.exists(mysql_data_dir) == False:
    subprocess.Popen(mysql_install_db_bin, creationflags=nw).wait()

# start_servers
mysql_server = subprocess.Popen(
    mariadbd_bin + ' --port=8006', creationflags=nw)

php_server = subprocess.Popen(
    php_bin + ' -S ' + '127.0.0.1:8001' + ' -t ' + www_dir, creationflags=nw)

webview.create_window('App', 'http://127.0.0.1:8001')
webview.start()

# end program and cleanup
php_server.kill()
mysql_server.kill()
