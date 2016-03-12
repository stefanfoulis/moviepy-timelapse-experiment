from moviepy.editor import *
from collections import OrderedDict
import os
import click
import json
import dateparser
import imgdb


source_path = '/data/_input/prefixed-photos-thumbs/320x'


def _create_video(images, )


@click.command()
@click.option('--start-at')
@click.option('--end-at')
@click.option('--fps', default=15)
@click.option('--outfile')
@click.option('--dryrun', default=False)
@click.option('--width', default=None)
def create_timelapse(start_at, end_at, fps, outfile, dryrun):
    db = imgdb.ImgDB()
    img_paths = []
    start_at = dateparser.parse(start_at)
    end_at = dateparser.parse(end_at)
    click.echo('creating timelapse for timespan of {} until {} ({})'.format(start_at, end_at, end_at - start_at))
    for img in db.filter(start_at=start_at, end_at=end_at):
        img_paths.append(img.path)
    frame_count = len(img_paths)
    click.echo('  {} frames, {} fps, {}s'.format(
        frame_count,
        fps,
        frame_count/fps,
    ))
    if dryrun:
        click.echo('dryrun. exiting.')
        return
    click.echo('  image sequence clip...')
    video = ImageSequenceClip(img_paths, fps=fps)
    # video = CompositeVideoClip([clip])
    click.echo('  writing video...')
    video.write_videofile(outfile, audio=False)


@click.group()
def cli():
    pass

cli.add_command(create_timelapse)


def old():
    for (dirpath, dirnames, filenames) in os.walk(source_path):
        jpgs = [os.path.join(dirpath, filename) for filename in filenames if os.path.splitext(filename)[1].lower()=='.jpg' and filename.startswith('2016-01-14')]
        # filenames_filtered.extend(list(set(jpgs)))
        break

    # clip = VideoFileClip("/data/_output/Abbruch-Tag-1.mp4").subclip(30,60)
    clip = ImageSequenceClip(jpgs, fps=15)

    txt_clip = TextClip("MoviePy ROCKS",fontsize=50,color='white')
    txt_clip = txt_clip.set_pos('center').set_duration(5)


    video = CompositeVideoClip([clip, txt_clip])

    video.write_videofile("/data/_output/mylapse-test-3.webm", audio=False)





if __name__ == '__main__':
    cli()
