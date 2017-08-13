from sqlalchemy import String, Integer, DateTime, Float, Column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import re
import csv

Base = declarative_base()

engine = create_engine("mysql+mysqlconnector://sergey:3GyNdM9a@linode/music", echo=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

band_links = "./last/band_links.csv"
band_details = "./last/band_details.csv"
album_links = "./last/album_links.csv"
album_details = "./last/album_details.csv"
member_links = "./last/member_links.csv"
similar_bands = "./last/similar_bands.csv"


class Band(Base):
    __tablename__ = 'band'
    id = Column(Integer(), primary_key=True, unique=True)
    name = Column(String(), nullable=False)
    formed_in = Column(Integer())
    disbanded_in = Column(Integer())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    country = Column(String())

    def __init__(self, lines, created_at=None, updated_at=None):
        self.id = UrlParser.extract_band_id(lines[0][0])
        self.name = UrlParser.extract_bandname(lines[0][0])
        self.created_at = created_at
        self.updated_at = updated_at
        for line in lines:
            if line[3] == 'country':
                self.country = line[1]
            if line[3] == 'former_in':
                self.formed_in = line[1]
            if line[3] == 'disbanded_in':
                self.disbanded_in = line[1]

    def __repr__(self):
        return "<Band('{}','{}','{}','{}','{}','{}')>".format(
            self.id, self.name, self.formed_in, self.disbanded_in, self.created_at, self.updated_at)


class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer(), primary_key=True, unique=True)
    band_id = Column(Integer(), ForeignKey("band.id"), unique=True)
    name = Column(String())
    release_at = Column(String())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    style = Column(String())
    cover_url = Column(String())
    type = Column(String())

    # def __init__(self, lines, created_at=None, updated_at=None):
    #     self.id = UrlParser.extract_band_id(lines[0][0])
    #     self.name = UrlParser.extract_bandname(lines[0][0])
    #     self.created_at = created_at
    #     self.updated_at = updated_at
    #     for line in lines:
    #         if line[3] == 'country':
    #             self.country = line[1]
    #         if line[3] == 'former_in':
    #             self.formed_in = line[1]
    #         if line[3] == 'disbanded_in':
    #             self.disbanded_in = line[1]

    # def __repr__(self):
    #     return "<Band('{}','{}','{}','{}','{}','{}')>".format(
    #         self.id, self.name, self.formed_in, self.disbanded_in, self.created_at, self.updated_at)


class UrlParser:
    @staticmethod
    def extract_bandname(url):
        return re.search("(?<=bandname=).+", url).group()

    @staticmethod
    def extract_band_id(url):
        return re.search("(?<=band_id=)\d+", url).group()

    @staticmethod
    def extract_album_id(url):
        return re.search("(?<=album_id=)\d+", url).group()


def parse_bands():
    bands = []
    with open(band_details) as f:
        iterator = csv.reader(f)

        start_line = next(iterator)
        end_line = start_line

        try:
            while True:
                lines = []
                while start_line[0] == end_line[0]:
                    lines.append(end_line)
                    end_line = next(iterator)
                bands.append(Band().build(lines, updated_at=datetime.now()))
                start_line = end_line
        except StopIteration:
            pass

    print(len(bands))
    return bands


session = Session()
for band in parse_bands():
    session.merge(band)
session.commit()
