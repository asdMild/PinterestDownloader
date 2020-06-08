import py3pin.Pinterest as Pinterest
import json, os, requests, time

mainpath = os.path.dirname(os.path.abspath(__file__))
username = ""
try:
    username = input("please input user name")
except:
    input("invalid user name")
    exit(0)


# 检查url是否是200
def isValidUrl(url):
    i = 0
    while i < 3:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            if requests.options(url, timeout=5, headers=headers).status_code == 200:
                return True
            if requests.get(url, timeout=5, headers=headers).status_code == 200:
                return True
            raise ConnectionError
        except requests.exceptions.RequestException:
            i += 1
        except:
            return False
    return False


# 从原始网站下载
def downloadFromUrl(url, DownloadPath, name='', type='jpg'):
    type = type.strip('.')
    # remove 因为下面做了try
    #if not isValidUrl(url):
        #return None
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    file_path = DownloadPath
    zip_url = url
    try:
        os.mkdir(file_path)
    except Exception:
        pass
    if not os.path.exists(DownloadPath):
        os.makedirs(DownloadPath)

    if name == '':
        name = 'temp'
    zip_path = os.path.join(file_path, name+'.'+type)

    print(DownloadPath+name, "begin downloading")
    #if not os.path.exists(zip_path):
    try:
        r = requests.get(zip_url, stream=True, headers=headers, timeout=15)
        length = float(r.headers['content-length'])
        f = open(zip_path, 'wb+')
        count = 0
        count_tmp = 0
        time1 = time.time()
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 2:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    print('\r'+zip_path + ': ' + '{:.2f}'.format(p) + '%' + ' Speed: ' + '{:.2f}'.format(speed) + 'M/S',end = '', flush=True)
                    time1 = time.time()
        f.close()
        print(DownloadPath+name, "download finished")
    except:
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except:
            pass
        if not isValidUrl(url):
            print(url + " invalid url")
        print(DownloadPath+name, "download failed")
    if os.path.exists(zip_path):
        return zip_path
    else:
        return None


def readOldJson(boardname='', name='result'):
    if not os.path.exists(mainpath + '/' + username + '/'+boardname+'/'):
        os.makedirs(mainpath + '/' + username + '/'+boardname+'/')
    if os.path.exists(mainpath + '/' + username + '/'+boardname+'/' + name+'.json'):
        with open(mainpath + '/' + username + '/' +boardname+'/'+ name+'.json', 'r', encoding='utf-8') as result_file:
            try:
                json_result = json.load(result_file)
            except:
                json_result = {}
    else:
        json_result = {}
    return json_result

def writeJson(data,boardname='', name='result'):
    with open(mainpath + '/' + username + '/' +boardname+'/'+ name+'.json', 'w+', encoding='utf-8') as result_file:
        json.dump(data, result_file, ensure_ascii=False)

def downloadBoard(Boardid):
    pins = p.board_feed(board_id=Boardid)
    d = readOldJson(pins[0]['board']["name"])
    f = readOldJson(pins[0]['board']["name"], name='fail')
    for pin in pins:
        try:
            if pin["image_signature"] in d.keys():
                continue
            else:
                try:
                    images = pin["images"]
                    k = sorted(images.values(), key=lambda x: (-x['width']))
                    url = k[0]['url']
                except:
                    url = ''

                returncode = None
                if url != '':
                    if not os.path.exists(mainpath + '/' + username + '/' + pin['board']["name"] + '/'):
                        os.makedirs(mainpath + '/' + username + '/' + pin['board']["name"] + '/')
                    returncode = downloadFromUrl(url, DownloadPath=mainpath + '/' + username + '/' + pin['board'][
                        "name"] + '/', name=pin["image_signature"])
                if returncode != None:
                    d[pin["image_signature"]] = url
                else:
                    f[pin["image_signature"]] = pin
        except:
            continue

    writeJson(d, pins[0]['board']["name"])
    writeJson(f, pins[0]['board']["name"], 'fail')



p = Pinterest.Pinterest()
boards = p.boards(username=username)
pins = []
for b in boards:
    downloadBoard(b['id'])


input("download finished")