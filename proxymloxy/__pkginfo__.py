name = "proxymloxy"
desc = "Reverse Proxy Manager with simple YAML configuration"
author = {
	"name":"Johannes Krattenmacher",
	"email":"proxymloxy@dev.krateng.ch",
	"github": "krateng"
}
version = 1,0,0
versionstr = ".".join(str(n) for n in version)
links = {
	"pypi":"proxymloxy",
	"github":"proxymloxy"
}
python_version = ">=3.6"
requires = [
	"jinja2",
	"ipaddress",
	"yaml",
	"doreah"	
]
resources = [
]

commands = {
	"proxymloxy":"proxymloxy:translate"
}
