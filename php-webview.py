import os
import subprocess
import webview
import re
import shutil
import pyautogui


# shorthands
nw = subprocess.CREATE_NO_WINDOW

# paths
work_dir = os.getcwd()
apache_dir = os.path.join(work_dir, 'bin', 'apache')
php_dir = os.path.join(work_dir, 'bin', 'php')
mariadb_dir = os.path.join(work_dir, 'bin', 'mariadb')
php_ext_dir = os.path.join(php_dir, 'ext')
www_dir = os.path.join(work_dir, 'www')


def checks():
    if os.path.exists(www_dir) == False:
        os.mkdir(www_dir)

    if os.path.exists(apache_dir) == False:
        pyautogui.alert(apache_dir + ' not found.\nPlease use setup.exe to download it.', "Error")
        raise SystemExit

    if os.path.exists(php_dir) == False:
        pyautogui.alert(php_dir + ' not found.\nPlease use setup.exe to download it.', "Error")
        raise SystemExit

    if os.path.exists(mariadb_dir) == False:
        pyautogui.alert(mariadb_dir + ' not found.\nPlease use setup.exe to download it.', "Error")
        raise SystemExit


def makeHttpdConfig():
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


def makePHPConfig():
    if os.path.exists(os.path.join(php_dir, 'php.ini')) == False:
        shutil.copyfile(os.path.join(php_dir, 'php.ini-development'), os.path.join(php_dir, 'php.ini'))

    php_ini = open(os.path.join(php_dir, 'php.ini'), "rt")
    data = php_ini.read()
    php_ini.close()

    data = re.sub(r'(^;? ?extension_dir = .*ext".*)',
                  'extension_dir = "{}"'.format(php_ext_dir.replace('\\', '\\\\')), data, flags=re.M)

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


def startMysqlServer():
    # initialize mysql data if required
    if os.path.exists(os.path.join(mariadb_dir, 'data')) == False:
        data_cmd = '"' + os.path.join(mariadb_dir, 'bin', 'mysql_install_db.exe') + \
            '" -d "' + os.path.join(mariadb_dir, 'data') + '"'
        subprocess.Popen(data_cmd, creationflags=nw).wait()

    return subprocess.Popen([os.path.join(mariadb_dir, 'bin', 'mysqld.exe'), '--port=8006'], creationflags=nw)


def startHttpdServer():
    return subprocess.Popen([os.path.join(apache_dir, 'bin', 'httpd.exe')], creationflags=nw)


def startWebview():
    webview.create_window('App', 'http://127.0.0.1:8001')
    webview.start()


def killServers(processes):
    for process in processes:
        process.kill()


def main():
    checks()
    makeHttpdConfig()
    makePHPConfig()
    mysql_process = startMysqlServer()
    httpd_process = startHttpdServer()
    startWebview()
    killServers([mysql_process, httpd_process])


main()
