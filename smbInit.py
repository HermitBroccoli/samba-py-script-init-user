import subprocess
from time import sleep
import os
import ipaddress

subprocess.run("apt install samba samba-common", shell=True)

def validate_subnet(subnet):
    try:
        ipaddress.ip_network(subnet, strict=True)
        return True
    except ValueError:
        return False

CONF_DIR = "/etc/samba"
CONF_FILE = "smb.conf"

admin_name = str(input("Enter admin username: "))
admin_pass = str(input("Enter admin password: "))
subprocess.run(f'(echo "{admin_pass}"; echo "{admin_pass}") | smbpasswd -a -s {admin_name}', shell=True)

LIST_PORT = [
	{"port": 445, "protocol": "tcp"},
	{"port": 139, "protocol": "tcp"},
	{"port": 138, "protocol": "udp"},
	{"port": 137, "protocol": "udp"},
]

LIST_USERPASWWORD = [
	{"user": 'student1', "password": 'student1'},
	{"user": 'student2', "password": 'student2'},
	{"user": 'student3', "password": 'student3'},
	{"user": 'student4', "password": 'student4'},
	{"user": 'student5', "password": 'student5'},
	{"user": 'student6', "password": 'student6'},
	{"user": 'student7', "password": 'student7'},
	{"user": 'student8', "password": 'student8'},
	{"user": 'student9', "password": 'student9'},
	{"user": 'student10', "password": 'student10'},
] 

with open(os.path.join(CONF_DIR, CONF_FILE), "a") as mm:
	mm.write(f"\ninclude = /root/users.conf")

with open(os.path.join("/root", "users.conf"), "a") as f:
	for item in LIST_USERPASWWORD:
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
		valid users = {admin_name}, {item['user']}
		security mask = 0770
		directory security mask = 0770
		
		"""
		f.write(conf)
        
for item in LIST_USERPASWWORD:
	sleep(0.5)
	subprocess.run(f"mkdir -p /home/{item['user']}", shell=True)
	subprocess.run(f"chown {item['user']}:{admin_name} /home/{item['user']}", shell=True)
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