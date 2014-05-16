tagit
=====

A Python Mutagen audio file Tagger for folder based music archives.

Motivation:
-----------
A long story which comes later.

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

Reference:
https://musicbrainz.org/doc/MusicBrainz_Picard/Tags/Mapping

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
