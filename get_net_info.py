import sys,os
#from ipwhois import IPWhois
from pprint import pprint
import geoip2.database

def geoip_query(ip_address):
    #reader_city = geoip2.database.Reader('./GeoLite2-City/GeoLite2-City.mmdb')
    reader_city = geoip2.database.Reader('./GeoLite2-City.mmdb')
    try:
        response_city = reader_city.city(ip_address)
        country_code = response_city.country.iso_code
        city = response_city.city.name

        if country_code == None:
            country_code = ""
        if city == None:
            city = ""
    except geoip2.errors.AddressNotFoundError:
        country_code = city = ""
    return [country_code, city.replace("\\", " ").replace("\"", " ")]

f=open("allproxy.txt","r")
proxy=[]
for i in f.readlines():
    proxy.append(i)

f.close() 

f=open("proxy_whois.txt","w")
for i in proxy:
    ip=i.split(":")[0]
    try:
        cmd = "whois -h whois.cymru.com " + ip
        #cmd = "whois -h whois.radb.net " + ip
        buff=os.popen(cmd, 'r', 2)
        seg=[]
        for l in buff:
            if l.find("AS Name")<0 and l.find("whois.cymru.com")<0:
                seg=l.split("|")
                #pprint(seg)
        if seg[0]==None:
            seg[0]=""
            seg[1]=""
            seg[2]=""
        geo=geoip_query(ip)
        print(ip+","+i.split(":")[1].strip("\n")+","+seg[0].strip()+","+seg[2].split(",")[0].strip()+","+geo[0]+","+geo[1])
        f.write(ip+","+i.split(":")[1].strip("\n")+","+seg[0].strip()+","+seg[2].split(",")[0].strip()+","+geo[0]+","+geo[1]+"\n")
    #    print(results['asn']+","+results['asn_country_code']+","+results['nets'][0]['name']+","+results['nets'][0]['state'])
    except Exception as err:
        print(err)

f.close()
