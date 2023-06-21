import os
import subprocess
import urllib.request
from urllib.error import URLError
from shutil import rmtree
from gpubs.log import msg1, msg2
def check_disk_space(predicted_size, download_dir, verbose):
    required_space = predicted_size
    available_space = os.statvfs(download_dir).f_frsize * os.statvfs(download_dir).f_bavail
    required_space_human = subprocess.check_output(['numfmt', '--to=iec-i', '--suffix=B', str(required_space)]).decode().strip()
    available_space_human = subprocess.check_output(['numfmt', '--to=iec-i', '--suffix=B', str(available_space)]).decode().strip()

    msg1(verbose, f"Predicted download size = {required_space_human}, Available space = {available_space_human}")

    if required_space > available_space:
        print(f"Insufficient disk space! Required: {required_space_human}, Available: {available_space_human}")
        exit(1)

def download_file(url, file_path, verbose):
    try:
        urllib.request.urlretrieve(url, file_path)
    except URLError as e:
        msg1(verbose, f"Error downloading file: {url}")
        msg1(verbose, f"Reason: {str(e.reason)}")
        #exit(1)

def verify_md5(file_path, md5_file_path, verbose):
    try:
        output = subprocess.check_output(['md5sum', '-c', os.path.basename(md5_file_path)], cwd=os.path.dirname(md5_file_path), stderr=subprocess.DEVNULL).decode()
        #output = subprocess.check_output(['md5sum', '-c', md5_file_path], stderr=subprocess.DEVNULL).decode()
        if "OK" in output:
            msg2(verbose, f"{md5_file_path}: OK - MD5 checksum verification succeeded.")
        else:
            msg1(verbose, f"ERROR: {md5_file_path}: FAILED - MD5 checksum verification failed.")
    except subprocess.CalledProcessError:
        msg1(verbose, f"ERROR: {md5_file_path}: FAILED - MD5 checksum verification failed.")
