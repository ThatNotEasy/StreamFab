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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def get_episodes_info(episodes_data):
    episodes_array = []
    count = 1

    for part in episodes_data:
        lis = part.find_all("li")
        for index in range(len(lis)):
            li = lis[index]

            title = ''
            js_title = li.find("div", class_="js-episode-title-name")
            if not js_title:
                js_title = li.find("div", class_="dv-episode-noplayback-title")
            if not js_title:
                js_title = li.find("div", class_="_1TQ2Rs")
            if not js_title:
                js_title = li.find("div", class_="izvPPq")

            if not js_title:
                js_title = li.find("span", class_="S4388s")
            if not js_title:
                js_title = li.find("span", class_="P1uAb6")


            if js_title:
                title = js_title.text
            
            synopsis = ''
            js_synopsis = li.find("div", class_="_3qsVvm")
            if js_synopsis:
                synopsis = js_synopsis.string
 
            if li.find("a")==None:
                count += 1
                continue

            if not(li.find("a").has_attr('href')):
                count += 1
                continue

            play_url = ""
            play_url = li.find("a")['href']
            if play_url == None:
                count += 1
                continue
            
            if 'force_return_url' in play_url:
                count += 1
                continue

            episodeId = ""
            if li.find("label")!=None:
                episodeId = li.find("label")['for'].replace('selector-','')

            runtime_str = ''
            js_runtime = li.find("div", class_="_1DcCXQ _2_ujMf")
            if not js_runtime:
                js_runtime = li.find("div", class_="_3rBDNv _1AeKJC")
            if not js_runtime:
                js_runtime = li.find("div", class_="_1wFEYz ci7S35")
            if js_runtime:
                divs = js_runtime.find_all('div')
                if divs:
                    if len(divs) > 1:
                        runtime_str = divs[1].string
                    else:
                        runtime_str = divs[0].string
                
            runtime = get_seconds(runtime_str)
            
            thumbs_url = ''
            pic = li.find("picture")
            if pic:
                img = pic.find("img")
                thumbs_url = img['src']
                
            if not thumbs_url:
                img = li.find("img")
                if img:
                    thumbs_url = img['src']

            # positionStr = title.replace(" ",'').split('.')[0]
            # if(is_number(positionStr)):
            #     position = int(positionStr) 
            # else:
            #     position = count
            position = count

            e_obj = {
                    "seq": position,
                    "episodeId": episodeId,
                    "play_url": play_url,
                    "synopsis": synopsis,
                    "title": title,
                    "runtime": runtime,
                    "runtime_str":runtime_str,
                    "thumbs": {
                        "url": thumbs_url
                    }
                }

            count += 1
            episodes_array.append(e_obj)

    return episodes_array

def get_extras_info(extras_data):
    extras = {}

    for tag in extras_data:
        extras_tag = ''
        js_title = tag.find(class_='ROp-tf')
        if not js_title:
            js_title = tag.find(class_='Dsc37Q')  
        if js_title:
            extras_tag = js_title.text.replace(" ", "")
    
        extras_list = []
        lis = []
        ul = tag.find(class_="jxBPRE _28m62t")
        if ul:
            lis = ul.find_all("li")

        if not lis:
            lis = tag.find_all(class_="_1z3n6o")

        for index in range(len(lis)):
            li = lis[index]

            title = ""
            runtime_str = ""
            runtime = 0
            rating = ""
            play_id = ""
            play_url = ""
            synopsis = ""
            thumbs_url = ""

            js_playbutton = li.find('a', attrs={'data-automation-id':'extras-playbutton'})
            if not js_playbutton:
                continue
            if js_playbutton:
                play_url = js_playbutton['href']

            js_title = li.find("div", class_="vRplU5")
            if not js_title:
                js_title = li.find('span', class_="lTKTFD")
            if js_title:
                title = js_title.string

            js_runtime_str = li.find(attrs={'data-automation-id':'runtime-badge'})
            if js_runtime_str:
                runtime_str = js_runtime_str.string
                runtime = get_seconds(runtime_str)

            js_rating = li.find(class_="_2BZ5w7")
            if not js_rating:
                js_rating = li.find('span', class_="G8xF_x")
            if js_rating:
                rating = js_rating.string

            js_synopsis = li.find(class_="_16wNxC")
            if not js_synopsis:
                js_synopsis = li.find(class_="rPtVMq")
            if js_synopsis:
                synopsis = js_synopsis.string
            
            js_thumbs = li.find('img')
            if js_thumbs:
                thumbs_url = js_thumbs['src']

            js_data_asin = li.find(class_="_1Opa2_ dvui-packshot _3g93Un")
            if not js_data_asin:
                js_data_asin = li.find(class_="_1Opa2_ dvui-packshot _8eIApy")
            if js_data_asin:
                play_id = js_data_asin['data-asin']

            meta = {
                "title": title,
                "runtime": runtime,
                "runtime_str": runtime_str,
                "rating": rating,
                "play_id": play_id,
                "play_url": play_url,
                "synopsis": synopsis,
                "thumbs": {"url":thumbs_url},
            }
            extras_list.append(meta)

        extras[extras_tag] = extras_list

    return extras

def get_seasons_info(webpages):

    all_seasons = []

    for webpage in webpages:
        amazonSoup = bs4.BeautifulSoup(webpage,'html5lib')
        
        season_info = amazonSoup.find(class_="XR0d6P")   
        if not season_info:
            season_info = amazonSoup.find(class_="GG33WY")
        # if not season_info:
        #     season_info = amazonSoup.find(class_="dv-node-dp-seasons")
        if not season_info:
            continue

        pageTitleId = ''
        
        reCurrentId = r'"pageTitleId":"(.*?)"'
        page = re.findall(reCurrentId, webpage)
        if len(page) > 0:
            pageTitleId = page[0]

        if pageTitleId == '':
            reCurrentId = r'"originalURI":"(.*?)"'
            originalURI = re.findall(reCurrentId, webpage)
            if len(originalURI) > 0:
                originalURI = originalURI[0]
                match = re.search(r'/([A-Z0-9]+)\b', originalURI)
                if match:
                    pageTitleId = match.group(1)

        big_title = ''
        titles = amazonSoup.select('._2Q73m9')
        if len(titles)!=0:
            big_title = titles[0].string
        elif len(amazonSoup.find_all(attrs={'data-automation-id':'title'}))!=0:
            big_title = amazonSoup.find_all(attrs={'data-automation-id':'title'})[0].string
        else:
            big_title = amazonSoup.title.string
        
        release_year = ''
        if len(amazonSoup.find_all(attrs={'data-automation-id':'release-year-badge'}))!=0:
            release_year = amazonSoup.find_all(attrs={'data-automation-id':'release-year-badge'})[0].string

        season_name = ''
        dv_node_dp_seasons = amazonSoup.find_all(class_="dv-node-dp-seasons")
        if len(dv_node_dp_seasons)==0:
            dv_node_dp_seasons = amazonSoup.find_all(class_='dv-node-dp-seasons-default')
        
        if len(dv_node_dp_seasons)!=0:
            e_season = dv_node_dp_seasons[0].find(class_="_36qUej")
            if not e_season:
                e_season = dv_node_dp_seasons[0].find(class_="_3R4jka")

            if e_season:
                season_name = e_season.string

        if not season_name:   
            fclass = amazonSoup.find(class_="XqYSS8 dw87r6")
            if fclass:
                if len(fclass.select("._36qUej"))!=0:
                    season_name = fclass.select("._36qUej")[0].string
        
        if not season_name:
            fclass =amazonSoup.find_all(class_="XqYSS8 _1J8qi6")
            if len(fclass)!=0:
                season_name = fclass[0].string

        if not season_name:
            data_automation_id = amazonSoup.find(attrs={'data-automation-id':'title'})
            if data_automation_id:
                seasonNameDomList = data_automation_id.next_siblings
                for seasonNameDom in seasonNameDomList:
                    if type(seasonNameDom) is not bs4.element.NavigableString:
                        seasonNameDomStr = seasonNameDom.get_text().strip().replace('\n', '').replace('\r', '').strip()
                        if "Season 1"==seasonNameDomStr:
                            season_name = seasonNameDomStr
                        elif "Season 1" in seasonNameDomStr:
                            season_name = seasonNameDomStr.split('Season 1')[0].strip().replace('\n', '').replace('\r', '').strip()
                        else:
                            season_name = seasonNameDomStr
                        break
                    
        episodes = []
        episodes_data = amazonSoup.find_all(class_='XR0d6P')
        if not episodes_data:
            episodes_data = amazonSoup.find_all(class_='GG33WY')
        if episodes_data:
            episodes = get_episodes_info(episodes_data)
 
        extras = {}
        extras_data = amazonSoup.select('._3g0WlT')
        if not extras_data:
            extras_data = amazonSoup.select('._3QUUKy')
        if not extras_data:
            extras_data = amazonSoup.select('._4fOMiL')
        if extras_data:
            extras = get_extras_info(extras_data)

        bShowMore = False
        total_episodes = 0
        ep_expander = amazonSoup.find_all(attrs={'data-automation-id':'ep-expander'})
        if ep_expander:
            bShowMore = True
            text = ep_expander[0].text.strip()
            match = re.search(r'\d+', text)
            if match:
                total_episodes = int(match.group())

        if amazonSoup.find(class_='_1NNx6V DwgwxH'):
            bShowMore = True

        seasons = {
                "id": pageTitleId,
                "title": big_title,
                "release_time": release_year,
                "season_name":season_name,
                "episodes": episodes,
                "extras": extras,
                "show_more": bShowMore,
                "total_episodes": total_episodes
            }
        
        all_seasons.append(seasons)

    obj = {"seasons": all_seasons}

    return obj

def run(params): 
    arrParams = list(params)
    log_path = ''
    webpages = []   
    for index in range(len(arrParams)):
        if index==0:
            log_path = arrParams[index]
        elif index==1:
            output_file = arrParams[index]
        else:
            strIn = arrParams[index]
            f = open(strIn,'r', encoding='UTF-8')
            webpages.append(f.read())
            f.close()

    # set logging
    log_handler = logging.FileHandler(log_path)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    try:
        with open(output_file,"w",encoding='UTF-8') as f:
            season_info = get_seasons_info(webpages)
            json.dump(season_info,f)
            logger.info("amazon_get_seasons_info complete...")
            
    except Exception as e:
        logger.exception(str(e))

import os
if __name__ == '__main__':

    params = [
        "./amazon/log/python.log",
        "./amazon/result/get_seasons_info.json",
        "./amazon/html/_de/Watch Good Omens - Season 1 _ Prime Video.html",
    ]

    if os.path.exists(params[0]):
        os.remove(params[0])
    if os.path.exists(params[1]):
        os.remove(params[1])

    run(params)