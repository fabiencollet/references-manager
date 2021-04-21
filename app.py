import os
import sys
import subprocess
import threading

from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from werkzeug import exceptions

try:
    from core import *
    from database import *
    from color import dict_hue
except ImportError:
    from .core import *
    from .database import *
    from .color import dict_hue

# Globals
################################################################################

log = initLog(__name__)
app = Flask(__name__)

CONFIG_FILEPATH = open('config.json')
CONFIG = json.load(CONFIG_FILEPATH)

UPLOAD_FOLDER = os.sep.join([str(os.getcwd()), "static", "library"])

ALLOWED_EXTENSIONS = CONFIG["allowed_extensions"]

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Init
################################################################################

db = Database(CONFIG["database"])


# Classes
################################################################################

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Reference Manager")
        self.resize(1280, 800)

        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.web_widget = QWebEngineView()
        self.web_widget.load(QUrl("http://127.0.0.1:5000/"))

        self.setCentralWidget(self.web_widget)


# Functions
################################################################################

def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def buildCommands(url):
    commands = {}

    if url[:5] not in HTTPS:

        filepath = os.sep.join([str(os.getcwd()), url])

        for software in CONFIG["software"]:
            software_path = CONFIG["software"][software]
            commands[software] = f'"{software_path}" {filepath}'

    return commands

# Routes
################################################################################


@app.route('/', methods=['GET'])
def index():

    page = 0
    db = Database(CONFIG["database"])
    db.fixLocalMedias()

    nb_medias = db.countAllMedias()
    nb_pages = math.ceil(nb_medias / 50)

    if nb_pages > 0:
        last_page = nb_pages - 1
    else:
        last_page = 0

    if request.method == 'GET':
        data = request.args
        if "page" in data:
            page = int(data["page"])
        if "delete" in data:
            delete_url = data["delete"]
            db.deletePicture(delete_url)

    list_pages = [0]
    range_page = 3

    for i in range(range_page):
        if page - (range_page - i) > 0:
            list_pages.append(page - (range_page - i))

    if page > 0:
        list_pages.append(page)

    for i in range(1, range_page + 1):
        if (page + i) < last_page:
            list_pages.append(page + i)

    if last_page not in list_pages:
        list_pages.append(last_page)

    pictures = db.getAllMedias(page, 50)

    return render_template("index.html",
                           pictures=pictures,
                           current_page=page,
                           list_pages=list_pages,
                           width_buttons=len(list_pages)*50)


@app.route('/add_medias')
def add_medias():
    db = Database(CONFIG["database"])
    artists = db.listAllArtistName()
    return render_template("add_medias.html", artists=artists)


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        name = request.form["nm"]
        file_type = request.form["file_type"]

        return render_template("search.html",
                               name=name,
                               file_type=file_type
                               )


@app.route('/artist/<current_artist>', methods=['GET'])
def artist_page(current_artist):

    db = Database(CONFIG["database"])

    if request.method == 'GET':
        data = request.args
        if "delete" in data:
            delete_url = data["delete"]
            db.deletePicture(delete_url)

    pictures = db.getMediasByArtist(current_artist)

    artists = db.listAllArtistName()

    return render_template("artist.html",
                           pictures=pictures,
                           current_artist=current_artist,
                           artists=sorted(artists))


@app.route('/artist')
def artist():

    current_artist = "Unknown"

    db = Database(CONFIG["database"])
    pictures = db.getMediasByArtist(current_artist)

    artists = db.listAllArtistName()

    return render_template("artist.html",
                           pictures=pictures,
                           current_artist=current_artist,
                           artists=sorted(artists))


@app.route('/edit_artist', methods=['POST'])
def edit_artist():
    if request.method == 'POST':

        current_artist = request.form["artist"]

        db = Database(CONFIG["database"])
        pictures = db.getMediasByArtist(current_artist)

        artists = db.listAllArtistName()

        return render_template("artist.html",
                               pictures=pictures,
                               current_artist=current_artist,
                               artists=sorted(artists))


@app.route('/add_new_artist', methods=['POST'])
def add_new_artist():
    if request.method == 'POST':
        current_artist = request.form["artist"]

        db = Database(CONFIG["database"])

        db.addArtist(current_artist)

        artists = db.listAllArtistName()

        return render_template("artist.html",
                               current_artist=current_artist,
                               artists=sorted(artists))


@app.route('/tag/<current_tag>', methods=['GET'])
def tag_page(current_tag):

    db = Database(CONFIG["database"])

    if request.method == 'GET':
        data = request.args
        if "delete" in data:
            delete_url = data["delete"]
            db.deletePicture(delete_url)

    pictures = db.getMediasByTag(current_tag)

    tags = []
    temp_tags = db.listAllTag()

    for tag in temp_tags:
        if artist != current_tag:
            tags.append(tag)

    return render_template("tag.html",
                           pictures=pictures,
                           current_tag=current_tag,
                           tags=sorted(tags))


@app.route('/tag', methods=['GET'])
def tag():

    current_tag = ""

    db = Database(CONFIG["database"])

    if request.method == 'GET':
        data = request.args
        if 'deleteTag' in data:
            delete_tag = data['deleteTag']
            db.deleteTag(delete_tag)

    pictures = db.getMediasByTag(current_tag)

    tags = []
    temp_tags = db.listAllTag()

    for tag in temp_tags:
        if artist != current_tag:
            tags.append(tag)

    return render_template("tag.html",
                           pictures=pictures,
                           current_tag=current_tag,
                           tags=sorted(tags))


@app.route('/add_new_tag', methods=['POST'])
def add_new_tag():
    if request.method == 'POST':
        current_tag = request.form["tag"]

        db = Database(CONFIG["database"])

        db.addTag(current_tag)

        pictures = db.getMediasByTag(current_tag)

        tags = []
        temp_tags = db.listAllTag()

        for tag in temp_tags:
            if artist != current_tag:
                tags.append(tag)

        return render_template("tag.html",
                               pictures=pictures,
                               current_tag=current_tag,
                               tags=sorted(tags))


# COLOR
################################################################################

@app.route('/color', methods=['GET', 'POST'])
def color():

    hue, sat, value = (6, 0.5, 0.5)

    db = Database(CONFIG["database"])

    if request.method == 'GET':
        data = request.args
        if "hue" in data:
            hue = data["hue"]
        if "sat" in data:
            sat = data["sat"]
        if "val" in data:
            value = data["val"]
        if "delete" in data:
            delete_url = data["delete"]
            db.deletePicture(delete_url)

    if request.method == 'POST':
        hue = request.form["hue"]
        sat = request.form["saturation"]
        value = request.form["value"]

    pictures = db.getMediasByColor(int(hue), float(sat), float(value))

    return render_template("color.html",
                           pictures=pictures,
                           hue=hue,
                           saturation=sat,
                           value=value,
                           dict_hue=dict_hue)


# SETTINGS
################################################################################
@app.route('/fix_database', methods=['POST'])
def fix_database():

    db = Database(CONFIG["database"])

    db.fixLocalMedias()

    artists = db.listAllArtistName()

    return render_template("add_medias.html",
                           info=f"Database Fixed",
                           artists=artists)


@app.route('/add_local_picture', methods=['POST'])
def add_local_picture():

    db = Database(CONFIG["database"])
    artists = db.listAllArtistName()

    if request.method == 'POST':
        local_path = ""
        url = request.files["url"]
        artist = request.form["artist"]

        database_path = "/static/library/"
        # if user does not select file, browser also
        # submit an empty part without filename

        if url and allowedFile(url.filename):
            filename = secure_filename(url.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            database_path += filename
            url.save(local_path)

        if not url:
            return render_template("add_medias.html",
                                   info="Please enter Url",
                                   artists=artists)

        log.warning(database_path)

        if database_path:
            db.addPicture(database_path, False, artist)

        return render_template("add_medias.html",
                               info=f"Import Done! {filename}",
                               artists=artists)


@app.route('/add_url_picture', methods=['POST'])
def add_url_picture():

    db = Database(CONFIG["database"])
    artists = db.listAllArtistName()

    if request.method == 'POST':
        url = request.form["url"]
        artist = request.form["artist"]
        save_local = request.form.get("save_local")

        if not url:
            return render_template("add_medias.html",
                                   info="Please enter Url",
                                   artists=artists)

        db.addPicture(url, save_local, artist)

        return render_template("add_medias.html",
                               info=f"Import Done! {url}",
                               artists=artists)


@app.route('/scrap_by_url', methods=['POST'])
def scrap_by_url():

    db = Database(CONFIG["database"])
    artists = db.listAllArtistName()

    if request.method == 'POST':

        url = request.form["url"]
        artist = request.form["artist"]
        save_local = request.form.get("save_local")

        if not url:
            return render_template("add_medias.html",
                                   info="Nothing to scrap",
                                   artists=artists)

        urls = getPicturesFromURL(url)

        for url in urls:
            if isValidPictureUrl(url):
                db.addPicture(url, save_local, artist)

        return render_template("add_medias.html",
                               info=f"Scrap Done!",
                               artists=artists)


@app.route('/edit', methods=['GET', 'POST'])
def edit():

    db = Database(CONFIG["database"])

    if request.method == 'GET':
        data = request.args
        if "url" in data:
            url = data["url"]

        if "command" in data:
            command = data["command"]
            subprocess.run(command)

        current_artist = db.getArtistWithUrl(url)
        artists = []
        temp_artists = db.listAllArtistName()

        for artist in temp_artists:
            if artist != current_artist:
                artists.append(artist)

        current_tags = db.getTagsWithUrl(url)
        tags = db.listAllTag()

        color = db.getColorWithUrl(url)

        commands = buildCommands(url)

        return render_template("edit.html",
                               url=url,
                               current_artist=current_artist,
                               artists=sorted(artists),
                               current_tags=current_tags,
                               tags=sorted(tags),
                               color=color,
                               commands=commands)

    ############################################################################
    # POST
    ############################################################################

    if request.method == 'POST':
        url = request.form["url"]
        current_artist = request.form["current_artist"]
        previous_tags = request.form["previous_tags"]
        current_tags = request.form["current_tags"]

        if current_artist:
            db.updateArtist(url, current_artist)

        if current_tags:
            split_space = current_tags.split(" ")
            without_space = "".join(split_space)
            list_current_tags = without_space.split(",")
            for current_tag in list_current_tags:
                if current_tag:
                    db.addTagToMedia(url, current_tag)

            list_tags_to_remove = []
            list_previous_tags = previous_tags.split(",")
            for previous_tag in list_previous_tags:
                if previous_tag not in list_current_tags:
                    list_tags_to_remove.append(previous_tag)

            if list_tags_to_remove:
                for tag_to_remove in list_tags_to_remove:
                    db.removeTagToMedia(url, tag_to_remove)

        tags = db.listAllTag()

        artists = []
        temp_artists = db.listAllArtistName()

        for artist in temp_artists:
            if artist != current_artist:
                artists.append(artist)

        color = db.getColorWithUrl(url)

        commands = buildCommands(url)

        return render_template("edit.html",
                               url=url,
                               current_artist=current_artist,
                               artists=sorted(artists),
                               current_tags=current_tags,
                               tags=sorted(tags),
                               color=color,
                               commands=commands)


@app.route('/delete', methods=['GET'])
def delete():
    db = Database(CONFIG["database"])

    data = request.args
    if 'url' in data:
        url = data['url']
        db.deletePicture(url)

    if 'artist' in data:
        artist = data['artist']
        db.deleteArtist(artist)

    pictures = db.getAllMedias(0, 50)

    return render_template("index.html", pictures=pictures)


if __name__ == "__main__":

    qt_app = QApplication(sys.argv)

    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True,
              'use_reloader': False, 'debug': False}

    threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    win = MainWindow()
    win.show()

    sys.exit(qt_app.exec_())
