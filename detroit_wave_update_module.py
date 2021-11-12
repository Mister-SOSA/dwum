from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os
import shutil
import subprocess
import urllib.request as urllib
from tkinter import messagebox
import configparser
import sys


def get_hwid():
    """ Fetch this machine's HWID for authentication """
    cmd = 'wmic csproduct get uuid'
    uuid = str(subprocess.check_output(cmd))
    pos1 = uuid.find("\\n") + 2
    uuid = uuid[pos1:-15]
    return uuid



def download_and_unzip(url, extract_to='.'):
    """ Function to download and unzip from url """
    print('\n\nDownloading Detroit Wave Soundkit. Please Wait...')
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)



def newest_version():
    """ Fetch newest available version number from Github text file """
    fetch_config = urllib.urlopen(
        'https://raw.githubusercontent.com/Mister-SOSA/dwum/main/newest_version.txt')
    return ((fetch_config.read()).decode())


def current_version():
    """ Fetch currently installed version number from local config file """
    with open('version.ini') as f:
        return f.readlines()[0]


def update():
    """ Fetch newest version of kit and unzip it in the current directory """
    res = messagebox.askyesno('Detroit Wave Updater', 'Is this where you\'d like to install the sound kit?\n' + os.getcwd())
    if res == False:
        messagebox.showinfo('Detroit Wave Updater', 'Move the updater, version.ini, and key file to the folder you\'d like to install the kit. Then run the updater again.')
        sys.exit()
    else:
        messagebox.showinfo('Detroit Wave Updater', 'The newest version of Detroit Wave will be now be installed here.')
    if (os.path.isdir('Alex Kure - Sounds of Detroit III')):
        try:
            shutil.rmtree('Alex Kure - Sounds of Detroit III/')
        except:
            messagebox.showerror(
                'Permissions Issue', 'Update failed due to a permissions issue. Try running the updater as administrator.')
            sys.exit()
    try:
        download_and_unzip(
            'https://www.dropbox.com/s/zazlpjlshbm1r0r/Alex%20Kure%20-%20Detroit%20Wave.zip?dl=1')
        messagebox.showinfo('Detroit Wave Updater', 'Update completed!\nFeel free to give me feedback on Instagram: @AlexKure')

    except:
        messagebox.showerror(
            'Update Failed!', 'Make sure you are connected to the internet and try again.\nIf this error persists, contact me on Instagram: @AlexKure')
        sys.exit();
    file = open("version.ini", "r+")
    file.truncate(0)
    file.write(newest_version())
    file.close()
    sys.exit()


def main():
    """ Check if user placed key file and version.ini in the same dir as updater """
    if not (os.path.exists('key.exe')):
        messagebox.showerror(
            'Missing Key', 'Your "key" file was not found. Make sure it is in the same folder as the updater.')
        sys.exit()

    if not (os.path.exists('version.ini')):
        messagebox.showerror(
            'Missing version.ini', 'Your version.ini file was not found in this folder. Make sure it is in the same folder as the updater')
        sys.exit()

    """ Initiate config parser and read key file """
    config = configparser.ConfigParser()
    config.read('key.exe')

    """ Check HWID with provided key file. If matched, proceed. If not, quit with error """
    if (config['REGISTRATION']['hwid'] == 'unregistered'):
        config['REGISTRATION']['hwid'] = get_hwid()
        try:
            with open('key.exe', 'w') as configfile:
                config.write(configfile)
        except:
            messagebox.showinfo(
                'Registration Failed!', 'First time setup failed for some unknown reason.\nTry running as administrator.')

    elif (config['REGISTRATION']['HWID'] == get_hwid()):
        messagebox.showinfo('Validation Success!',
                            'Device is ada registered with this program.')

    if (config['REGISTRATION']['HWID'] != get_hwid()):
        messagebox.showerror('Validation Failed!', 'Your device is not registered with this soundkit. Make sure you have purchased the soundkit and placed the provided key file in the same folder as this updater.\n\nFor assistance, DM me on Instagram: @AlexKure')
        sys.exit()

    """ Check if a new version of the kit is available. If so, download it and unzip it to the current dir """
    if (current_version() != newest_version()):
        res = messagebox.askyesno('Detroit Wave Updater', 'An update is available! Would you like to download it?')
        if res == True:
            update()
        else:
            messagebox.showinfo('Update Cancelled', 'If you change your mind, run this updater again to download the latest version of Detroit Wave.')
    else:
        res = messagebox.askyesno('Detroit Wave Updater', 'You already have the newest version of the soundkit. Would you like to reinstall it anyway?')
        if res == True:
            update()
        else:
            sys.exit()
