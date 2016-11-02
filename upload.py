#coding: utf-8
import os
import re
import requests
import sys

if len(sys.argv) == 2:
    mainpath = sys.argv[-1]
else:
    exit()

temppath = r'G:\mydownload\GETUI_ANDROID_SDK\GETUI_ANDROID_SDK\Demo\PushDemo\yijia\temp.apk'

cmd = 'curl -F "file=@{path}" -F "uKey=xxx" -F "_api_key=xxx" http://www.pgyer.com/apiv1/app/upload'
content = os.popen(cmd.format(path=mainpath)).read()
print(content)

match = re.search('"appKey":"(\w+)"', content)

if match:
    appkey = match.group(1)

    content = os.popen(cmd.format(path=temppath)).read()

    url = 'http://static.pgyer.com/' + appkey
    html = requests.get(url).text

    match = re.search('http://static.pgyer.com/app/qrcodeHistory/\w+', html)
    if match:
        print('appKey#{soonAppkey}#appKeysoon#{soon}#soon'.format(soonAppkey=appkey,soon=match.group()))
    else:
        print('no qrcode')
