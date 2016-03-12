from moviepy.editor import *
from collections import OrderedDict
import os

source_path = '/data/_input/prefixed-photos'

images = OrderedDict()
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
