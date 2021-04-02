import yaml
import ipaddress
from itertools import islice
import os
from jinja2 import Environment, PackageLoader
from doreah.control import mainfunction


jenv = Environment(
    loader=PackageLoader('proxymloxy','.')
)
jtmpl = jenv.get_template("configfile.jinja")

def load_yml_file(name):
	try:
		with open(name,"r") as ymlfile:
			info = yaml.safe_load(ymlfile)
		return info
	except:
		print("Input file",name,"could not be found!")
		return False

def write_conf_file(txt,name):
	#if not os.path.exists(name) or ask("Overwrite " + name):
	
	try:
		os.makedirs(os.path.dirname(name),exist_ok=True)
		with open(name,"w") as conffile:
			conffile.write(txt)
		return True
	except:
		print("Output file",name,"could not be written!")
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
		
			server['names'] = [name + "." + domain['domain'] for name in server['names']]
		
			if server["ipv6"]:
				host = int(str(server["host"]),16) - 1
				server['ip'] = "[" + str(next(islice(ipv6network.hosts(),host,None))) + "]"
			else:
				host = int(server["host"]) - 1
				server['ip'] = str(next(islice(ipv4network.hosts(),host,None)))
				
	return jtmpl.render(**info)
	


def translate(input,output):
	data = load_yml_file(input)
	if data is not False:
		result = create_conf_file_new(data)
		return write_conf_file(result,output)
	return False
	

def restart_nginx():
	os.system("sudo systemctl restart nginx.service")
	
@mainfunction({'i':'input','o':'output'},shield=True)
def main(input="proxymloxy.yml",output="/etc/nginx/conf.d/proxymloxy.conf"):
	if translate(input,output): restart_nginx()
