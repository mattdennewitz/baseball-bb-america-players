# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


def parse_int(value):
    return int(value)


def clean_text(value):
    return value.strip()


class PlayerLoader(ItemLoader):
    """Base Player loader
    """
    default_input_processor = MapCompose(clean_text)
    default_output_processor = TakeFirst()


class Player(scrapy.Item):
    """Schematics for a single player's profile
    """
    bbam_id = scrapy.Field(input_processor=MapCompose(parse_int))
    full_name = scrapy.Field()
    proper_name = scrapy.Field()
    full_team_name = scrapy.Field()
    position = scrapy.Field()
    birth_date = scrapy.Field()
    bats = scrapy.Field()
    throws = scrapy.Field()
    height = scrapy.Field(input_processor=MapCompose(parse_int))
    high_school = scrapy.Field()
    college = scrapy.Field()
