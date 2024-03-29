#!/usr/bin/env python


import re, sys, string
import bs4

webpage = '''
<html><head><title>The Website Title</title></head>
<body>
<p>Download my <strong>Python</strong> book from <a href="http://inventwithpython.com">my website</a>.</p>
<p class="slogan">Learn Python the easy way!</p>
<p>By <span id="author">Al Sweigart</span></p>
</body></html>
'''

def createSrt_vtt():
    exampleSoup = bs4.BeautifulSoup(webpage,'html5lib')
    elems = exampleSoup.select('#author')
    type(elems)
    # print (elems[0].getText())
    # print(webpage)