tagit
=====

A Python [Mutagen] audio file tagger for folder based music archives.

Description
-----------

Post ripping audio file tagger for folder based music archives.
Developed for cleanup of folder based audio file archives and for post-ripp
tagging e.g. after ripped with [abcde].

Features
--------
* mp3 and m4a (AAC) support.
* Ability to tag complete folder based music archives.
* Single folder tagging support as well.
* iTunes recognized tags.
* Embeds album cover.
* Informative tagging output.
* Folder renaming, for common folder notation.

Requirements
------------
* A folder based music archive, recommendation is to have on CD represented by one folder.
* Audio file names in the notation ```<track>-<titel>-<artist>.<extension>``` or 
  ```<titel>-<artist>.<extension>``` for doing a file to tag tagging. 
* An album cover image in jpg format, named *cover.jpg* is required in each CD folder
  to tag the album cover.
* An album info file named *album.info* in each CD music folder in Python ConfigParser style is
  required for tagging album, albumartist, date, genre, discnumber and totaldiscs.

Example *album.info* file content for a single artist folder:
```
[albuminfo]
album = Thriller
albumartist = Michael Jackson
date = 1982
genre = Pop
discnumber = 1
totaldiscs = 1
```

Example *album.info* file content for a multiple artist folder:
```
[albuminfo]
album = Standing in the Shadows of Motown
albumartist = Various Artists
date = 2003
genre = Soul
discnumber = 1
totaldiscs = 1
```

Usage
-----
```
usage: tagit.py [-h] [-v] [-s SINGLE | -a] [-i]

audio file tagger for folder based music archives for mp3 and m4a files

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s SINGLE, --single SINGLE
                        single directory, input must be the directory name
  -a, --archive         complete audio file directory archive, starting from
                        the current directory
  -i, --info            gives a verbose output about the tagging status
  -n, --no-info         suppresses the verbose output about the tagging status
```

Tag Mapping Table
-----------------

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

Good Other Stuff
----------------
* [neroAacEncoder] my AAC (m4a) encoder choice.
* [abcde] the best Linux CD ripper, command line only, but who needs more.
* If you are looking for a tagger with a great graphical UI
  go for [Puddeltag].

[Mutagen]:https://pypi.python.org/pypi/mutagen/1.23
[neroAacEncoder]:http://www.nero.com/enu/company/about-nero/nero-aac-codec.php
[abcde]:https://code.google.com/p/abcde/
[MusicBrainz Picard Mapping]:https://musicbrainz.org/doc/MusicBrainz_Picard/Tags/Mapping
[Puddeltag]:http://puddletag.sourceforge.net/