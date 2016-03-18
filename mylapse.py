from moviepy.editor import *
import os
import click
import dateparser
import imgdb
import datetime


source_path = '/data/_input/prefixed-photos-thumbs/320x'


def img_iterator(db, timeblocks, size):
    for start_at, end_at in timeblocks:
        for img in db.filter(start_at=start_at, end_at=end_at):
            if size:
                yield img[size]
            else:
                yield img.path


class TimestampedImageSequenceClip(CompositeVideoClip):
    def __init__(self, *args, **kwargs):
        self.clips = []
        self.add_timestamp = kwargs.pop('timestamp', False)
        self.timelapse = ImageSequenceClip(*args, **kwargs)
        self.clips.append(self.timelapse)
        if self.add_timestamp:
            txt_clip = TextClip("MoviePy ROCKS", fontsize=50, color='white')
            self.txt_clip = txt_clip.set_pos('center').set_duration(5)
            self.clips.append(self.txt_clip)
        super(TimestampedImageSequenceClip, self).__init__(self.clips)


timespan_helptext = (
    'time ranges like this "2016-03-01 11:00->2016-03-01 18:00" '
    'or this "2016-01-01->2016-03-18@6;12;18". Multiples comma seperated.'
)

@click.command()
@click.option('--timespan', help=timespan_helptext')
@click.option('--fps', default=15)
@click.option('--outfile')
@click.option('--dryrun', default=False)
@click.option('--size', default=None)
@click.option('--timestamp', default=False)
def create_timelapse(timespan, fps, outfile, dryrun, size, timestamp):
    db = imgdb.ImgDB()
    timeblocks = []
    duration = datetime.timedelta()
    for timeblock in timespan.split(','):
        timeblock = timeblock.strip()
        if not timeblock:
            continue
        start_at, end_at = timeblock.split('->')
        assert '@' not in start_at
        start_at = dateparser.parse(start_at)
        if '@' in end_at:
            end_at, times = end_at.split('@')
        else:
            times = None
        end_at = dateparser.parse(end_at)
        if times:
            current_datetime = start_at
            while current_datetime <= end_at:
                for hour in times.split(';'):
                    micro_start_at = current_datetime + datetime.timedelta(hours=int(hour)-1, seconds=59*60)
                    micro_end_at = current_datetime + datetime.timedelta(hours=int(hour), seconds=1*60)
                    timeblocks.append((micro_start_at, micro_end_at))
                    duration += micro_end_at - micro_start_at
                current_datetime = current_datetime + datetime.timedelta(hours=24)
        else:
            timeblocks.append((start_at, end_at))
            duration += end_at - start_at

    click.echo('creating timelapse for following timespans'.format(timeblocks, duration))
    for start_at, end_at in timeblocks:
        click.echo('    {} -> {}'.format(str(start_at), str(end_at)))
    img_paths = list(img_iterator(db=db, timeblocks=timeblocks, size=size))
    frame_count = len(img_paths)
    click.echo('  {} frames, {} fps, {}s, {}'.format(
        frame_count,
        fps,
        frame_count/fps,
        size or 'original size',
    ))
    if dryrun:
        click.echo('dryrun. exiting.')
        return
    click.echo('  image sequence clip...')
    # video = ImageSequenceClip(img_paths, fps=fps)
    video = TimestampedImageSequenceClip(img_paths, fps=fps, timestamp=timestamp)
    # video = CompositeVideoClip([clip])
    click.echo('  writing video...')
    try:
        os.makedirs(os.path.dirname(outfile))
    except OSError:
        pass
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
