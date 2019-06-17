#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# https://developers.google.com/youtube/v3/code_samples/python?hl=ko
# https://developers.google.com/youtube/v3/docs/search/list?hl=ko
# https://console.cloud.google.com/apis/api/youtube.googleapis.com/credentials?project=cobalt-chalice-215602

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = os.environ.get('YOUTUBE_SEARCH_KEY')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(options, minus_day):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    now = datetime.now()
    if minus_day == 30:
        publishedAfter = "%04d-%02d-%02dT00:00:00Z" % (now.year, now.month - 1, now.day)
    else:
        publishedAfter = "%04d-%02d-%02dT00:00:00Z" % (now.year, now.month, now.day - minus_day)
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        part="id,snippet",
        order=options.order,
        publishedAfter=publishedAfter,
        type="video",
        maxResults=options.max_results
    ).execute()

    videos = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        # print(search_result)
        if search_result["id"]["kind"] == "youtube#video":
            publishedAt = search_result["snippet"]["publishedAt"]
            msg = "* %s\nhttps://www.youtube.com/watch?v=%s\n(%s)" % (
                  search_result["snippet"]["title"].replace("&amp;", "&").replace("&quot;", '"'),
                  search_result["id"]["videoId"],
                  publishedAt.replace('T', ' ')[:-5])
        videos.append(msg)

    if minus_day == 30:
        today = "%02d/%02d ~ %02d/%02d" % (now.month - 1, now.day, now.month, now.day)
    else:
        today = "%02d/%02d ~ %02d/%02d" % (now.month, now.day - minus_day, now.month, now.day)
    if minus_day == 1:
        print "[Daily] 조회수 기준 상위 5개\n", today
        print "\n".join(videos)
    elif minus_day == 7:
        print "[Weekly] 조회수 기준 상위 5개\n", today
        print "\n".join(videos)
    elif minus_day == 30:
        print "[Monthly] 조회수 기준 상위 5개\n", today
        print "\n".join(videos)


def main():
    print "[ Beta Youtube 링크 모음 ]"
    argparser.add_argument("--q", help="Search term", default="부동산")
    argparser.add_argument("--max-results", help="Max results", default=5)
    argparser.add_argument("--order", help="order type", default="viewCount")
    # "[u'date', u'rating', u'relevance', u'title', u'videoCount', u'viewCount']"
    args = argparser.parse_args()

    youtube_search(args, 1)
    print('\n\n')
    youtube_search(args, 7)
    print('\n\n')
    youtube_search(args, 30)

    # try:
    #     youtube_search(args, 1)
    # except HttpError, e:
    #     print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


if __name__ == "__main__":
    main()

