import subprocess
from time import sleep
import os
import ipaddress
import getpass
import json
import platform

def error(message = "Exit with error"):
	platformOS()
	print(f"Error: {message}")

def validate_subnet(subnet):
	try:
		ipaddress.ip_network(subnet, strict=True)
		return True
	except ValueError:
		return False
	
def platformOS():
	if platform.system() == 'Windows':
		subprocess.run("cls", shell=True)
	else:
		subprocess.run("clear", shell=True)

try:
	with open("./config.json", "r") as user:
		CONF = json.loads(user.read())

	if (CONF.get("users") and len(CONF["users"])>0) and CONF.get("config_dir") and CONF.get("config_file") and CONF.get("admin_user") and CONF.get("ports") and len(CONF["ports"])>0:
		LIST_USERPASWWORD = CONF["users"]
		LIST_PORT = CONF['ports'] 
		CONF_DIR = CONF["config_dir"]
		CONF_FILE = CONF["config_file"]
		ADMIN_NAME = CONF["admin_user"]

		subprocess.run("apt install samba samba-common", shell=True)
			
		admin_pass = getpass.getpass("Enter admin password: ")
		subprocess.run(f'(echo "{admin_pass}"; echo "{admin_pass}") | smbpasswd -a -s {ADMIN_NAME}', shell=True)

		with open(os.path.join(CONF_DIR, CONF_FILE), "a") as mm:
			mm.write(f"\ninclude = /home/{ADMIN_NAME}/users.conf")

		with open(os.path.join(f"/home/{ADMIN_NAME}", "users.conf"), "a") as f:
			for item in LIST_USERPASWWORD["users"]:
				conf = f"""
		[{item['user']}]
		comment = {item['user']}
		path = /home/{item['user']}
		browsable = yes
		guest ok = no
		read only = no
		create mask = 0770
		directory mask = 0770
		writable = yes
		valid users = {ADMIN_NAME}, {item['user']}
		security mask = 0770
		directory security mask = 0770
				"""
				f.write(conf)
				
		for item in LIST_USERPASWWORD["users"]:
			sleep(0.5)
			subprocess.run(f"mkdir -p /home/{item['user']}", shell=True)
			subprocess.run(f"chown {item['user']}:{ADMIN_NAME} /home/{item['user']}", shell=True)
			subprocess.run(f"chmod 770 /home/{item['user']}", shell=True)
			subprocess.run(f"useradd {item['user']}", shell=True)
			subprocess.run(f"(echo {item['user']}:{item['password']}) | chpasswd", shell=True)
			subprocess.run(f'(echo "{item["password"]}"; echo {item["password"]}) | smbpasswd -a -s {item["user"]}', shell=True)

		conf_net = str(input("Would you like to apply port settings and write them to iptables? (y/n): "))
		if (conf_net != "n" and conf_net != "N" and conf_net != "no" and conf_net != "No"):
			while True:
				conf_subnet = str(input("Please enter your subnet and network mask in prefix notation (example: 0.0.0.0/0): "))
				if validate_subnet(conf_subnet):
					print("The subnet is entered correctly")
					break
				else:
					print("The subnet is entered incorrectly, please try again")
			
			for ports in LIST_PORT:
				subprocess.run(f"iptables -A INPUT -p {ports['protocol']} -m {ports['protocol']} --dport {ports['port']} -s {conf_subnet} -j ACCEPT", shell=True)
			
			subprocess.run("apt-get install iptables-persistent", shell=True)

		subprocess.run("service smbd restart", shell=True)
	else:
		print("Please check your configuration file")
except Exception:
	error()
except KeyboardInterrupt:
	error()