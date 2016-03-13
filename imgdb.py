# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
import yaml
from pprint import pprint
import os
import click
from resizeimage import resizeimage
from PIL import Image
import dateparser


SOURCE_PATH = '/data/_input/prefixed-photos'
THUMBS_PATH = '/data/_input/prefixed-photos-thumbs'
# THUMBS_PATH = '/work/thumbs'


def datetime_from_filename(filename):
    datestr = filename[0:10]
    timestr = filename[11:19].replace('-', ':')
    return dateparser.parse('{} {}'.format(datestr, timestr))


class Img(dict):
    def __init__(self, path):
        super(Img, self).__init__()
        self.path = path
        self.filename = os.path.basename(path)
        self.date_taken = datetime_from_filename(self.filename)

    def __missing__(self, key):
        if 'x' not in key:
            raise KeyError
        try:
            width, height = key.split('x')
            width, height = int(width), int(height)
        except:
            raise KeyError
        basedir = SOURCE_PATH
        relpath = self.path.replace(basedir + '/', '')
        # click.echo(relpath)
        outpath = os.path.join(THUMBS_PATH, key, relpath)
        outdir = os.path.dirname(outpath)
        try:
            os.makedirs(outdir)
        except OSError:
            pass
        exists = os.path.exists(outpath)
        if not exists:
            click.echo('generating {}'.format(outpath))
            _resize(self.path, outpath, width=width, height=height)
        self[key] = outpath
        return outpath


class ImgDB(object):
    def __init__(self, dbpath='db.json'):
        self.dbpath = dbpath
        with open(dbpath, 'r') as dbfile:
            self.db = json.load(dbfile)

    def all(self):
        for day in self.db.values():
            for hour in day.values():
                for img in hour:
                    yield Img(img)

    def filter(self, start_at, end_at):
        # TODO: make more effecient
        for img in self.all():
            if img.date_taken and img.date_taken >= start_at and img.date_taken <= end_at:
                yield img


@click.command()
def generate_db(source_path=SOURCE_PATH):
    click.echo('Generating the image database')
    images = OrderedDict()
    for (dirpath, dirnames, filenames) in os.walk(source_path):
        for filename in filenames:
            datestr = filename[0:10]
            timestr = filename[11:19].replace('-', ':')
            hour = timestr[0:2]
            print(datestr, timestr, hour)
            images.setdefault(datestr, OrderedDict())
            images[datestr].setdefault(hour, [])
            images[datestr][hour].append(os.path.join(dirpath, filename))
            # create date keys
            # images.setdefault(dirname, OrderedDict())
        # jpgs = [os.path.join(dirpath, filename) for filename in filenames if os.path.splitext(filename)[1].lower()=='.jpg' and filename.startswith('2016-01-14')]
        # filenames_filtered.extend(list(set(jpgs)))
        # break

    with open('db.json', 'w') as dbfile:
        json.dump(images, dbfile, sort_keys=True, indent=4)

    with open('db.yaml', 'w') as dbfile:
        yaml.dump(images, dbfile, indent=4, default_flow_style=False)


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
        try:
            os.makedirs(outdir)
        except OSError:
            pass
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
