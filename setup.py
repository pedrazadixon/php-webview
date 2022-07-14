import click
import requests
import argparse
import shutil
import os
import zipfile
import tempfile
from bs4 import BeautifulSoup


def download_file(file_name, url):
    with open(os.path.join(tempfile.gettempdir(), file_name), "wb") as f:
        print("Download file %s" % file_name)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        response = requests.get(url, stream=True, headers=headers)
        total_length = response.headers.get('content-length')
        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            total_length = int(total_length)
            with click.progressbar(length=total_length, label='Downloading...') as bar:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    bar.update(4096)


def getPhpVersions():
    php_versions_supported = []
    php_page = 'https://windows.php.net/downloads/releases/archives/'
    page = requests.get(php_page)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a")
    for result in results:
        if 'nts' in result.getText():
            continue
        if 'test-pack' in result.getText():
            continue
        if 'debug-pack' in result.getText():
            continue
        if 'src' in result.getText():
            continue
        if 'devel-pack' in result.getText():
            continue
        if not result.getText().startswith("php-"):
            continue
        if not result.getText().endswith(".zip"):
            continue
        if '-5.6.40' in result.getText():
            php_versions_supported.append(result.getText().split('-')[1])
        if '-7.' in result.getText():
            php_versions_supported.append(result.getText().split('-')[1])
        if '-8.' in result.getText():
            php_versions_supported.append(result.getText().split('-')[1])

    return set(php_versions_supported)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--php', help='php version', required=True)
    parser.add_argument('--arch', help='architecture x86 or x64', choices=['x86', 'x64'], required=True)
    args = parser.parse_args()

    php_vc_vs = None
    php_version = args.php
    php_arch = args.arch
    apache_arch = 'win64' if args.arch == 'x64' else 'win32'
    mariadb_arch = 'winx64' if args.arch == 'x64' else 'win32'

    if(php_version.startswith('5.5') or php_version.startswith('5.6')):
        php_vc_vs = 'VC11'
        apache_base_url = 'https://home.apache.org/~steffenal/VC11/binaries/'
        apache_filename = 'httpd-2.4.38-{}-VC11.zip'.format(apache_arch)

    if(php_version.startswith('7.0') or php_version.startswith('7.1')):
        php_vc_vs = 'VC14'
        apache_base_url = 'https://home.apache.org/~steffenal/VC14/binaries/'
        apache_filename = 'httpd-2.4.41-{}-VC14.zip'.format(apache_arch)

    if(php_version.startswith('7.2') or php_version.startswith('7.3') or php_version.startswith('7.4')):
        php_vc_vs = 'VC15'
        apache_base_url = 'https://home.apache.org/~steffenal/VC15/binaries/'
        apache_filename = 'httpd-2.4.54-{}-VC15.zip'.format(apache_arch)

    if(php_version.startswith('8.0') or php_version.startswith('8.1')):
        php_vc_vs = 'vs16'
        apache_base_url = 'https://www.apachelounge.com/download/VS16/binaries/'
        apache_filename = 'httpd-2.4.54-{}-VS16.zip'.format(apache_arch)

    print("Verifing support of PHP version...")
    if (php_vc_vs is None):
        print("Error: PHP version not supported.")
        raise SystemExit

    php_versions_supported = getPhpVersions()
    if php_version not in php_versions_supported:
        print("Error: PHP version not supported.")
        raise SystemExit

    if (len(php_version.split('.')) != 3):
        print("Error: Incorrect PHP version number.")
        raise SystemExit

    php_base_url = 'https://windows.php.net/downloads/releases/archives/'
    php_filename = 'php-{}-Win32-{}-{}.zip'.format(php_version, php_vc_vs, php_arch)

    download_file(php_filename, php_base_url + php_filename)
    download_file(apache_filename, apache_base_url + apache_filename)

    mariadb_filename = False
    if (os.path.exists(os.path.join(os.getcwd(), 'bin', 'mariadb')) == False):
        mariadb_base_url = 'https://archive.mariadb.org/mariadb-10.2.41/{}-packages/'.format(mariadb_arch)
        mariadb_filename = 'mariadb-10.2.41-{}.zip'.format(mariadb_arch)
        download_file(mariadb_filename, mariadb_base_url + mariadb_filename)

    php_bin_dir = os.path.join(os.getcwd(), 'bin', 'php')
    apache_bin_dir = os.path.join(os.getcwd(), 'bin', 'apache')
    mariadb_bin_dir = os.path.join(os.getcwd(), 'bin', 'mariadb')

    print('Removing old php bin...')
    if (os.path.exists(php_bin_dir)):
        shutil.rmtree(php_bin_dir)

    print('Removing old apache bin...')
    if (os.path.exists(apache_bin_dir)):
        shutil.rmtree(apache_bin_dir)

    print('Extract ' + php_filename)
    with zipfile.ZipFile(os.path.join(tempfile.gettempdir(), php_filename), 'r') as zip_ref:
        with click.progressbar(length=len(zip_ref.namelist()), label='Extracting...') as bar:
            for file in zip_ref.namelist():
                zip_ref.extract(file, php_bin_dir)
                bar.update(1)

    print('Extract ' + apache_filename)
    with zipfile.ZipFile(os.path.join(tempfile.gettempdir(), apache_filename), 'r') as zip_ref:
        with click.progressbar(length=len(zip_ref.namelist()), label='Extracting...') as bar:
            for file in zip_ref.namelist():
                if(file.startswith('Apache24')):
                    zip_ref.extract(file, os.path.join(os.getcwd(), 'bin'))
                bar.update(1)

    if (os.path.exists(os.path.join(os.getcwd(), 'bin', 'mariadb')) == False):
        print('Extract ' + mariadb_filename)
        with zipfile.ZipFile(os.path.join(tempfile.gettempdir(), mariadb_filename), 'r') as zip_ref:
            with click.progressbar(length=len(zip_ref.namelist()), label='Extracting...') as bar:
                for file in zip_ref.namelist():
                    zip_ref.extract(file, os.path.join(os.getcwd(), 'bin'))
                    bar.update(1)

    os.rename(os.path.join(os.getcwd(), 'bin', 'Apache24'), apache_bin_dir)

    if (os.path.exists(os.path.join(os.getcwd(), 'bin', 'mariadb')) == False):
        os.rename(os.path.join(os.getcwd(), 'bin', 'mariadb-10.2.41-{}'.format(mariadb_arch)), mariadb_bin_dir)

    print('Removing downloaded temp files...')
    os.remove(os.path.join(tempfile.gettempdir(), php_filename))
    os.remove(os.path.join(tempfile.gettempdir(), apache_filename))

    if (mariadb_filename):
        os.remove(os.path.join(tempfile.gettempdir(), mariadb_filename))

    print('New PHP version installed!')


main()
