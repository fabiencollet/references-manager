import os
import requests
import json

import shutil
import sqlite3

try:
    from core import initLog, picturesToGallery
    from color import *
except ImportError:
    from .core import initLog, picturesToGallery
    from .color import *

# Globals
################################################################################

CONFIG_FILEPATH = open('config.json')
CONFIG = json.load(CONFIG_FILEPATH)

TAGS = CONFIG["tags"]
ALLOWED_EXTENSIONS = CONFIG["allowed_extensions"]

UPLOAD_FOLDER = os.sep.join([str(os.getcwd()), "static", "library"])

HTTPS = ["http:", "https"]

log = initLog(__name__)


# Classes
################################################################################

class Database(object):

    def __init__(self, path):
        super(Database, self).__init__()

        self.path = path
        self.file = os.path.split(path)[-1]
        self.name, self.extension = os.path.splitext(self.file)

        self.connection = None
        self.cursor = None

        if not self.exist():

            self.connect()

            self.tab_artist = Table(self, "Artist", True)
            self.tab_media = Table(self, "Media", True)
            self.tab_tag = Table(self, "Tag", True)
            self.tab_media_tag = Table(self, "MediaTag", True)

            self.createEmpty()
            self.initFirstLines()

        else:
            self.connect()
            self.tab_artist = Table(self, "Artist")
            self.tab_media = Table(self, "Media")
            self.tab_tag = Table(self, "Tag")
            self.tab_media_tag = Table(self, "MediaTag")

    def getAllPictures(self):
        pictures = {}
        self.tab_media.listAllValues("Url")
        self.tab_media.listAllValues("MediaArtistId")
        return pictures

    def listAllArtistName(self):
        return self.tab_artist.listAllValues("Name")

    def listAllTag(self):
        return self.tab_tag.listAllValues("Name")

    def downloadFile(self, url):

        response = requests.get(url, stream=True)

        path, file = os.path.split(url)

        file_split = file.rsplit("?")

        if len(file_split) > 1:
            file = file_split[0]

        database_path = os.path.join("/static/library/", file)
        local_path = os.path.join(UPLOAD_FOLDER, file)

        file = open(local_path, 'wb')

        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, file)
        del response

        return [database_path, local_path]

    def addArtist(self, name):
        already_exist = self.tab_artist.valueExist(name, "Name")
        if not already_exist:
            self.tab_artist.insertLine([name])

    def deleteArtist(self, name):
        already_exist = self.tab_artist.valueExist(name, "Name")
        if already_exist:
            artist_id = self.tab_artist.getIdByValue(name, "Name")
            self.tab_artist.deleteLineWhen("Name", name)

            urls = self.tab_media.getValuesWhenOtherIs("Url",
                                                       "MediaArtistId",
                                                       artist_id)

            for url in urls:
                self.updateArtist(url, "Unknown")

    def addTag(self, tag):

        if tag == "":
            return False

        already_exist = self.tab_tag.valueExist(tag, "Name")
        if not already_exist:
            self.tab_tag.insertLine([tag])

    def deleteTag(self, tag):
        already_exist = self.tab_tag.valueExist(tag, "Name")
        if already_exist:
            tag_id = self.tab_tag.getIdByValue(tag, "Name")
            self.tab_tag.deleteLineWhen("Name", tag)

            self.tab_media_tag.deleteLineWhen("MediaTagTagId", tag_id)

    def addTagToMedia(self, url, tag):

        if tag == "":
            return False

        media_index = self.tab_media.getIdByValue(url, "Url")
        tag_exist = self.tab_tag.valueExist(tag, "Name")
        if not tag_exist:
            self.tab_tag.insertLine([tag])

        tag_index = self.tab_tag.getIdByValue(tag, "Name")

        media_tag_exist = False

        list_media = self.tab_media_tag.getValuesWhenOtherIs("MediaTagId",
                                                             "MediaTagMediaId",
                                                             media_index)
        list_tag = self.tab_media_tag.getValuesWhenOtherIs("MediaTagId",
                                                           "MediaTagTagId",
                                                           tag_index)

        for media in list_media:
            if media in list_tag:
                media_tag_exist = True

        if not media_tag_exist:
            self.tab_media_tag.insertLine([media_index, tag_index])

    def removeTagToMedia(self, url, tag):

        media_index = self.tab_media.getIdByValue(url, "Url")
        tag_index = self.tab_tag.getIdByValue(tag, "Name")

        media_ids = self.tab_media_tag.getValuesWhenOtherIs("MediaTagId",
                                                            "MediaTagMediaId",
                                                            media_index)

        tag_ids = self.tab_media_tag.getValuesWhenOtherIs("MediaTagId",
                                                          "MediaTagTagId",
                                                          tag_index)

        for media_id in media_ids:
            if media_id in tag_ids:
                self.tab_media_tag.deleteLineById(media_id)
                return True

        return False

    def addPicture(self, url, save_local=False, artist=""):

        path, file = os.path.split(url)
        file_name, ext = file.rsplit(".", 1)

        local_full_path = os.sep.join([UPLOAD_FOLDER, file])
        local_database_path = os.path.join("/static/library/", file)

        from_internet = False

        if self.tab_media.getIdByValue(local_database_path, "Url"):
            log.warning(f"{url} already in the database")
            return False

        if self.tab_media.getIdByValue(url, "Url"):
            log.warning(f"{url} already in the database")
            return False

        if url[:5] in HTTPS:
            from_internet = True

            # Force to not save Gif in local if url come from internet
            if ext == "gif":
                save_local = False

        if not artist:
            artist_name = "1"
        else:
            index = self.tab_artist.getIdByValue(artist, "Name")
            if index:
                artist_name = str(index)
            else:
                self.tab_artist.insertLine([artist])
                index = self.tab_artist.getIdByValue(artist, "Name")
                artist_name = str(index)

        if from_internet and save_local:
            path, image_path = self.downloadFile(url)

        elif from_internet and not save_local:
            path = url
            image_path = url

        else:
            path = url
            image_path = local_full_path

        # Color
        image_infos = getPictureInformations(image_path)
        hue, sat, value, bright, width_ratio, height_ratio = image_infos

        if path and artist_name:
            self.tab_media.insertLine([path,
                                       hue,
                                       sat,
                                       value,
                                       bright,
                                       width_ratio,
                                       height_ratio,
                                       artist_name])

    def getArtistWithUrl(self, url):

        artist_index = self.tab_media.getValuesWhenOtherIs("MediaArtistId",
                                                           "Url",
                                                           url)

        artist = self.tab_artist.getValueById(artist_index[0], "Name")

        return artist

    def listTagsWithUrl(self, url):

        temp_tags = []

        media_index = self.tab_media.getValuesWhenOtherIs("MediaId",
                                                          "Url",
                                                          url)[0]

        tags_index = self.tab_media_tag.getValuesWhenOtherIs("MediaTagTagId",
                                                             "MediaTagMediaId",
                                                             media_index)

        indexes = list(set(tags_index))

        for index in indexes:
            temp_tags.append(self.tab_tag.getValueById(index, "Name"))

        tags = list(set(temp_tags))

        return tags

    def getTagsWithUrl(self, url):

        tags = self.listTagsWithUrl(url)

        return ",".join(tags)

    def getColorWithUrl(self, url):

        media_index = self.tab_media.getValuesWhenOtherIs("MediaId",
                                                          "Url",
                                                          url)[0]

        hue = self.tab_media.getValueById(media_index, "Hue")
        saturation = self.tab_media.getValueById(media_index, "Saturation")
        value = self.tab_media.getValueById(media_index, "Value")
        brightness = self.tab_media.getValueById(media_index, "Brightness")

        return [hue, saturation, value, brightness]

    def updateArtist(self, url, artist):
        media_index = self.tab_media.getIdByValue(url, "Url")
        artist_index = self.tab_artist.getIdByValue(artist, "Name")

        if not artist_index:
            self.tab_artist.insertLine([artist])
            artist_index = self.tab_artist.getIdByValue(artist, "Name")

        self.tab_media.updateValue(str(media_index),
                                   "MediaArtistId",
                                   str(artist_index))

    def deletePicture(self, url):
        self.tab_media.deleteLineWhen("Url", url)

        media_id = self.tab_media.getIdByValue("Url", url)
        self.tab_media_tag.deleteLineWhen("MediaTagMediaId", media_id)

        if url[:5] in HTTPS:
            return

        path, file = os.path.split(url)
        local_path = os.sep.join([UPLOAD_FOLDER, file])

        if os.path.isfile(local_path):
            os.remove(local_path)

    def fixLocalMedias(self):

        urls = self.tab_media.listAllValues("Url")

        # Create Local Folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)

        for url in urls:

            if url[:5] in HTTPS:
                continue

            path, file = os.path.split(url)
            split_file = file.rsplit(".", 1)

            if len(split_file) < 2:
                self.tab_media.deleteLineWhen("Url", url)
                continue

            filename, ext = split_file

            local_path = os.sep.join([UPLOAD_FOLDER, file])

            if not os.path.isfile(local_path) or ext not in ALLOWED_EXTENSIONS:
                self.tab_media.deleteLineWhen("Url", url)

        for file in os.listdir(UPLOAD_FOLDER):

            database_path = "/".join(["", "static", "library", file])
            local_path = os.sep.join([UPLOAD_FOLDER, file])

            split_file = file.rsplit(".", 1)

            if len(split_file) < 2:
                os.remove(local_path)
                continue

            filename, ext = split_file

            if ext not in ALLOWED_EXTENSIONS:
                os.remove(local_path)
                continue

            if not self.tab_media.valueExist(database_path, "Url"):
                self.addPicture(database_path)

    def exist(self):
        if os.path.exists(self.path):
            log.info(f"{self.path} exist")
            return True
        else:
            log.info(f"{self.path} does not exist")
            return False

    def createEmpty(self):

        # Artist
        self.tab_artist.create()

        self.tab_artist.addColumn("Name", "TEXT", True)

        # Media
        self.tab_media.create()

        self.tab_media.addColumn("Url", "TEXT")
        self.tab_media.addColumn("Hue", "INTEGER")
        self.tab_media.addColumn("Saturation", "REAL")
        self.tab_media.addColumn("Value", "REAL")
        self.tab_media.addColumn("Brightness", "REAL")
        self.tab_media.addColumn("WidthRatio", "REAL")
        self.tab_media.addColumn("HeightRatio", "REAL")
        self.tab_media.addForeignKey("MediaArtistId", self.tab_artist.name)

        # Tag
        self.tab_tag.create()

        self.tab_tag.addColumn("Name", "TEXT", True)

        # MediaTag
        self.tab_media_tag.create()

        self.tab_media_tag.addForeignKey("MediaTagMediaId", self.tab_media.name)
        self.tab_media_tag.addForeignKey("MediaTagTagId", self.tab_tag.name)

        self.commit()

    def initFirstLines(self):

        log.info("Start Init Data")

        self.tab_artist.insertLine(["Unknown"])

        for tag in TAGS:
            self.tab_tag.insertLine([tag])

        log.info("Init Finished")

        self.commit()

    def countAllMedias(self):

        request = "SELECT COUNT(*) FROM Media;"
        count = self.fetchOne(request)[0]

        return count

    def getAllMedias(self, page=0, limit=400):

        urls = []

        start = page * limit
        end = ((page * limit) + limit) - 1

        request = f'SELECT Url FROM Media ORDER BY MediaId DESC ;'
        rows = self.fetchAll(request)

        nb_rows = len(rows)

        for i in range(start, end):
            if i >= nb_rows:
                break
            values = tuple(rows[i])

            urls.append(values[0])

        heights = self.getHeights(urls)
        dict_gallery = picturesToGallery(urls, heights)

        return dict_gallery

    def getMediasByArtist(self, artist):

        index = self.tab_artist.getIdByValue(artist, "Name")

        urls = self.tab_media.getValuesWhenOtherIs("Url",
                                                   "MediaArtistId",
                                                   index)

        heights = self.getHeights(urls)
        dict_gallery = picturesToGallery(urls, heights)

        return dict_gallery

    def getMediasByTag(self, tag):

        urls = []

        index = self.tab_tag.getIdByValue(tag, "Name")

        media_ids = self.tab_media_tag.getValuesWhenOtherIs("MediaTagMediaId",
                                                            "MediaTagTagId",
                                                            index)

        for media_id in media_ids:

            url = self.tab_media.getValuesWhenOtherIs("Url",
                                                      "MediaId",
                                                      media_id)

            if not url:
                self.tab_media_tag.deleteLineWhen("MediaTagMediaId", media_id)
                continue

            urls.append(url[0])

        heights = self.getHeights(urls)
        dict_gallery = picturesToGallery(urls, heights)

        return dict_gallery

    def getMediasByColor(self, hue, saturation, value):

        hue_done = False

        # Hue
        ########################################################################
        if hue == 0:
            list_hue_min = self.tab_media.getValuesWhenOtherIs("Url",
                                                                  "Hue",
                                                                  11)
            
            list_hue_equal = self.tab_media.getValuesWhenOtherIs("Url",
                                                                    "Hue",
                                                                    hue)

            list_hue_plus = self.tab_media.getValuesWhenOtherIs("Url",
                                                                   "Hue",
                                                                   hue + 1)
            hue_done = True

        elif hue == 11:
            list_hue_min = self.tab_media.getValuesWhenOtherIs("Url",
                                                                  "Hue",
                                                                  hue - 1)

            list_hue_equal = self.tab_media.getValuesWhenOtherIs("Url",
                                                                    "Hue",
                                                                    hue)

            list_hue_plus = self.tab_media.getValuesWhenOtherIs("Url",
                                                                   "Hue",
                                                                   0)

            hue_done = True

        else:
            hue_from = hue - 1
            hue_to = hue + 1

        # Saturation
        ########################################################################
        if saturation == 0:
            hue_done = False
            hue_from = 12
            hue_to = 12

            saturation_from = 0
            saturation_to = 0

        elif saturation == 1:
            saturation_from = 0.8
            saturation_to = 1

        else:
            saturation_from = round(saturation - 0.1, 1)
            saturation_to = round(saturation + 0.1, 1)
        # Value
        ########################################################################
        if value == 0:
            value_from = 0
            value_to = 0.2

        elif value == 1:
            value_from = 0.8
            value_to = 1

        else:
            value_from = round(value - 0.1, 1)
            value_to = round(value + 0.1, 1)

        if not hue_done:
            list_hue = self.tab_media.getValuesWhenOtherBetween("Url",
                                                                "Hue",
                                                                hue_from,
                                                                hue_to)

        else:
            set_hue = set(list_hue_min).union(set(list_hue_equal))
            set_hue.update(set(list_hue_plus))
            list_hue = list(set_hue)

        list_sat = self.tab_media.getValuesWhenOtherBetween("Url",
                                                            "Saturation",
                                                            saturation_from,
                                                            saturation_to)
        list_val = self.tab_media.getValuesWhenOtherBetween("Url",
                                                            "Value",
                                                            value_from,
                                                            value_to)

        urls = []

        for url in list_hue:
            if url in list_sat and url in list_val:
                urls.append(url)

        heights = self.getHeights(urls)

        dict_gallery = picturesToGallery(urls, heights)

        return dict_gallery

    def getHeights(self, urls):

        heights = []

        for url in urls:
            height = self.tab_media.getValueByUrl(url, "HeightRatio")
            heights.append(height)

        return heights

    def remove(self):
        if self.exist():
            os.remove(self.path)
            return True
        else:
            return False

    def connect(self):
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        if not self.exist():
            self.createEmpty()
            self.initFirstLines()

    def execute(self, request):
        log.info(request)
        self.cursor.execute(request)
        self.commit()

    def fetchAll(self, request):
        log.info(request)
        self.cursor.execute(request)
        response = self.cursor.fetchall()
        return response

    def fetchOne(self, request):
        log.info(request)
        self.cursor.execute(request)
        response = self.cursor.fetchone()
        return response

    def commit(self):
        self.connection.commit()

    def commitAndClose(self):
        self.connection.commit()
        self.connection.close()


class Table(object):

    def __init__(self, db, name, create=False):
        super(Table, self).__init__()

        self.db = db
        self.db_name = db.name
        self.cursor = db.cursor

        self.name = name
        self.columns = []
        if not create:
            self.initColumns()

    def initColumns(self):
        request = f'''PRAGMA table_info("{self.name}");'''
        table_infos = self.db.fetchAll(request)
        for row in table_infos:
            tuple(row)
            name = row["name"]

            if name != f"{self.name}Id":
                self.columns.append(name)


    def create(self):
        request = f'''CREATE TABLE IF NOT EXISTS "{self.name}" ("{self.name}Id"	
        INTEGER NOT NULL UNIQUE, PRIMARY KEY("{self.name}Id" AUTOINCREMENT));'''

        self.db.execute(request)

    def addColumn(self,
                  name,
                  type="TEXT",
                  not_null=False,
                  default_value="Unknown",
                  unique=False):

        params = []

        if not_null:
            params.append("NOT NULL DEFAULT")
            params.append(default_value)

        if unique:
            params.append("UNIQUE")

        all_params = " ".join(params)

        request = f'''ALTER TABLE "{self.name}" 
        ADD COLUMN "{name}" {type} {all_params};'''

        if request:
            self.columns.append(name)
            self.db.execute(request)

    def addForeignKey(self, name, table_link):

        request = f'''ALTER TABLE "{self.name}" ADD COLUMN 
        "{name}" INTEGER REFERENCES {table_link}({table_link}Id);'''

        self.columns.append(name)

        self.db.execute(request)

    def insertLine(self, values):

        join_values = ""
        join_columns = ""

        len_values = len(values)
        len_columns = len(self.columns)

        if len_values > 1:
            for i in range(len_values):
                if i == len_values - 1:
                    join_values += f'"{str(values[i])}"'
                else:
                    join_values += f'"{str(values[i])}", '
        else:
            join_values = f'"{str(values[0])}"'

        if len_columns > 1:
            for i in range(len_columns):
                if i == len_columns - 1:
                    join_columns += f'"{str(self.columns[i])}"'
                else:
                    join_columns += f'"{str(self.columns[i])}", '
        else:
            join_columns = f'"{self.columns[0]}"'

        request = f'''INSERT INTO {self.name} ({join_columns}) 
        VALUES ({join_values});'''

        self.db.execute(request)

    def insertMultiLine(self, lines):

        for values in lines:
            self.insertLine(values)

    def deleteLineWhen(self, column, value):
        request = f'DELETE FROM {self.name} WHERE "{column}" == "{value}";'

        self.db.execute(request)

    def deleteLineById(self, index):
        request = f'DELETE FROM {self.name} WHERE "{self.name}Id" == "{index}";'

        self.db.execute(request)

    def listAllValues(self, column):

        list_values = []

        if not column in self.columns:
            log.error(f"{column} does not exist in the table {self.name}")
            return list_values

        request = f'SELECT {column} FROM {self.name};'

        rows = self.db.fetchAll(request)

        for row in rows:
            values = tuple(row)
            list_values.append(values[0])

        return list_values

    def getValuesWhenOtherIs(self, column_return_value, column, value_equal):
        list_values = []

        request = f'''SELECT "{column_return_value}" FROM {self.name} 
        WHERE "{column}" == "{value_equal}";'''

        values = self.db.fetchAll(request)
        if values:
            for value in values:
                tuple(value)
                list_values.append(value[column_return_value])

        return list_values

    def getValuesWhenOtherBetween(self,
                                  column_return_value,
                                  column,
                                  value_from,
                                  value_to):
        list_values = []

        request = f'''SELECT "{column_return_value}" FROM {self.name} WHERE 
        "{column}" BETWEEN "{value_from}" AND "{value_to}";'''

        values = self.db.fetchAll(request)
        if values:
            for value in values:
                tuple(value)
                list_values.append(value[column_return_value])

        return list_values

    def updateValue(self, index, column, value):

        request = f'''UPDATE {self.name} SET {column} = {value} 
        WHERE "{self.name}Id" == "{index}";'''

        self.db.execute(request)

    def valueExist(self, value, column):

        request = f'SELECT * FROM {self.name} WHERE "{column}" == "{value}";'

        values = self.db.fetchAll(request)
        if values:
            return True
        else:
            return False

    def getValueById(self, index, column):

        request = f'''SELECT "{column}" FROM {self.name} 
        WHERE "{self.name}Id" == "{index}";'''

        value = self.db.fetchOne(request)
        if value:
            tuple(value)
            return value[column]
        else:
            return False

    def getValueByUrl(self, url, column):

        request = f'SELECT "{column}" FROM {self.name} WHERE "Url" == "{url}";'

        value = self.db.fetchOne(request)
        if value:
            tuple(value)
            return value[column]
        else:
            return False

    def getIdByValue(self, value, column):

        request = f'''SELECT "{self.name}Id" FROM {self.name} 
        WHERE "{column}" == "{value}";'''

        value = self.db.fetchOne(request)
        if value:
            tuple(value)
            return value[f"{self.name}Id"]
        else:
            return False

    def lineExist(self, values):

        join_values = ""
        join_columns = ""

        len_values = len(values)
        len_columns = len(self.columns)

        if len_values > 1:
            for i in range(len_values):
                if i == len_values - 1:
                    join_values += f'"{str(values[i])}"'
                else:
                    join_values += f'"{str(values[i])}", '
        else:
            join_values = f'"{str(values[0])}"'

        if len_columns > 1:
            for i in range(len_columns):
                if i == len_columns - 1:
                    join_columns += f'"{str(self.columns[i])}"'
                else:
                    join_columns += f'"{str(self.columns[i])}", '
        else:
            join_columns = f'"{self.columns[0]}"'

        request = f'''SELECT ({join_columns}) FROM {self.name} 
        WHERE ({join_columns}) == ({join_values});'''

        rows = self.db.fetchAll(request)

        if rows:
            return True
        else:
            return False
