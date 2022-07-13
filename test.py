import os
import subprocess
import webview
import re
import shutil

# shorthands
nw = subprocess.CREATE_NO_WINDOW


# paths
work_dir = os.getcwd()
apache_dir = os.path.join(work_dir, 'bin', 'apache')
php_dir = os.path.join(work_dir, 'bin', 'php')
php_ext_dir = os.path.join(php_dir, 'ext')
mariadb_dir = os.path.join(work_dir, 'bin', 'mariadb')
www_dir = os.path.join(work_dir, 'www')


# create folder www if required
if os.path.exists(www_dir) == False:
    os.mkdir(www_dir)


# make apache config
httpd_conf = open(os.path.join(apache_dir, 'conf', 'httpd.conf'), "rt")
data = httpd_conf.read()
httpd_conf.close()

httpd_SRVROOT = 'Define SRVROOT "{}"'.format(apache_dir.replace('\\', '\\\\'))
httpd_Listen = 'Listen 127.0.0.1:8001'
httpd_DocumentRoot = 'DocumentRoot "{}"'.format(www_dir.replace('\\', '\\\\'))
httpd_Directory = '<Directory "{}">'.format(www_dir.replace('\\', '\\\\'))
httpd_PHPIniDir = 'PHPIniDir "{}"'.format(php_dir.replace('\\', '\\\\'))

data = re.sub(r'(^Define SRVROOT .*)', httpd_SRVROOT, data, flags=re.M)
data = re.sub(r'(^Listen .*)', httpd_Listen, data, flags=re.M)
data = re.sub(r'(^DocumentRoot .*)', httpd_DocumentRoot, data, flags=re.M)
data = re.sub(r'(^<Directory .*(htdocs|www).*>$)', httpd_Directory, data, flags=re.M)
data = re.sub(r'(AllowOverride None)', 'AllowOverride All', data, flags=re.M)
data = re.sub(r'(DirectoryIndex index.html)', 'DirectoryIndex index.php index.html', data, flags=re.M)

if "PHPIniDir " in data:
    data = re.sub(r'(^PHPIniDir .*)', httpd_PHPIniDir, data, flags=re.M)
else:
    data = data + '\n' + httpd_PHPIniDir.replace('\\\\', '\\')

if os.path.exists(os.path.join(php_dir, 'php5apache2_4.dll')):
    directive = 'php5_module'
    dll_path = os.path.join(php_dir, 'php5apache2_4.dll')
    httpd_php_mod_string = 'LoadModule {} "{}"'.format(directive, dll_path.replace('\\', '\\\\'))

if os.path.exists(os.path.join(php_dir, 'php7apache2_4.dll')):
    directive = 'php7_module'
    dll_path = os.path.join(php_dir, 'php7apache2_4.dll')
    httpd_php_mod_string = 'LoadModule {} "{}"'.format(directive, dll_path.replace('\\', '\\\\'))

if os.path.exists(os.path.join(php_dir, 'php8apache2_4.dll')):
    directive = 'php_module'
    dll_path = os.path.join(php_dir, 'php8apache2_4.dll')
    httpd_php_mod_string = 'LoadModule {} "{}"'.format(directive, dll_path.replace('\\', '\\\\'))

if "LoadModule php" in data:
    data = re.sub(r'(^LoadModule php.*)', httpd_php_mod_string, data, flags=re.M)
else:
    data = data + '\n' + httpd_php_mod_string.replace('\\\\', '\\')

if not "AddType application/x-httpd-php .php" in data:
    data = data + '\nAddType application/x-httpd-php .php'

httpd_conf = open(os.path.join(apache_dir, 'conf', 'httpd.conf'), "wt")
httpd_conf.write(data)
httpd_conf.close()


# make php config
if os.path.exists(os.path.join(php_dir, 'php.ini')) == False:
    shutil.copyfile(os.path.join(php_dir, 'php.ini-development'), os.path.join(php_dir, 'php.ini'))

php_ini = open(os.path.join(php_dir, 'php.ini'), "rt")
data = php_ini.read()
php_ini.close()

data = re.sub(r'(^;? ?extension_dir = .*ext".*)',
              'extension_dir = "{}"'.format(php_ext_dir.replace('\\', '\\\\')), data, flags=re.M)

print('extension_dir = "{}"'.format(php_ext_dir.replace('\\', '\\\\')))

# php >= 7
data = re.sub(r'(^;extension=intl.*)', 'extension=intl', data, flags=re.M)
data = re.sub(r'(^;extension=mbstring.*)', 'extension=mbstring', data, flags=re.M)
data = re.sub(r'(^;extension=mysqli.*)', 'extension=mysqli', data, flags=re.M)
data = re.sub(r'(^;extension=openssl.*)', 'extension=openssl', data, flags=re.M)
data = re.sub(r'(^;extension=pdo_mysql.*)', 'extension=pdo_mysql', data, flags=re.M)

# php < 7
data = re.sub(r'(^;extension=php_intl.*)', 'extension=php_intl.dll', data, flags=re.M)
data = re.sub(r'(^;extension=php_mbstring.*)', 'extension=php_mbstring.dll', data, flags=re.M)
data = re.sub(r'(^;extension=php_mysqli.*)', 'extension=php_mysqli.dll', data, flags=re.M)
data = re.sub(r'(^;extension=php_openssl.*)', 'extension=php_openssl.dll', data, flags=re.M)
data = re.sub(r'(^;extension=php_pdo_mysql.*)', 'extension=php_pdo_mysql.dll', data, flags=re.M)

php_ini = open(os.path.join(php_dir, 'php.ini'), "wt")
php_ini.write(data)
php_ini.close()


# initialize mysql data if required
if os.path.exists(os.path.join(mariadb_dir, 'data')) == False:
    subprocess.Popen(os.path.join(mariadb_dir, 'bin', 'mysql_install_db.exe'), creationflags=nw).wait()


# start_servers
mysql_server = subprocess.Popen([os.path.join(mariadb_dir, 'bin', 'mariadbd.exe'), '--port=8006'], creationflags=nw)

httpd_server = subprocess.Popen([os.path.join(apache_dir, 'bin', 'httpd.exe')], creationflags=nw)


# start webview
webview.create_window('App', 'http://127.0.0.1:8001')
webview.start()


# end program and cleanup
httpd_server.kill()
mysql_server.kill()
