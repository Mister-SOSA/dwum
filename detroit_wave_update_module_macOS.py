from urllib.request import urlopen
from requests import get
from io import BytesIO
from zipfile import ZipFile
import os
import shutil
import subprocess
import urllib.request as urllib
from tkinter import messagebox
import configparser
import sys
import tkinter as tk
from supabase import create_client, Client
from subprocess import Popen, PIPE

url = 'https://apkhvjohfmclnxceppmh.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNzAwNzAyMywiZXhwIjoxOTUyNTgzMDIzfQ.wmgNIIak3F7szd-ZpabIMNvQXlE9qYbdc4RXdQtCn8Y'
Client = create_client(url, key)
real_cwd = os.getcwd()[0:os.getcwd().index('Detroit Wave Updater.app')]

root = tk.Tk()
root.overrideredirect(1)
root.withdraw()

def log_auth(hwid, attempted_key, working_directory, key_found, version_found, auth_response, ip_address, notes):
    """ Send authentication results to SQL table """
    Client.table('auth').insert({"hwid": hwid,
                                 "attempted_key": attempted_key,
                                 "working_directory": working_directory,
                                 "key_found": key_found,
                                 "version_found": version_found,
                                 "auth_response": auth_response,
                                 "ip_address": ip_address,
                                 "notes": notes}).execute()

def log_updates(hwid, installed_version, available_version, accepted_update, working_directory, outcome, ip_address, notes):
    """ Send update results to SQL table """
    Client.table('updates').insert({"hwid": hwid,
                                 "installed_version": installed_version,
                                 "available_version": available_version,
                                 "accepted_update": accepted_update,
                                 "working_directory": working_directory,
                                 "ip_address": ip_address,
                                 "outcome": outcome,
                                 "notes": notes}).execute()

def get_hwid():
    """ Fetch this machine's HWID for authentication """
    stdout = Popen('system_profiler SPHardwareDataType | grep Serial', shell=True, stdout=PIPE).stdout
    output = (stdout.read()).decode('ascii')
    uuid = (output[output.index(':') + 2: len(output)]).strip()
    return uuid



def download_and_unzip(url, extract_to=real_cwd):
    """ Function to download and unzip from url """
    print('\n\nDownloading Detroit Wave Soundkit. Please Wait...')
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)

def get_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    return ip

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
    res = messagebox.askyesno('Detroit Wave Updater', 'Is this where you\'d like to install the sound kit?\n' + real_cwd)
    if res == False:
        log_updates(get_hwid(), current_version(), newest_version(), 'FALSE', os.getcwd(), get_ip(), 'CANCELLED', 'User did not want to install to the current directory.')
        messagebox.showinfo('Detroit Wave Updater', 'Move the updater to the folder you\'d like to install the kit. Then run the updater again.')
        quit()
    else:
        messagebox.showinfo('Detroit Wave Updater', 'The newest version of Detroit Wave will be installed here when you click OK.\nPlease be patient as the update is downloaded.\nThe program may appear unresponsive while downloading.')
    if (os.path.isdir(real_cwd + 'Alex Kure - Sounds of Detroit III')):
        try:
            shutil.rmtree(real_cwd + 'Alex Kure - Sounds of Detroit III/')
        except:
            log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), get_ip(),'FAILED', 'Update failed due to a permissions issue.')
            messagebox.showerror(
                'Permissions Issue', 'Update failed due to a permissions issue. Try running the updater as administrator.')
            quit()
    try:
        download_and_unzip(
            'https://www.dropbox.com/s/zazlpjlshbm1r0r/Alex%20Kure%20-%20Detroit%20Wave.zip?dl=1')
        log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'SUCCESS', get_ip(), 'Successfully updated.')
        messagebox.showinfo('Detroit Wave Updater', 'Update completed! Feel free to give me feedback on Instagram: @AlexKure')

    except:
        log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'FAILED',  get_ip(), 'Update failed due to file availability or network connection.')
        messagebox.showerror(
            'Update Failed!', 'Make sure you are connected to the internet and try again.\nIf this error persists, contact me on Instagram: @AlexKure')
        quit();
    file = open("version.ini", "r+")
    file.truncate(0)
    file.write(newest_version())
    file.close()
    quit()


def main():
    """ Initiate config parser and read key file """
    config = configparser.ConfigParser()
    config.read('key.dll')


    """ Check if user placed key file and version.ini in the same dir as updater """
    if not (os.path.exists('key.dll')):
        log_auth(get_hwid(), 'NOT FOUND', os.getcwd(), 'FALSE', 'N/A', 'N/A', get_ip(), 'key.dll was not found in the current directory.')
        messagebox.showerror(
            'Missing Key', 'Your "key" file was not found.')
        quit()

    if not (os.path.exists('version.ini')):
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'FALSE', 'N/A', get_ip(), 'version.ini was not found in the current directory.')
        messagebox.showerror(
            'Missing version.ini', 'Your version.ini file was not found.')
        quit()

    """ Check HWID with provided key file. If matched, proceed. If not, quit with error """
    if (config['REGISTRATION']['hwid'] == 'unregistered'):
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'SUCCESS', get_ip(), 'First time registration.')
        config['REGISTRATION']['hwid'] = get_hwid()
        try:
            with open('key.dll', 'w') as configfile:
                config.write(configfile)
        except:
            log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'FAILED', get_ip(), 'First time registration failed.')
            messagebox.showinfo(
                'Registration Failed!', 'First time setup failed for some unknown reason.')

    if (config['REGISTRATION']['HWID'] != get_hwid()):
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'FAILED', get_ip(), 'Piracy Protection Triggered.')
        messagebox.showerror('Validation Failed!', 'Your device is not registered with this soundkit. Make sure you have purchased the soundkit and are using your own copy of the updater.\n\nFor assistance, DM me on Instagram: @AlexKure')
        quit()
    else:
        log_auth(get_hwid(), config['REGISTRATION']['hwid'], os.getcwd(), 'TRUE', 'TRUE', 'SUCCESS', get_ip(), 'Successful Login.')

    """ Check if a new version of the kit is available. If so, download it and unzip it to the current dir """
    if (current_version() != newest_version()):
        res = messagebox.askyesno('Detroit Wave Updater', 'An update is available! Would you like to download it?')
        if res == True:
            update()
        else:
            log_updates(get_hwid(), current_version(), newest_version(), 'FALSE', os.getcwd(), 'REJECTED', get_ip(), 'User rejected update')
            messagebox.showinfo('Update Cancelled', 'If you change your mind, run this updater again to download the latest version of Detroit Wave.')
    else:
        res = messagebox.askyesno('Detroit Wave Updater', 'You already have the newest version of the soundkit. Would you like to reinstall it anyway?')
        if res == True:
            log_updates(get_hwid(), current_version(), newest_version(), 'TRUE', os.getcwd(), 'N/A', get_ip(), 'User reinstalled.')
            update()
        else:
            quit()
