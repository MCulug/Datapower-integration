import requests
import os
import time
import filecmp
import shutil
import xml.etree.ElementTree as ET
import base64
##############################################################################################################################################
#This code requires be trigred with a cronjob or it can be modified to run as a daemon to triger it self. My suggestion is to run every 5 min#
##############################################################################################################################################
def fetch(pathi):                             #Fetch function takes path to audit file as argument and sends fetch request to server
 request= """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
<soapenv:Body>
<dp:request domain="default" xmlns:dp="http://www.datapower.com/schemas/management">
<dp:get-file name="%s"/>
</dp:request>
</soapenv:Body>
</soapenv:Envelope>""" %pathi                  #5550 is the default port of xml management interface in IBM datapower server which must be enabled before execution
 host="https://mgmt-kxesadpwd1.isbank:5550"
 AUTH = 'admin', 'devadmin'
 headers = {'Content-Type':'text/xml;charset=UTF-8'}
 XMLResp = requests.post(host, data=request, verify=False, headers=headers, auth=(AUTH))
 root = ET.fromstring(XMLResp.content)
 for child in root.iter('*'):
  if(str(child.tag) == "{http://www.datapower.com/schemas/management}file"):
   base64_message = child.text
   base64_bytes = base64_message.encode('ascii')
   message_bytes = base64.b64decode(base64_bytes)   #The server response is base64 encoded. We will decode and rename it
   message = message_bytes.decode('ascii')
   file = open("audit_new", "w+")
   file.write(message)
   file.close()

if os.path.isfile('switch/audit-log'):
 print (os.path.isfile('switch/audit-log')) 
 print ("Working with audit-log file")               #/switch and /audit directories must be created before running code. 
 fetch("audit:///audit-log")
 if (os.path.getsize('audit_new') >= os.path.getsize('switch/audit-log')) == True:
  print('New audit-log file will be overriden')
  os.remove('switch/audit-log')
  shutil.move('audit_new', 'switch/audit_new')
  os.rename('switch/audit_new', 'switch/audit-log')
 else:
  time = str(time.strftime("%d %B %Y %H:%M:%S"))
  print('files match. Move file to permanant audit directory')
  shutil.move('switch/audit-log', 'Audit/audit-log')
  os.rename('Audit/audit-log', 'Audit/'+time)
  file = open("switch/audit-log","w")
  print ("open file audit-log")
  file.close()
