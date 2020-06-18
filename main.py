# -*- coding: utf-8 -*-
"""Scraping YouTube Videoes for Set of Metadata."""

# TODO: Determine all URL types
# TODO: Determine why 'schema.org'?

# TODO: Check out all the NAs

import csv
import requests
import sys

import pandas as pd
from bs4 import BeautifulSoup

RELEVANT_METADATA = ['ownerChannelName',
                     'title',
                     'viewCount',
                     'uploadDate',
                     'approxDurationMs'
                     ]


class YouTubeScraper:
    """Class with YouTube scraping methods and helper methods."""

    YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='

    @classmethod
    def standardize_URL(self, youtube_url):
        """Return YouTube URL in standard form."""
        if '?v=' in youtube_url:
            video_code_index = youtube_url.find('?v=') + 3
            if '&' in youtube_url[video_code_index:]:
                video_code_index_end = youtube_url.find('&')
                video_code = youtube_url[video_code_index:video_code_index_end]
            else:
                video_code = youtube_url[video_code_index:]
        else:
            video_code = youtube_url[youtube_url.rindex('/')+1:]
        return self.YOUTUBE_VIDEO_PREFIX + video_code

    @classmethod
    def find_metadata_variable_value(self, soup, metadata_variable_to_find):
        """Pass finds metadata variable on YouTube video's page."""
        variable_identifier_string = '{}\\":\\"'.\
                                     format(metadata_variable_to_find)
        variable_identifier_offset = len(variable_identifier_string)
        
        potential_metadata_blob_1 = soup.find_all('script')[13].text
        potential_metadata_blob_2 = soup.find_all('script')[12].text

        if ("http://schema.org" in potential_metadata_blob_1) or \
            ("https://schema.org" in potential_metadata_blob_1):
            relevant_html_str = potential_metadata_blob_2
        else:
            relevant_html_str = potential_metadata_blob_1

        variable_start_index = relevant_html_str.\
                               find(variable_identifier_string) + \
                               variable_identifier_offset

        relevant_html_str_cut = relevant_html_str[variable_start_index:]

        variable_end_index = relevant_html_str_cut.find('\\",\\"')
        variable_value = relevant_html_str_cut[:variable_end_index]

        return variable_value


def null_row_values(url):
    """Return nulled row values."""
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
                url = YouTubeScraper.standardize_URL(url)
                response = requests.get(url,
                                        headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.text, features="html.parser")
                metadata_values = {}

                for var in RELEVANT_METADATA:
                    metadata_values[var] = YouTubeScraper.\
                        find_metadata_variable_value(soup, var)

                if (not metadata_values['viewCount']) or \
                   ('window' in metadata_values['viewCount']):
                    # check if video is removed
                    row_values = null_row_values(url)
                else:
                    try:
                        video_length_minutes = float(
                            metadata_values['approxDurationMs']) \
                            * 1.66666666e-5
                        row_values = {'URL': url,
                                      'Title': metadata_values['title'],
                                      'Creator': metadata_values['ownerChannelName'],
                                      'View Count': metadata_values['viewCount'],
                                      'Upload Date': metadata_values['uploadDate'],
                                      'Video Length (MS)': metadata_values['approxDurationMs'],
                                      'Video Length (minutes)': str(video_length_minutes)}
                    except:
                        e = sys.exc_info()[0]
                        print("Error: {}".format(e))
                        print(url)
                        print(metadata_values)

                        row_values = null_row_values(url)
            else:  # not a youtube URL
                row_values = null_row_values(url)

            writer.writerow(row_values)

# title = find_title(page)

# 1.5 hr
# 5:40 -  9:10 4hr - 11