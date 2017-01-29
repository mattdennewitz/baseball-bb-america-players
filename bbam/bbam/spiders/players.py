# -*- coding: utf-8 -*-
import re
import urllib

from dateutil import parser as date_parser

import scrapy

from ..items import PlayerLoader, Player
from .const import POSITIONS


class PlayersSpider(scrapy.Spider):
    name = 'players'
    allowed_domains = ['baseballamerica.com']

    def __init__(self):
        super(PlayersSpider, self).__init__()

        # this spider maintains an index of who it has already visisted
        # in order to prevent duplicates and reduce network chatter
        self.obvs = set()

        # visit each position
        self.start_urls = (
            'http://www.baseballamerica.com/statistics/players/search/?pos=' + pos
            for pos
            in POSITIONS
        )

    def parse(self, response):
        links = response.xpath("""
          //a[contains(@href, "/statistics/players/cards/")]/parent::td/parent::tr
        """)

        for link in links:
            # set baseball america player id from card url
            player_card_url = link.xpath('./td[1]/a/@href').extract_first()
            player_id = int(player_card_url.split('/')[-1])

            if player_id in self.obvs:
                # ignore players we've already visited
                continue

            loader = PlayerLoader(item=Player(), response=response)
            loader.add_value('bbam_id', player_id)

            # set full name
            full_name = link.xpath('./td[1]/a/text()').extract_first()
            loader.add_value('full_name', full_name)

            # set position
            position = link.xpath('./td[2]/text()').extract_first()
            loader.add_value('position', position)

            # set full team name
            full_team_name = link.xpath('./td[3]/text()').extract_first()
            if full_team_name == 'No Affiliation':
                full_team_name = None
            loader.add_value('full_team_name', full_team_name)

            player = loader.load_item()

            # request player detail, send result to ``parse_player``
            next_req = scrapy.Request(
                urllib.parse.urljoin('http://' + self.allowed_domains[0],
                                     player_card_url),
                callback=self.parse_player
            )
            next_req.meta['player'] = player
            yield next_req

            # indicate that we have seen this player
            self.obvs.add(player_id)

    def parse_player(self, response):
        """Extracts player vitals from card page
        """

        player = response.meta['player']
        loader = PlayerLoader(item=player, response=response)

        # set "bats"
        loader.add_xpath(
            'bats',
            '//strong[contains(., "Bats:")]/following-sibling::text()'
        )

        # set "throws"
        loader.add_xpath(
            'throws',
            '//strong[contains(., "Throws:")]/following-sibling::text()'
        )

        # set high school
        loader.add_xpath(
            'high_school',
            '//strong[contains(., "High School:")]/following-sibling::text()'
        )

        # set college
        loader.add_xpath(
            'college',
            '//strong[contains(., "College:")]/following-sibling::text()'
        )

        # set height, converted to inches
        ht = response.xpath(
            '//strong[contains(., "Ht.:")]/following-sibling::text()'
        ).extract_first()
        if ht:
            ht = ht.strip()
            try:
                ft, in_ = map(int, ht.split('-'))
                ft *= 12 # convert to inches
                loader.add_value('height', ft + in_)
            except ValueError as exc:
                self.logger.warning('Could not parse height for {}'
                                    .format(player['bbam_id']))

        # extract birth date, convert to YYYY-MM-DD format
        birth_date_line = response.xpath(
            '//strong[contains(., "Born:")]/following-sibling::text()'
        ).extract_first()
        if ' in ' in birth_date_line:
            birth_date_line = birth_date_line.split(' in ')[0]
        if birth_date_line:
            try:
                birth_date = date_parser.parse(birth_date_line)
                birth_date = birth_date.strftime('%Y-%m-%d')
            except ValueError as exc:
                self.logger.warning('Could not parse birth date for {}'
                                    .format(player['bbam_id']))
                birth_date = None

            loader.add_value('birth_date', birth_date)

        enhanced_player = loader.load_item()
        yield enhanced_player
