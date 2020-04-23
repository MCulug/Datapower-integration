import requests
import os
import time
import filecmp
import shutil
import xml.etree.ElementTree as ET
import base64

def fetch(path):                                                              #Fetch function takes path to audit file as argument and sends fetch request to server
 request= """<?xml version="1.0" encoding="UTF-8"?>                                  
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
<soapenv:Body>
<dp:request domain="default" xmlns:dp="http://www.datapower.com/schemas/management">
<dp:get-file name="%s"/>
</dp:request>
</soapenv:Body>
</soapenv:Envelope>""" %path
 host="https://yourDatapowerHost:5550"                                        #5550 is the default port of xml management interface in IBM datapower server
 AUTH = 'admin', 'XXXXXXXXX'
 headers = {'Content-Type':'text/xml;charset=UTF-8'}
 z = requests.post(host, data=request, verify=False, headers=headers, auth=(AUTH))
 root = ET.fromstring(z.content)
 for child in root.iter('*'):
  if(str(child.tag) == "{http://www.datapower.com/schemas/management}file"):  #The server response is base64 encoded. We will decode and rename it 
   base64_message = child.text
   base64_bytes = base64_message.encode('ascii')
   message_bytes = base64.b64decode(base64_bytes)
   message = message_bytes.decode('ascii')
   file = open("audit_new.txt", "w+")
   file.write(message)
   file.close()

if os.path.isfile('switch/audit-log'):                                        #Here is the switch mechanism. These two if statements will switch audit-log and audit-log.1 file
 print ("Working with audit-log file")
 fetch("audit:///audit-log")
 if filecmp.cmp('audit_new.txt', 'switch/audit-log') == False:
  print('files sizes are different. New log file will be overriden')          #switch and audit directories must be created before running code. 
  os.remove('switch/audit-log')
  shutil.move('audit_new.txt', 'switch/audit_new.txt')
  os.rename('switch/audit_new.txt', 'switch/audit-log')
 else:
  time = str(time.strftime("%d %B %Y %H:%M:%S"))
  print('files match. Move file to permanant audit directory and switching to other log file audit-log.1')
  shutil.move('switch/audit-log', 'Audit/audit-log')
  os.rename('Audit/audit-log', 'Audit/'+time+'.txt')
  file = open("audit-log.1","w")
  file.close()

if os.path.isfile('switch/audit-log.1'):
 print ("Working with audit-log.1 file")
 fetch("audit:///audit-log.1")
 if filecmp.cmp('audit_new.txt', 'switch/audit-log.1') == False:
  print('files sizes are different. New log file will be overriden')
  os.remove('switch/audit-log.1')
  shutil.move('audit_new.txt', 'switch/audit_new.txt')
  os.rename('switch/audit_new.txt', 'switch/audit-log.1')
 else:
  time = str(time.strftime("%d %B %Y %H:%M:%S"))
  print('files match. Move file to permanant audit directory and switching to other log file audit-log')
  shutil.move('switch/audit-log.1', 'Audit/audit-log.1')
  os.rename('Audit/audit-log.1', 'Audit/'+time+'.txt')
  file = open("audit-log","w")
  file.close()
