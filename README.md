tagit
=====

A Python Mutagen audio file Tagger for folder based music archives.

Motivation:
-----------
A long story which comes later.

Features:
---------
Will bee added soon.

Requirements:
-------------
- An album cover image in jpg format, named "cover.jpg" is required in each CD folder
  to tag the album cover.
- An album info file in each CD music folder in Python ConfigParser style is
required for tagging album, albumartist, date, genre, discnumber and totaldiscs.

Example:
```
[albuminfo]
album = Thriller
albumartist = Michael Jackson
date = 1982
genre = Pop
discnumber = 1
totaldiscs = 1
```

Usage:
------
```
usage: tagit.py [-h] [-v] [-s SINGLE | -a]
                [-u {all,album,albumartist,cover,genre}] [-i]

audio file archive tagger for mp3 and m4a

optional arguments:
  -h, --help            show this help message & exit
  -v, --version         show programs version number & exit
  -s <dir>, --single <dir> single directory, input must be the folder name
  -a, --archive         complete audio file directory archive, starting from the 
                        current directory
  -u {all,album,albumartist,cover,genre}, 
      --update {all,album,albumartist,cover,genre}
                        updates only the defined tag fields, 
                        all tags all fields form album.info plus cover
  -i, --info            gives a verbose output about the tagging status
```
-u is a blind option so far.


Tag Mapping Table:
------------------

The following tables describes the tag maps I have used in my code
for internal tag names, iTunes (m4a) and ID3v2 (mp3).

Reference: [MusicBrainz Picard Mapping]

| Internal Name | MP4 (iTunes) | MP3 (ID3v2 4.0) 
|---------------|--------------|-----------------
| tracknumber   | trkn         | TRCK            
| totaltracks   | trkn         | TRCK         
| title         | \xa9nam      | TIT2       
| artist        | \xa9ART      | TPE1
| album         | \xa9alb      | TALB        
| date          | \xa9day      | TDRC        
| genre         | \xa9gen      | TCON
| albumartist   | aART         | TPE2          
| discnumber    | disk         | TPOS
| totaldiscs    | disk         | TPOS
| cover         | covr         | APIC


Coding style:
-------------
Even though I'm mainly used to write code in a proprietary Lisp dialect
I tried to write pythonic code according to:
- [Style Guide for Python Code]
- [The Zen of Python]


Good other stuff:
-----------------
- If you are looking for a Tagger with a great graphical UI
  go for [Puddeltag].
- [Beets] a music collection organizer which looks for Music Brainz entries, as well on GitHub.

[MusicBrainz Picard Mapping]:https://musicbrainz.org/doc/MusicBrainz_Picard/Tags/Mapping
[Style Guide for Python Code]:http://legacy.python.org/dev/peps/pep-0008/
[The Zen of Python]:http://legacy.python.org/dev/peps/pep-0020/
[Puddeltag]:http://puddletag.sourceforge.net/
[Beets]:http://beets.radbox.org/
