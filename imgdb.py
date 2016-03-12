# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
import yaml
from pprint import pprint
import os
import click
from resizeimage import resizeimage
from PIL import Image


SOURCE_PATH = '/data/_input/prefixed-photos'
THUMBS_PATH = '/data/_input/prefixed-photos-thumbs'
# THUMBS_PATH = '/work/thumbs'


@click.group()
def cli():
    pass


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


def _resize(inpath, outpath, width):
    with open(inpath, 'r+b') as infile:
        with Image.open(infile) as inimage:
            thumb = resizeimage.resize_width(inimage, width, validate=True)
            thumb.save(outpath, inimage.format)


@click.command()
@click.option('--name', default=None, help='identifier for the thumbnail type')
@click.option('--width', default=640, help='desired width for the thumbnail')
@click.option('--date', help='date for which thumbnails should be generated')
@click.option('--hour', default=None, help='hour (of date) for which thumbnails should be generated')
@click.option('--overwrite', default=False, help='whether to overwrite existing thumbnails')
def generate_thumbnails(name, width, date, hour, overwrite):
    with open('db.json', 'r') as dbfile:
        db = json.load(dbfile)
    if hour:
        images = db[date][hour]
    else:
        images = []
        for lst in db[date].values():
            images.extend(lst)
    basedir = SOURCE_PATH
    name = name or '{}x'.format(width)
    for img in images:
        relpath = img.replace(basedir + '/', '')
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




cli.add_command(generate_db)
cli.add_command(generate_thumbnails)


if __name__ == '__main__':
    cli()
