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
        elems = amazonSoup.select('.dv-node-dp-seasons a')
        season_urls = []
        for elem in elems:
            href = elem['href']
            season_urls.append(href)
        dict = {
            "season_urls":season_urls
        }

        if season_urls is None or len(season_urls)==0:
            logger.warning("No season urls found '.dv-node-dp-seasons a' - trying '.dv-node-dp-seasons-default'...")
            elems = amazonSoup.select('.dv-node-dp-seasons-default a')
            season_urls = []
            # 递归查找所有元素中的 herf
            for elem in elems:
                href = elem['href']
                season_urls.append(href)
            dict = {
                "season_urls":season_urls
            }



        with open(output_file,"w", encoding='UTF-8') as f:
            json.dump(dict,f)
            logger.info("amazon_get_season_urls complete...")

    except Exception as e:
        logger.exception(str(e))

import os
if __name__ == '__main__':

    params = [
        "./amazon/log/python.log",
        "./amazon/result/get_season_urls.json",
        "./amazon/html/_de/Watch Good Omens - Season 1 _ Prime Video.html",
    ]

    if os.path.exists(params[0]):
        os.remove(params[0])
    if os.path.exists(params[1]):
        os.remove(params[1])

    run(params)