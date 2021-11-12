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





""" Fetch this machine's HWID for authentication """
def get_HWID():
    cmd = 'wmic csproduct get uuid'
    uuid = str(subprocess.check_output(cmd))
    pos1 = uuid.find("\\n") + 2
    uuid = uuid[pos1:-15]
    return uuid



""" Function to download and unzip from url """
def download_and_unzip(url, extract_to='.'):
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)



""" Fetch newest available version number from Dropbox config file """
def newest_version():
    fetch_config = urllib.urlopen(
        'https://www.dropbox.com/s/uo25m27q4lkoo6l/newest_version.txt?dl=1')
    return ((fetch_config.read()).decode())



""" Fetch currently installed version number from local config file """
def current_version():
    with open('version.ini') as f:
        return f.readlines()[0]



""" Fetch newest version of kit and unzip it in the current directory """
def update():
    if (os.path.isdir('Alex Kure - Sounds of Detroit III')):
        try:
            shutil.rmtree('Alex Kure - Sounds of Detroit III/')
        except:
            messagebox.showerror(
            'Permissions Issue', 'Update failed due to a permissions issue. Try running the updater as administrator.')
            quit()
    try:
        download_and_unzip(
        'https://www.dropbox.com/s/zazlpjlshbm1r0r/Alex%20Kure%20-%20Detroit%20Wave.zip?dl=1')
    except:
        messagebox.showinfo(
            'Update Failed!', 'Make sure you are connected to the internet and try again.\nIf this error persists, contact me on Instagram: @AlexKure')
    file = open("version.ini", "r+")
    file.truncate(0)
    file.write(newest_version())
    file.close()

""" Check if user placed key file and version.ini in the same dir as updater """
if not (os.path.exists('key.exe')):
    messagebox.showerror(
    'Missing Key', 'Your "key" file was not found. Make sure it is in the same folder as the updater.')
    quit()

if not (os.path.exists('version.ini')):
    messagebox.showerror(
    'Missing version.ini', 'Your version.ini file was not found in this folder. Make sure it is in the same folder as the updater')
    quit()



""" Initiate config parser and read key file """
config = configparser.ConfigParser()
config.read('key.exe')

""" Check HWID with provided key file. If matched, proceed. If not, quit with error """
if (config['REGISTRATION']['hwid'] == 'unregistered'):
    config['REGISTRATION']['hwid'] = get_HWID()
    try:
        with open('key.exe', 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo(
            'Registered!', 'First time setup complete. Device is registered.')
    except:
        messagebox.showinfo(
            'Registration Failed!', 'First time setup failed for some unknown reason.')

elif (config['REGISTRATION']['HWID'] == get_HWID()):
    messagebox.showinfo('Validation Success!',
                        'Device is registered with this program.')

if (config['REGISTRATION']['HWID'] != get_HWID()):
    messagebox.showerror('Validation Failed!', 'Your device is not registered with this soundkit. Make sure you have purchased the soundkit and placed the provided key file in the same folder as this updater.\n\nFor assistance, DM me on Instagram: @AlexKure')
    quit()


""" Check if a new version of the kit is available. If so, download it and unzip it to the current dir """
if (current_version() != newest_version()):
    messagebox.showinfo(
        'New Version Available!', 'An update is available! Downloading it now.')
    update()
else:
    messagebox.showinfo(
        'No Updates Available.', 'Newest version already installed. Enjoy!')

os.remove("./detroit_wave_update_module.exe")
