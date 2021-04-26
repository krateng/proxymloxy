name = "proxymloxy"
desc = "Reverse Proxy Manager with simple YAML configuration"
author = {
	"name":"Johannes Krattenmacher",
	"email":"proxymloxy@dev.krateng.ch",
	"github": "krateng"
}
version = 1,1,3
versionstr = ".".join(str(n) for n in version)
links = {
	"pypi":"proxymloxy",
	"github":"proxymloxy"
}
python_version = ">=3.6"
requires = [
	"jinja2",
	"ipaddress",
	"PyYAML",
	"doreah"
]
resources = [
	"configfile.jinja"
]

commands = {
	"proxymloxy":"proxymloxy:main"
}
