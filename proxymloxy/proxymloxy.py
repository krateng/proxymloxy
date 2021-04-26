import yaml
import ipaddress
from itertools import islice
import os
from jinja2 import Environment, PackageLoader
from doreah.control import mainfunction

NGINX_CONF_FILE = "/etc/nginx/conf.d/proxymloxy.conf"
PROXYMLOXY_CONF_FILE = "./proxymloxy.yml"
CONTAINER_CONF_FILE = "/etc/pve/lxc/{cid}.conf"
AUTH_FILE = "/etc/nginx/auth"


jenv = Environment(
    loader=PackageLoader('proxymloxy','.')
)
jtmpl = jenv.get_template("configfile.jinja")

def load_container_ip(cid,ipv6=True):
	with open(CONTAINER_CONF_FILE.format(cid=cid)) as fd:
		lines = fd.readlines()
	print(f"Loaded container {cid} configuration")
	info = dict([entry.split('=') for entry in [l for l in lines if l.startswith('net0: ')][0].split(": ")[-1].split(",")])

	if ipv6:
		return ipaddress.IPv6Interface(info['ip6']).ip
	else:
		return ipaddress.IPv4Interface(info['ip']).ip

def load_yml_file():
	try:
		with open(PROXYMLOXY_CONF_FILE,"r") as ymlfile:
			info = yaml.safe_load(ymlfile)
		print("Loaded configuration")
		global NGINX_CONF_FILE, CONTAINER_CONF_FILE, AUTH_FILE
		if "filepaths" in info:
			if "nginx_config_file" in info['filepaths']: NGINX_CONF_FILE = info['filepaths']['nginx_config_file']
			if "container_conf_file_template" in info['filepaths']: CONTAINER_CONF_FILE = info['filepaths']['container_conf_file_template']
			if "auth_file" in info['filepaths']: AUTH_FILE = info['filepaths']['auth_file']

		# now write stuff back into the loaded data in case it came from a different source and we need it inside the template
		info['filepaths']['nginx_config_file'] = NGINX_CONF_FILE
		info['filepaths']['container_conf_file_template'] = CONTAINER_CONF_FILE
		info['filepaths']['nginx_config_file'] = NGINX_CONF_FILE
		return info
	except:
		print("Input file",PROXYMLOXY_CONF_FILE,"could not be found!")
		return False

def write_conf_file(txt):
	if os.path.exists(NGINX_CONF_FILE):
		try: os.replace(NGINX_CONF_FILE,NGINX_CONF_FILE + ".old")
		except:	print("Could not back up old config file, do you have permissions?")

	try:
		os.makedirs(os.path.dirname(os.path.abspath(NGINX_CONF_FILE)),exist_ok=True)
		with open(NGINX_CONF_FILE,"w") as conffile:
			conffile.write(txt)
		print("Wrote nginx config file")
		return True
	except:
		print("Output file",NGINX_CONF_FILE,"could not be written!")
		return False


def create_conf_file_new(info):

	ipv4network = ipaddress.IPv4Network(info["network_ipv4"])
	ipv6network = ipaddress.IPv6Network(info["network_ipv6"])
	info['network'] = {'v4':str(ipv4network),'v6':str(ipv6network)}


	for domain in info['domains']:
		for server in domain['servers']:

			if not "ipv6" in server: server["ipv6"] = True
			if not "settings" in server: server["settings"] = []
			if not "private" in server: server["private"] = False
			if not "restricted" in server: server["restricted"] = False
			if not "custompath" in server: server["custompath"] = ""
			if not "port" in server: server["port"] = 80

			server['names'] = [name + "." + domain['domain'] for name in server['names']]


			if server["ipv6"]:
				if "container" in server:
					server['ip'] = load_container_ip(server["container"],ipv6=True)
				else:
					host = int(str(server["host"]),16) - 1
					server['ip'] = "[" + str(next(islice(ipv6network.hosts(),host,None))) + "]"
			else:
				if "container" in server:
					server['ip'] = load_container_ip(server["container"],ipv6=False)
				else:
					host = int(server["host"]) - 1
					server['ip'] = str(next(islice(ipv4network.hosts(),host,None)))

	return jtmpl.render(**info)



def translate():
	data = load_yml_file()
	if data is not False:
		result = create_conf_file_new(data)
		return write_conf_file(result)
	return False


def restart_nginx():
	print("Restarting Nginx")
	os.system("sudo systemctl restart nginx.service")
	print("Success!")

@mainfunction({'i':'inputf','o':'outputf','c':'containerc','a':'authf'},shield=True)
def main(inputf=PROXYMLOXY_CONF_FILE,outputf=NGINX_CONF_FILE,containerc=CONTAINER_CONF_FILE,authf=AUTH_FILE):

	global PROXYMLOXY_CONF_FILE, NGINX_CONF_FILE, CONTAINER_CONF_FILE, AUTH_FILE
	PROXYMLOXY_CONF_FILE = inputf
	NGINX_CONF_FILE = outputf
	CONTAINER_CONF_FILE = containerc
	AUTH_FILE = authf

	if translate(): restart_nginx()
