#!/usr/bin/env python

import re, sys, string
import bs4,json

import logging
logger = logging.getLogger()

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

        amazonSoup = bs4.BeautifulSoup(webpage,'html5lib')
        #<main id="main" data-testid="detailpage-main"></main>

        is_meta = False
        media_type = 'movie'
        
        main_element = amazonSoup.find('main',attrs={'id':'main','data-testid':'detailpage-main'})
        if main_element is not None:
            e_synopsis = main_element.select('._1wxob_')
            if len(e_synopsis)==0:
                e_synopsis = main_element.select('._3qsVvm')
            
            if len(e_synopsis)==0:
                e_synopsis = main_element.select('._5tB6mN')

            e_thumb = main_element.select('#atf-full')
            if len(e_thumb)==0:
                e_thumb = main_element.select('.om7nme')
                
            if len(e_synopsis)==0 and len(e_thumb)==0:
                is_meta = False
            else:
                is_meta = True

            #[show, movie, is_live, has_live, upcoming]
            e_live = amazonSoup.find_all(attrs={'data-automation-id':'live-state-badge'})
            if len(e_live) > 0:
                str = e_live[0].string
                if str == 'LIVE':
                    media_type = 'is_live'
                elif str == 'UPCOMING':
                    media_type = 'upcoming'
                else:
                    media_type = 'has_live'
            else:
                e_episodes = amazonSoup.find_all(class_='XR0d6P')
                if not e_episodes:
                    e_episodes = amazonSoup.find_all(class_='GG33WY')
                if len(e_episodes) > 0:
                    media_type = 'show'
                else:
                    media_type = 'movie'

        dict = {
            'is_meta':is_meta,
            'media_type':media_type
        }

        with open(output_file,"w", encoding='UTF-8') as f:
            json.dump(dict,f)
            logging.info("amazon_is_meta complete...")
                
    except Exception as e:
        logger.exception(str(e))

import os
if __name__ == '__main__':

    params = [
        "./log/python.log",
        "./result/is_meta.json",
        "./html/Live/live_Amazon.com_ Wu-Tang Clan & Nas_ NY State of Mind Tour at Climate Pledge Arena _ Movies & TV.html",
        #"./html/Watch Meg 2_ The Trench _ Prime Video.html",
    ]

    if os.path.exists(params[0]):
        os.remove(params[0])
    if os.path.exists(params[1]):
        os.remove(params[1])

    run(params)