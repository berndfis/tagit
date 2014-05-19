tagit
=====

A Python [Mutagen] audio file tagger for folder based music archives.

Description
-----------

Will bee added soon.

Features
--------
* mp3 and m4a (AAC) support.
* Ability to tag complete folder based music archives.
* Single folder tagging support as well.
* iTunes recognized tags.
* Embeds album cover.
* Informative tagging output.

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
usage: tagit.py [-h] [-v] [-s SINGLE | -a]
                [-u {all,album,albumartist,cover,genre}] [-i]

audio file archive tagger for mp3 and m4a

optional arguments:
  -h, --help            show this help message & exit
  -v, --version         show programs version number & exit
  -s SINGLE, --single SINGLE single directory, input must be the folder name
  -a, --archive         complete audio file directory archive, starting from the 
                        current directory
  -u {all,album,albumartist,cover,genre}, 
      --update {all,album,albumartist,cover,genre}
                        updates only the defined tag fields, 
                        all tags all fields form album.info plus cover
  -i, --info            gives a verbose output about the tagging status
```
*-u is a blind option so far.*


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

Motivation
----------
A long story which comes later.

Coding Style
------------
Even though I'm mainly used to write code in a proprietary Lisp dialect
I tried to write pythonic code according to:
* [Style Guide for Python Code]
* [The Zen of Python]


Good Other Stuff
----------------
* [neroAacEncoder] my AAC (m4a) encoder choice.
* [abcde] the best Linux CD ripper, comand line only, but who needs more.
* [Asuder] a lean grahical CD ripper for Linux.
* If you are looking for a tagger with a great graphical UI
  go for [Puddeltag].
* [Beets] a music collection organizer which looks for Music Brainz entries, also  [Beets on GitHub].

[Mutagen]:https://code.google.com/p/mutagen/
[neroAacEncoder]:http://www.nero.com/enu/company/about-nero/nero-aac-codec.php
[abcde]:https://code.google.com/p/abcde/
[Asuder]:http://littlesvr.ca/asunder/
[MusicBrainz Picard Mapping]:https://musicbrainz.org/doc/MusicBrainz_Picard/Tags/Mapping
[Style Guide for Python Code]:http://legacy.python.org/dev/peps/pep-0008/
[The Zen of Python]:http://legacy.python.org/dev/peps/pep-0020/
[Puddeltag]:http://puddletag.sourceforge.net/
[Beets]:http://beets.radbox.org/
[Beets on GitHub]:https://github.com/sampsyo/beets
