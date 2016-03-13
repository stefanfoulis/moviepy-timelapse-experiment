# -*- coding: utf-8 -*-
import json
import os
import click
from resizeimage import resizeimage
from PIL import Image
import dateparser


SOURCE_PATH = '/data/_input/prefixed-photos'
THUMBS_PATH = '/data/_input/prefixed-photos-thumbs'
DB_BASEDIR = '/data/_input/db/'


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


def datetime_from_filename(filename):
    if all(filename[idx] == '-' for idx in (4, 7)):
        datestr = filename[0:10]
    else:
        return None
    if all(filename[idx] in ('-', ':') for idx in (13, 16)):
        timestr = filename[11:19].replace('-', ':')
    else:
        timestr = ''
    datetimestr = '{} {}'.format(datestr, timestr)
    return dateparser.parse(datetimestr)


class Img(dict):
    def __init__(self, base_path, rel_img_path, thumbs_base):
        super(Img, self).__init__()
        self.base_path = base_path
        self.rel_img_path = rel_img_path
        self.thumbs_base = thumbs_base
        self.path = os.path.join(base_path, rel_img_path)
        self.filename = os.path.basename(self.path)
        self.date_taken = datetime_from_filename(self.filename)

    def __missing__(self, key):
        if 'x' not in key:
            raise KeyError
        try:
            width, height = key.split('x')
            width, height = int(width), int(height)
        except:
            raise KeyError
        # click.echo(relpath)
        outpath = os.path.join(self.thumbs_base, key, self.rel_img_path)
        outdir = os.path.dirname(outpath)
        makedirs(outdir)
        exists = os.path.exists(outpath)
        if not exists:
            click.echo('generating {}'.format(outpath))
            _resize(self.path, outpath, width=width, height=height)
        self[key] = outpath
        return outpath


class Day(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self._db = None
        self.date = datetime_from_filename(os.path.basename(self.dbpath)).date()

    @property
    def db(self):
        if self._db is None:
            with open(self.dbpath, 'r') as dbfile:
                self._db = json.load(dbfile)
        return self._db


class ImgDB(object):
    def __init__(self, dbpath=DB_BASEDIR, img_path=SOURCE_PATH, thumbs_path=THUMBS_PATH):
        self.dbpath = os.path.abspath(dbpath)
        makedirs(self.dbpath)
        self.img_path = img_path
        self.thumbs_path = thumbs_path
        self._days = None

    def import_images(self, source_path=None):
        source_path = source_path or self.img_path
        for (day_dirpath, day_dirnames, day_filenames) in os.walk(source_path):
            for day_dirname in day_dirnames:
                if not all(day_dirname[idx] == '-' for idx in (4, 7)):
                    continue
                daydata = {
                    'date': day_dirname,
                    'basedir': source_path,
                    'images': []
                }
                for (img_dirpath, img_dirnames, img_filenames) in os.walk(os.path.join(day_dirpath, day_dirname)):
                    for filename in img_filenames:
                        if not filename.lower().endswith('.jpg'):
                            continue
                        abspath = os.path.join(img_dirpath, filename)
                        relpath = abspath.replace(self.img_path + '/', '')
                        daydata['images'].append(relpath)
                daydata['images'] = sorted(daydata['images'])
                with open(os.path.join(self.dbpath, '{}.json'.format(day_dirname)), 'w') as dbfile:
                    json.dump(
                        daydata,
                        dbfile,
                        sort_keys=True,
                        indent=4,
                    )
            break

    def days(self):
        for (dirpath, dirnames, filenames) in os.walk(self.dbpath):
            for filename in filenames:
                if filename.endswith('.json'):
                    day_db_path = os.path.join(dirpath, filename)
                    yield Day(dbpath=day_db_path)

    def all(self):
        for img in self.filter(start_at=None, end_at=None):
            yield img

    def filter(self, start_at, end_at):
        for day in self.days():
            if (start_at is None or start_at.date() <= day.date) and (end_at is None or end_at.date() >= day.date):
                for img_relpath in day.db['images']:
                    img = Img(self.img_path, img_relpath, self.thumbs_path)
                    if img.date_taken and img.date_taken >= start_at and img.date_taken <= end_at:
                        yield img


@click.command()
def generate_db():
    click.echo('Generating the image database')
    db = ImgDB()
    db.import_images()


def _resize(inpath, outpath, width=None, height=None):
    with open(inpath, 'r+b') as infile:
        with Image.open(infile) as inimage:
            if width and height:
                thumb = resizeimage.resize_cover(inimage, [width, height])
            elif width:
                thumb = resizeimage.resize_width(inimage, width, validate=True)
            elif height:
                thumb = resizeimage.resize_height(inimage, height, validate=True)
            else:
                raise RuntimeError('at least width or height must be provided')
            thumb.save(outpath, inimage.format)


@click.command()
@click.option('--name', default=None, help='identifier for the thumbnail type')
@click.option('--start-at')
@click.option('--end-at')
@click.option('--width', default=640, help='desired width for the thumbnail')
@click.option('--date', help='date for which thumbnails should be generated')
@click.option('--hour', default=None, help='hour (of date) for which thumbnails should be generated')
@click.option('--overwrite', default=False, help='whether to overwrite existing thumbnails')
def generate_thumbnails(name, width, start_at, end_at, overwrite):
    db = ImgDB()
    start_at = dateparser.parse(start_at)
    end_at = dateparser.parse(end_at)
    basedir = SOURCE_PATH
    name = name or '{}x'.format(width)
    for img in db.filter(start_at=start_at, end_at=end_at):
        relpath = img.path.replace(basedir + '/', '')
        # click.echo(relpath)
        outpath = os.path.join(THUMBS_PATH, name, relpath)
        outdir = os.path.dirname(outpath)
        os.makedirs(outdir)
        exists = os.path.exists(outpath)
        if exists and not overwrite:
            click.echo('skipping {}'.format(outpath))
        else:
            click.echo('generating {}'.format(outpath))
            _resize(img, outpath, width=width)


@click.group()
def cli():
    pass


cli.add_command(generate_db)
cli.add_command(generate_thumbnails)


if __name__ == '__main__':
    cli()
