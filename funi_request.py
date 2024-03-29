import requests
import json
import logging
def hello():
    print('hello')
    pass

def api_request(id, token, output_file):

    # logging.basicConfig(level=logging.INFO,
    #                 format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                 datefmt='%m-%d %H:%M',
    #                 filename='e:\\myapp.log',
    #                 filemode='w')

    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # # tell the handler to use this format
    # console.setFormatter(formatter)
    # logging.getLogger('').addHandler(console)

    hdr = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0' }
    hdr['devicetype'] = 'Android Phone'
    hdr['Authorization'] = 'Token {}'.format(token)

    url= 'https://prod-api-funimationnow.dadcdigital.com/api/source/catalog/video/{}/signed'.format(id)
    print('{}'.format(url))
    r= requests.get(url, headers=hdr)
    try:
        x = r.json()
        with open(output_file, "wb") as file:
            file.write(bytes(json.dumps(x), encoding='utf-8'))
    except:
        return None

if __name__ == '__main__':
    # id = '1399964'
    id = '1398850'
    outputdir = 'C:\\Users\\fab\\AppData\\Local\\Temp\\'
    outputfile='{}{}.json'.format(outputdir, id)
    api_request(id, '5b506b51f20f11512db78d1ee944dad001a5d398', outputfile)
