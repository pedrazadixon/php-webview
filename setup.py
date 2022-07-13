import click
import requests
import argparse
import shutil
import os
import zipfile
import tempfile


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--php', help='php version', required=True)
    parser.add_argument('--arch', help='architecture x86 or x64', choices=['x86', 'x64'], required=True)
    args = parser.parse_args()

    php_vc_vs = None
    php_version = args.php
    php_arch = args.arch
    apache_arch = 'win64' if args.arch == 'x64' else 'win32'

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

    if (php_vc_vs is None):
        print("Error: PHP version not supported.")
        raise SystemExit

    if (len(php_version.split('.')) != 3):
        print("Error: Incorrect PHP version number.")
        raise SystemExit

    php_base_url = 'https://windows.php.net/downloads/releases/archives/'
    php_filename = 'php-{}-Win32-{}-{}.zip'.format(php_version, php_vc_vs, php_arch)

    download_file(php_filename, php_base_url + php_filename)
    download_file(apache_filename, apache_base_url + apache_filename)

    php_bin_dir = os.path.join(os.getcwd(), 'bin', 'php')
    apache_bin_dir = os.path.join(os.getcwd(), 'bin', 'apache')

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

    os.rename(os.path.join(os.getcwd(), 'bin', 'Apache24'), apache_bin_dir)

    print('Removing downloaded temp files...')
    os.remove(os.path.join(tempfile.gettempdir(), php_filename))
    os.remove(os.path.join(tempfile.gettempdir(), apache_filename))

    print('New PHP version installed!')


main()