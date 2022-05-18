import os
import sys
import paramiko
import argparse
import platform
from io import StringIO
from scp import SCPClient, SCPException
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException

"""
Python script which allows ssh connexion between Azure VM to upload or retrieve files

Usage:
python3 copyData.py get|upload src dest

"""

if platform.system() == "Windows":
	DEFAULT_LOCAL = os.environ["USERPROFILE"] + '\\'
else:
	DEFAULT_LOCAL = os.environ["HOME"] + '/'

IP = "x2021helios34195214001.northeurope.cloudapp.azure.com"
USERNAME = "SECONDSECRETUSER"
PASSWORD = "SECONDSECRETPASSWORD"
PORT = 64639
DEFAULT_VM = "/home/heliosia/"
DEFAULT_LOCAL += "Documents"

def set_environment():
	os.environ["AZURE_IP"] = IP
	os.environ["AZURE_USERNAME"] = USERNAME
	os.environ["AZURE_PASSWD"] = PASSWORD
	os.environ["AZURE_PORT"] = str(PORT)

def connect():
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(IP, username=USERNAME, password=PASSWORD, port=PORT)
	except AuthenticationException:
		raise AuthenticationException("Authentication failed")
	return client

def progress(filename, size, sent):
    	sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size) * 100))

def get(client, src, dest):
	if src == None:
		print("No source provided.", end=' ')
		src = DEFAULT_VM
	if dest == None:
		print("No destination provided.", end=' ')
		dest = DEFAULT_LOCAL
	scp = SCPClient(client.get_transport(), progress=progress)
	try:
		scp.get(src, recursive=True, local_path=dest)
	except SCPException:
		raise SCPException("File not found")
	finally:
		scp.close()
	print("Copying %s to %s" % (src, dest))

def upload(client, src, dest):
	if src == None:
		raise Exception("Please specify a file/folder to copy.")
	if dest == None:
		print("No destination provided.", end=' ')
		dest = DEFAULT_VM
	scp = SCPClient(client.get_transport(), progress=progress)
	try:
		scp.put(src, recursive=True, remote_path=dest)
	except SCPException:
		raise SCPException("File not found")
	finally:
		scp.close()
	print("Copying %s to %s" % (src, dest))

def main():
	client = connect()
	if len(sys.argv) < 2:
		raise Exception("Error")
	set_environment()
	if sys.argv[1] == "upload":
		if len(sys.argv) < 3:
			raise Exception("Not enough arguments")
		if len(sys.argv) == 3:
			upload(client, sys.argv[2], None)
		else:
			upload(client, sys.argv[2], sys.argv[3])
	elif sys.argv[1] == "get":
		if len(sys.argv) == 2:
			get(client, None, None)
		elif len(sys.argv) == 3:
			get(client, sys.argv[2], None)
		else:
			get(client, sys.argv[2], sys.argv[3])
	else:
		raise Exception("Unknown command")
	client.close()

main()
