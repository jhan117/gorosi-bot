import requests
import discord
from bs4 import BeautifulSoup

from common_func import *

# 고시 채널
gosi_channel = 961515641699979285


class GetPost:
    def __init__(self):
        self.text = []
        self.date = []

        self.soup = BeautifulSoup(requests.get(gosi_url).text, "lxml")

        self.list_all = self.soup.select("#tab-content1 > li")
        self.list_7 = self.soup.select("#tab-content3 > li")

    def notice(self):
        for item in self.list_all:
            if item.select_one(".notice_icon"):
                self.text.append(item.a.text)
                self.date.append(item.select_one("span.date").text)

        return dict(zip(self.text, self.date))

    def new(self):
        for item in self.list_all:
            if item.select_one("img"):
                self.text.append(item.a.text)
                self.date.append(item.select_one("span.date").text)

        return dict(zip(self.text, self.date))

    def grade_7(self):
        for item in self.list_7:
            self.text.append(item.a.text)
            self.date.append(item.select_one("span.date").text)

        return dict(zip(self.text, self.date))


# 게시글 임베드
def make_gosi_embed(post_dict):
    embed = discord.Embed(
        title='사이버국가고시센터', url=gosi_url, color=0xFF0000)

    for key, value in post_dict.items():
        embed.add_field(name=key, value=value, inline=False)

    return embed
