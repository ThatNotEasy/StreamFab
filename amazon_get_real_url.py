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
        expander = amazonSoup.find_all(attrs={'data-automation-id':'ep-expander'})
        if len(expander)==0:
            real_url = ""
        else:
            real_url = expander[0]['href']
        dict = {
            "real_url":real_url
        }
        with open(output_file,"w", encoding='UTF-8') as f:
            json.dump(dict,f)
            logger.info("get_real_url complete...")

    except Exception as e:
        logger.exception(str(e))

import os
if __name__ == '__main__':

    params = [
        "./log/python.log",
        "./result/get_real_url.json",
        "./html/season_1.html",
    ]

    if os.path.exists(params[0]):
        os.remove(params[0])
    if os.path.exists(params[1]):
        os.remove(params[1])

    run(params)