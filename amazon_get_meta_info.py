#!/usr/bin/env python

import re, sys, string
import bs4,json

import logging
logger = logging.getLogger()

def get_seconds(str):
    try:
        seconds = 0
        if str=='':
            return seconds
        if '時間' in str and '分' in str:
            strs = str.split('時間')
            hours = strs[0]
            min_str = strs[1]
            min_strs = min_str.split('分')
            min = min_strs[0]
            seconds = 60 * 60 * int(hours) + 60 * int(min)
        elif 'h' in str:
            if ' ' in str:
                strs = str.split(' ')
                hours = strs[0]
                min = strs[2]
                seconds = 60 * 60 * int(hours) + 60 * int(min)
            else:
                if 'min' in str:
                    str = str[:-3]
                    strs = str.split('h')
                    hours = strs[0]
                    min = strs[1]
                    seconds = 60 * 60 * int(hours) + 60 * int(min)
                else:
                    str = str[:-1]
                    seconds = 60 * 60 * int(str)
        else:
            if ' ' in str:
                strs = str.split(' ')
                min = strs[0]
                seconds = 60 * int(min)
            else:
                str = str[:-3]
                seconds = 60 * int(str)
                pass

    except Exception:
        return 0

    return seconds

EU_REGION = "atv-ps-eu"
JP_REGION = "atv-ps-fe"
US_REGION = "atv-ps"

ROW_NA = "ART4WZ8MWBX2Y"
ROE_EU = "A3K6Y4MI8GDYMT"
ROW_EU = "A2MFUE2XK8ZSSY"
ROW_FE = "A15PK738MTQHSO"

DE = "A1PA6795UKMFR9"
JP = "A1VC38T7YXB528"
UK = "A1F83G8C2ARO7P"
US = "ATVPDKIKX0DER"

def getDomainFromMarketplaceId(marketplaceID):

    if marketplaceID==ROW_NA or marketplaceID==ROE_EU or marketplaceID==ROW_EU or marketplaceID==ROW_FE:
        return ".primevideo.com"
    if marketplaceID==DE:
        return ".amazon.de"
    if marketplaceID==JP:
        return ".amazon.co.jp"
    if marketplaceID==UK:
        return ".amazon.co.uk"
    return ".amazon.com"

def getAVTFromMarketplaceId(marketplaceID):

    if marketplaceID==ROW_NA or marketplaceID==US:
        return US_REGION
    if marketplaceID==ROE_EU or marketplaceID==ROW_EU or marketplaceID==UK or marketplaceID==DE:
        return EU_REGION
    if marketplaceID==ROW_FE or marketplaceID==JP:
        return JP_REGION
    raise("getAVTFromMarketplaceId error")

def get_meta_info(webpage):
    amazonSoup = bs4.BeautifulSoup(webpage,'html5lib')

    reJson = r'"marketplaceID":"(.*?)"'
    marketplaceID = re.findall(reJson, webpage)[0]

    domain = getAVTFromMarketplaceId(marketplaceID) + getDomainFromMarketplaceId(marketplaceID)

    movie_play_url = ''
    movie_play_urls = amazonSoup.select('.dv-dp-node-playback')
    if len(movie_play_urls)!=0:
        movie_play_url = movie_play_urls[0].find("a")['href']

    current_id = ""
    if amazonSoup.find("ol",class_="_3kgCxW")!=None:
        lis = amazonSoup.find("ol",class_="_3kgCxW").find_all("li")
        for index in range(len(lis)):
            li = lis[index]
            href = ""
            if li.find("a")==None:
                continue
            if not(li.find("a").has_attr('href')):
                continue
            href= li.find("a")['href']
            episodeId = ""
            if li.find("label")!=None:
                episodeId = li.find("label")['for'].replace('selector-','')
            if href.split('ref')[0] == movie_play_url.split('ref')[0]:
                current_id = episodeId

    reLocale = r'"locale":"(.*?)"'
    locale = re.findall(reLocale, webpage)[0]

    reKeywordTitle = r'"keywords":\["(.*?)"\]'
    tmp_keyword_title = re.findall(reKeywordTitle, webpage)
    reTitle = r'"parentTitle":"(.*?)"'
    tmp_title = re.findall(reTitle, webpage)

    h1_title=""
    h1_elements = amazonSoup.findAll('h1')
    for h1_element in h1_elements:
        if h1_element.find('img') :
            h1_title=h1_element.find('img').attrs["alt"]
        pass

    main_element = amazonSoup.find('main',attrs={'id':'main','data-testid':'detailpage-main'})

    if len(amazonSoup.select('._2Q73m9'))!=0:
        title = amazonSoup.select('._2Q73m9')[0].string
    elif len(amazonSoup.find_all(attrs={'data-automation-id':'title'}))!=0:
        title = amazonSoup.find_all(attrs={'data-automation-id':'title'})[0].string
    elif h1_title:
        title = h1_title
    elif len(tmp_keyword_title)!=0:
        title = tmp_keyword_title[0] 
    elif len(tmp_title)!=0:
        title = tmp_title[0]
    else:
        title = amazonSoup.title.string
    
    release_time = ''
    release_times = amazonSoup.find_all(attrs={'data-automation-id':'release-year-badge'})
    if len(release_times)==1:
        release_time = release_times[0].string
    runtime_strs = amazonSoup.find_all(attrs={'data-automation-id':'runtime-badge'})
    runtime_str = ""
    if len(runtime_strs)==1:
        runtime_str = runtime_strs[0].string
    runtime = get_seconds(runtime_str)
    
    synopsis = ''
    e_synopsis = amazonSoup.select('._1wxob_')
    if len(e_synopsis)==0:
        e_synopsis = amazonSoup.select('._3qsVvm')
    if len(e_synopsis)==0 and main_element is not None:
        e_synopsis = main_element.select('._5tB6mN')
    if len(e_synopsis)==0 and main_element is not None:
        e_synopsis = main_element.select('.dv-dp-node-synopsis')
    if len(e_synopsis)!=0:
        synopsis = e_synopsis[0].string

    thumbs = ''
    e_thumb = amazonSoup.select('#atf-full')
    if len(e_thumb)!=0:
        thumbs = e_thumb[0]['src']
    if not thumbs:
        e_thumb = amazonSoup.find("img", class_="_2x6L3o")
        if e_thumb:
            thumbs = e_thumb['src']
    if not thumbs:
        div_thumb = amazonSoup.find(attrs={'data-automation-id':'hero-background'})
        if div_thumb:
            e_thumb = div_thumb.find("img")
        if e_thumb:
            thumbs = e_thumb['src']

    if current_id=="":
        reCurrentId = r'"pageTitleId":"(.*?)"'
        current_ids = re.findall(reCurrentId, webpage)
        if len(current_ids)!=0:
            current_id = re.findall(reCurrentId, webpage)[0]

    try:
        audios = []
        subtitles = []

        meta_info = amazonSoup.select('.dv-dp-node-meta-info')
        if (len(meta_info) > 0):
            l = len(meta_info[0].select('._2czKtE'))
            if (l==1):
                e_audios = amazonSoup.select('.dv-dp-node-meta-info')[0].select("._2czKtE")[0].select('dd')[0].text
                for e_audio in e_audios.split(','):
                    if '…' in e_audio:
                        e_audio = e_audio.split('…')[1]
                    audios.append(e_audio)
            else:
                e_subtitles = amazonSoup.select('.dv-dp-node-meta-info')[0].select('._2czKtE')[0].select('dd')[0].text
                e_audios = amazonSoup.select('.dv-dp-node-meta-info')[0].select("._2czKtE")[1].select('dd')[0].text
                for e_audio in e_audios.split(','):
                    if '…' in e_audio:
                        e_audio = e_audio.split('…')[1]
                    audios.append(e_audio)
                for e_subtitle in e_subtitles.split(','):
                    if '…' in e_subtitle:
                        e_subtitle = e_subtitle.split('…')[1]
                    subtitles.append(e_subtitle)

    except Exception as e:
        audios = ['English']
        subtitles = ['English']
    # if 'primevideo.com' not in domain:
        # current_id = ""

    genres = []
    if main_element is not None:
        genres_div = main_element.find('div', {'class': 'dv-node-dp-genres'})
        if genres_div:
            genres_spans = genres_div.find_all('span', {'aria-label': True})
            for span in genres_spans:
                genres.append(span.get('aria-label'))
        # if genres is not None or len(genres) != 0:
            # print(genres)


    directors = []
    casts =[]
    try:
        if main_element is not None:
            div_product_detail = main_element.find(attrs={'data-automation-id':'btf-product-details'})
            if div_product_detail:
                directors_dl = div_product_detail.find_all('dl')
                for dl in directors_dl:
                    dt = dl.find('dt', string='Directors')
                    if dt:
                        directors = [director.text for director in dt.find_next_sibling('dd').find_all('a')]
                        break

                casts_dl = div_product_detail.find_all('dl')
                for dl in casts_dl:
                    dt = dl.find('dt', string='Starring')
                    if dt:
                        casts = [cast.text for cast in dt.find_next_sibling('dd').find_all('a')]
                        break

    except Exception as e:
        logger.info(str(e))
        directors = []
        casts = []
    
    # if casts:
    #     print('casts :',casts)
    # if directors:
    #     print("directors :",directors)


    info = {
        "id": current_id,
        "marketplaceID":marketplaceID,
        "domain":domain,
        "locale":locale,
        "movie_play_url":movie_play_url,
        "title": title,
        "release_time": release_time,
        "runtime": runtime,
        "runtime_str":runtime_str,
        "subtitles":subtitles,
        "audios":audios,
        "synopsis": synopsis,
        "thumbs": thumbs,
        "directors": directors,
        "casts": casts,
        "writers": [],
        "genres": genres,
        "moodTags": []
    }

    return info

def run(params):
    arrParams = list(params)
    log_path = ''
    for index in range(len(arrParams)):
        if index==0:
            log_path = arrParams[index]
        elif index==1:
            output_file = arrParams[index]
        else:
            input_file= arrParams[index]
    
    # set logging
    log_handler = logging.FileHandler(log_path)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    try:
        f = open(input_file,'r',encoding='UTF-8')
        webpage = f.read()
        f.close()

        info = get_meta_info(webpage)

        with open(output_file,"w",encoding='UTF-8') as f:
            json.dump(info,f)
        logger.info("get_meta_info complete...")

    except Exception as e:
        logger.exception(str(e))

import os
if __name__ == '__main__':

    params = [
        "./python.log",
        "./get_meta_info.json",
        "./amazonGetMetaInfoTempIn.html",
    ]

    if os.path.exists(params[0]):
        os.remove(params[0])
    if os.path.exists(params[1]):
        os.remove(params[1])

    run(params)