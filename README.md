python mylapse.py create_timelapse --timespan="2016-03-01 06:00->2016-03-01 19:00,2016-03-02 06:00->2016-03-02 19:00,2016-03-03 06:00->2016-03-03 19:00,2016-03-07 06:00->2016-03-07 19:00,2016-03-08 06:00->2016-03-08 19:00,2016-03-09 06:00->2016-03-09 19:00,2016-03-10 06:00->2016-03-10 19:00" --outfile=/data/_output/test/2016-03-03--10-ohne-Wochenende-25fps.mp4 --size=640x480 --fps=25


python mylapse.py create_timelapse --timespan="2016-03-01 06:00->2016-03-01 19:00,2016-03-02 06:00->2016-03-02 19:00,2016-03-03 06:00->2016-03-03 19:00,2016-03-07 06:00->2016-03-07 19:00,2016-03-08 06:00->2016-03-08 19:00,2016-03-09 06:00->2016-03-09 19:00,2016-03-10 06:00->2016-03-10 19:00" --outfile=/data/_output/test/2016-03-03-bis-2016-03-11-ohne-Wochenende-25fps.mp4 --size=640x480 --fps=25

python mylapse.py create_timelapse --timespan="2016-03-11 06:00->2016-03-11 19:00" --outfile=/data/_output/test/test-2016-03-11--1.mp4 --size=640x480 --fps=25


python imgdb.py generate_db
