# -*- coding: utf-8 -*-
"""
Scraping YouTube Videoes for Set of Metadata
"""

# TODO: Determine all URL types
# TODO: Determine why 'schema.org'?

import pandas as pd

import csv
import requests
import sys

from bs4 import BeautifulSoup

RELEVANT_METADATA = ['ownerChannelName',
                     'title',
                     'viewCount',
                     'uploadDate',
                     'approxDurationMs'
                     ]


class YouTubeScraper:
    YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
    
    @classmethod
    def video_code(self, youtube_url): # shorten URL only
        return youtube_url[youtube_url.rindex('/')+1:]
    
    
    @classmethod
    def lengthen_url(self, youtube_url):
        return self.YOUTUBE_VIDEO_PREFIX + self.video_code(youtube_url)
    
    
    @classmethod
    def find_metadata_variable_value(self, soup, metadata_variable_to_find, alt=False):
        variable_identifier_string = '{}\\":\\"'.format(metadata_variable_to_find)
        variable_identifier_offset = len(variable_identifier_string)
        
        if alt:
            relevant_html_str = soup.find_all('script')[12].text
        else:
            relevant_html_str = soup.find_all('script')[13].text
        
        variable_start_index = relevant_html_str.rfind(variable_identifier_string) + \
                               variable_identifier_offset
            
        relevant_html_str_cut = relevant_html_str[variable_start_index:]
        
        variable_end_index = relevant_html_str_cut.find('\\"')
        variable_value = relevant_html_str_cut[:variable_end_index]
        
        return variable_value
    
    
def null_row_values(url):
    return {'URL': url, 
            'Title': 'N/A', 
            'Creator': 'N/A', 
            'View Count': 'N/A', 
            'Upload Date': 'N/A',
            'Video Length (MS)': 'N/A',
            'Video Length (minutes)': 'N/A'}

    
if __name__ == "__main__":
    urls_to_scrape = pd.read_excel('youtube_url.xlsx').video_url
    
    with open('youtube_videos_metadata.csv', mode='w') as csv_file:
        field_names = ['URL', 'Title', 'Creator', 'View Count', 'Upload Date',
                       'Video Length (MS)', 'Video Length (minutes)']
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
    
        for url in urls_to_scrape:
            if 'youtu' in url:
                if '-' not in url: # If URL is shortened form
                    url = YouTubeScraper.lengthen_url(url)
                elif '&' in url:
                    ampersand_index = url.find('&')
                    url = url[:ampersand_index]
                    
                response = requests.get(url, headers={ 'User-Agent': 'Mozilla/5.0' })
                soup = BeautifulSoup(response.text, features="html.parser")
                metadata_values = {}
                is_alt = False
                
                for var in RELEVANT_METADATA:
                    metadata_values[var] = YouTubeScraper.find_metadata_variable_value(soup, var, is_alt)
                    if (('https://schema.org' in metadata_values[var]) or \
                       ('http://schema.org'  in metadata_values[var])):
                        is_alt = True
                        metadata_values[var] = YouTubeScraper.find_metadata_variable_value(soup, var, is_alt)
                    
                if (not metadata_values['viewCount']) or \
                   ('window' in metadata_values['viewCount']): # check if video is removed
                    row_values = null_row_values(url)
                else:
                    try:
                        video_length_minutes = float(metadata_values['approxDurationMs']) * 1.66666666e-5
                        
                        row_values = {'URL': url, 'Title': metadata_values['title'], 
                            'Creator': metadata_values['ownerChannelName'], 
                            'View Count': metadata_values['viewCount'], 
                            'Upload Date': metadata_values['uploadDate'],
                            'Video Length (MS)': metadata_values['approxDurationMs'], 
                            'Video Length (minutes)': str(video_length_minutes)}
                    except:
                        e = sys.exc_info()[0]
                        print( "Error: {}".format(e))
                        print(url)
                        print(metadata_values)
                        
                        row_values = null_row_values(url)
            else: # not a youtube URL
                row_values = null_row_values(url)

            writer.writerow(row_values)

# title = find_title(page)

# 1.5 hr
# 5:40