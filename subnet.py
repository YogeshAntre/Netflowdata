import ipaddress
def validate_subnet(subnet):
    #print(subnet)
    network = ipaddress.IPv4Network(subnet)
    #print(network)
    return 1<= network.prefixlen <= 32
def generate_ips(subnet):

        if validate_subnet(subnet):
            network = ipaddress.IPv4Network(subnet)
            ip_list = [str(ip) for ip in network.hosts()]
            #print(ip_list)
            return ip_list
        else:
            return ({"status":False,"msg":"Invalid range select range between /16 to /30"})
# (generate_ips("10.17.0.0/16"))