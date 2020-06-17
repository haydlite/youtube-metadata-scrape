# -*- coding: utf-8 -*-
"""
Scraping YouTube Videoes for Set of Metadata
"""

# TODO: Sometimes URLs differ in format

# TODO: Title CHECK
# TODO: Creator CHECK
# TODO: Views as of Date
# TODO: Date Uploaded
# TODO: Video Length

# TODO: Test
    

import pandas as pd
import requests
from bs4 import BeautifulSoup

YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
wdir = '/Users/hle/projects/youtube-metadata-scrape/'


def video_code(youtube_url): # shorten URL only
    return youtube_url[youtube_url.rindex('/')+1:]


def lengthen_url(youtube_url):
    return YOUTUBE_VIDEO_PREFIX + video_code(youtube_url)


def find_metadata_variable_value(soup, metadata_variable_to_find):
    variable_identifier_string = '{}\\":\\"'.format(metadata_variable_to_find)
    variable_start_index = soup.find_all('script')[13].text.\
        rfind('{}\\":\\"'.format(metadata_variable_to_find)) 
        + len('{}\\":\\"'.format(metadata_variable_to_find))
        
    metadata_string = soup.find_all('script')[13].text
    metadata_string_cut = metadata_string[variable_start_index:]
    
    variable_end_index = metadata_string_cut.find('\\"')
    variable_value = metadataStringCut[:variable_end_index]
    
    return variable_value

     

def find_title(soup):
    title_StartIndex = soup.find_all('script')[13].text.rfind('viewCount\\":\\"') + len('viewCount\\":\\"')
    metadataString = soup.find_all('script')[13].text
    metadataStringCut = metadataString[title_StartIndex:]
    title_EndIndex = metadataStringCut.find('\\"')
    title = metadataStringCut[:title_EndIndex]
    return title


def find_creator(soup):
    ownerChannelName_StartIndex = soup.find_all('script')[13].text.rfind('ownerChannelName\\":\\"') + len('ownerChannelName\\":\\"')
    metadataString = soup.find_all('script')[13].text
    metadataStringCut = metadataString[ownerChannelName_StartIndex:]
    ownerChannelName_EndIndex = metadataStringCut.find('\\"')
    ownerChannelName = metadataStringCut[:ownerChannelName_EndIndex]
    return ownerChannelName

def find_view_count(soup):
    viewCount_StartIndex = soup.find_all('script')[13].text.rfind('viewCount\\":\\"') + len('viewCount\\":\\"')
    metadataString = soup.find_all('script')[13].text
    metadataStringCut = metadataString[viewCount_StartIndex:]
    viewCount_EndIndex = metadataStringCut.find('\\"')
    viewCount = metadataStringCut[:viewCount_EndIndex]
    return viewCount


df = pd.read_excel('youtube_url.xlsx')
url = df.video_url[50]
if url.rfind('=') == -1: # If URL is shorten form
    url = lengthen_url(url)

response = requests.get(url, headers={ 'User-Agent': 'Mozilla/5.0' })

soup = BeautifulSoup(response.text, features="html.parser")
creator = find_creator(soup)
title = find_title(soup)




 
with open(wdir + '{}.txt'.format(url[url.rfind('=')+1:]), 'w+', encoding='utf-8') as f_out:
    f_out.write(soup.prettify())
    



# title = find_title(page)

# 1.5 hr
# 5:40