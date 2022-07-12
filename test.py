import os
import subprocess
import webview

# shorthands
nw = subprocess.CREATE_NO_WINDOW


# paths
work_dir = os.getcwd()
apache_dir = os.path.join(work_dir, 'bin', 'Apache24')
php_dir = os.path.join(work_dir, 'bin', 'php')
mariadb_dir = os.path.join(work_dir, 'bin', 'mariadb')
www_dir = os.path.join(work_dir, 'www')


# make httpd config
httpd_ori = open(os.path.join(apache_dir, 'conf', 'httpd.ori'), "rt")
data = httpd_ori.read()
data = data.replace('[PHPIniDir]', php_dir)
data = data.replace('[php7_module]', os.path.join(
    php_dir, 'php7apache2_4.dll'))
data = data.replace('[SRVROOT]', apache_dir)
data = data.replace('[DocumentRoot]', www_dir)
httpd_ori.close()

httpd_conf = open(os.path.join(apache_dir, 'conf', 'httpd.conf'), "wt")
httpd_conf.write(data)
httpd_conf.close()


# initialize mysql data if required
if os.path.exists(os.path.join(mariadb_dir, 'data')) == False:
    subprocess.Popen(
        os.path.join(mariadb_dir, 'bin', 'mysql_install_db.exe'), creationflags=nw).wait()


# start_servers
mysql_server = subprocess.Popen(
    [os.path.join(mariadb_dir, 'bin', 'mariadbd.exe'), '--port=8006'], creationflags=nw)

httpd_server = subprocess.Popen(
    [os.path.join(apache_dir, 'bin', 'httpd.exe')], creationflags=nw)


# start webview
webview.create_window('App', 'http://127.0.0.1:8001')
webview.start()


# end program and cleanup
httpd_server.kill()
mysql_server.kill()
