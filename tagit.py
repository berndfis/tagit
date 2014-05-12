#!/usr/bin/python

# Next Stpes:
# - for -s check if dir exists
# - complete argparse --> update is implemented blind currently
# - form future import print

# TODO:
# options for
# - update or overwirte mode, abcde seems to tag correctly, if cover in album path works
#   update options have to be checked
# - -single -> done
# - -archive ->done
# - probably all update options could be grouped -> done
# - file format -> automatic detection             -> done
# - embed cover to file or just put it in the album path
#   -> check for iTunes -> done for iTunes, MortPlayer
#   -> check for networkpalyer support
# - create play list -> needed ?
# - smart various artist detection -> needed ? 
# - if everything is done try to restucture, make code beter

# TODO: Documentation

################################################################################
#
#   Git Hash:       $Id$
#   Date:           $Date$
#   File:           $File$
#   Author:         $Author$
#   Revision:       $Revision$
#
#   Motivation:
#   
#   Tag Mapping Table:
#
#   Internal Name       MP4             MP3
#   Compatible with:            
#   MusicBrainz Picard  iTunes          ID3v2 (4.0)
#   https://musicbrainz.org/doc/MusicBrainz_Picard/Tags/Mapping
#   ----------------------------------------------------------------------------
#   tracknumber         trkn            TRCK   
#   totaltracks         trkn            TRCK
#   title               \xa9nam         TIT2       
#   artist              \xa9ART        	TPE1
#   album               \xa9alb         TALB        
#   date                \xa9day         TDRC        
#   genre               \xa9gen         TCON
#   albumartist         aART            TPE2          
#   discnumber	        disk            TPOS
#   totaldiscs          disk            TPOS
#   cover               covr            APIC
#
#   Coding style:
#   Even though I'm mainly used to write code in a proprietary Lisp dialect
#   I tried to write pythonic code according to:
#   http://legacy.python.org/dev/peps/pep-0008/
#   http://legacy.python.org/dev/peps/pep-0020/
#
################################################################################

import os
import string
import glob
import sys
import fcntl
import termios
import struct
import time
import argparse
from ConfigParser import SafeConfigParser
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, error
from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TALB, TDRC, TCON, TPE2, TPOS, APIC

################################################################################
def usage():
    """Displays usage and processes the input arguments"""
 
    parser = argparse.ArgumentParser(
                description = 
                    'audio file archive tagger for mp3 and m4a',
                version = os.path.split( __file__ )[1] + 'Version: 0.1'
                )

    group = parser.add_mutually_exclusive_group()
    
    # Optional arguments      
    group.add_argument(
        '-s', '--single',
        action = 'store',
        help = 'single directory, input must be the directory name'
        )  
        
    group.add_argument(
        '-a', '--archive',
        action = 'store_true',
        help = 'complete audio file directory archive, starting from the current directory'
        )

    parser.add_argument(
        '-u', '--update',
        action = 'append',
        default = 'all',
        choices = ['all', 'album', 'albumartist', 'cover', 'genre'],
        help = 'updates only the defined tag fields, "all" tags all fields form album.info plus cover'
        )
    parser.add_argument(
        '-i', '--info',
        action = 'store_true',
        default = True,
        help = 'gives a verbose output about the tagging status'
        )    
 
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    return vars(args)

#############################################################################
def queryYesNo(question, default='yes'):
    """Ask a yes/no question via raw_input() and return their answer."""
    
    valid = {'yes':True, 'y':True, 'ye':True, 'no':False, 'n':False}
    if default == None:
        prompt = '[y/n]'
    elif default == 'yes':
        prompt = '[Y/n]'
    elif default == 'no':
        prompt = '[y/N]'
    else:
        raise ValueError( 'Invalid default answer: "%s"' % default )

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write('Please respond with "yes" or "no" (or "y" or "n").\n')

################################################################################                             
def createPrompt(path):
    """Checks if a file exists and ask to create it if not."""

    if os.path.isfile(path):
        return os.path.basename(path)
    else:
        TrueFalse = queryYesNo(
                    'File "%s" does not exists, do you want to proceed?' 
                    % os.path.basename(path)
                    )  
        return TrueFalse
    
################################################################################     
def color(this_color, string):
    """Creates a terminal color output."""

    return "\033[" + this_color + "m" + string + "\033[0m"

################################################################################
def progress(current, total):
    """Creates a terminal progress bar."""
    
    prefix = '%d/%d' % (current, total)
    barStart = ' ['
    barEnd = '] '
    barSize = len(prefix + barStart + barEnd ) + total
    amount = int(current / (total / float(barSize)))
    remain = barSize - amount
    bar = 'X' * amount + ' ' * remain
    return prefix + barStart + bar + barEnd

################################################################################           
def getAlbumInfo(albumInfoPath, tags):
    """Reads the album info file and adds the content to the tag dictionary.
        Posible album info options are:
        srtings: album, albumartist, date, genre
        integers: discnumber, totaldiscs
    """
    
    parser = SafeConfigParser()
    parser.read(albumInfoPath)
    for option in parser.options('albuminfo'):
        if parser.has_option('albuminfo', option):
           if option in ['discnumber', 'totaldiscs']:
                tags[option] = int(parser.get('albuminfo', option))
           else:    
                tags[option] = parser.get('albuminfo', option)
        
    return tags
    
################################################################################    
def getCover(folder, tags):
    """Reads the album cover image and adds it to the tag dictionary."""

    tags['cover_image'] = open(os.path.join(folder, 'cover.jpg'), 'rb').read()
    return tags

################################################################################
def createTagInfo(tagName, tags):
    """Creates the print info for tag."""
    
    if tagName in tags:
        print('\t%s: %s' % (tagName.title(), color('32', tags[tagName])))
    else:
        print('\t%s: %s' % (tagName.title(), color('31', 'No')))
    
################################################################################
def printTaggingInfo(fileName, tags, i):
    """Prints the tagging information and status of the audio file."""
    
    print('Tagging audio file: %s' % (color('1;33', os.path.basename(fileName))))

    tagNames = ['track', 'title', 'artist','album', 'albumartist', 'genre', 'date']

    for tagName in tagNames:
        createTagInfo(tagName, tags)
              
    if 'cover_image' in tags:
        print('\tCover: %s' % (color('32', 'Yes')))
    else:
        print('\tCover: %s' % (color('31', 'No')))

    # Print 
    sys.stdout.write(progress(i, tags['totaltracks']) + '\r')
    sys.stdout.flush()
    time.sleep(0.002)                  
    
################################################################################
def tagMP4(folder, audioFile, tags, info):
    # TODO: need a update function

    # Build cover data
    cover = []
    cover.append(MP4Cover(tags['cover_image'] , MP4Cover.FORMAT_PNG))

    # Get mp4 audio file
    mp4audio = MP4(audioFile)

    # Tag everything new.
    # Delete old tags first.
    mp4audio.delete(audioFile) 
    
    # Adding new tags.
    if 'track' in tags and 'totaltracks' in tags: 
        mp4audio['trkn'] = [(int(tags['track']), tags['totaltracks'])]
    mp4audio['\xa9nam'] = tags['title']
    mp4audio['\xa9ART'] = tags['artist']
    if 'album' in tags:
        mp4audio['\xa9alb'] = tags['album']
    if 'albumartist' in tags:
        mp4audio['aART'] = tags['albumartist']
    if 'date' in tags:
        mp4audio['\xa9day'] = tags['date']
    if 'genre' in tags:
        mp4audio['\xa9gen'] = tags['genre']
    if 'discnumber' in tags and 'totaldiscs' in tags:
        mp4audio['disk'] = [(tags['discnumber'], tags['totaldiscs'])]
    if 'cover_image' in tags:
        mp4audio['covr'] = cover
              
    # Save new tags.
    mp4audio.save( )
    
################################################################################
def tagMP3(folder, audioFile, tags, info):
    # TODO: need a update function
     
    # Get mp3 audio file    
    # and create ID3 tag if not present
    mp3audio = MP3(audioFile, ID3 = ID3)
   
    # Tag everything new.
    # Delete old tags first.
    mp3audio.delete(audioFile)

    # Adding new tags.
    if 'track' in tags and 'totaltracks' in tags: 
        mp3audio['TRCK'] =  TRCK(encoding = 3, text = unicode(str(tags['track']) + '/' + str(tags['totaltracks']))) 
    mp3audio['TIT2'] = TIT2(encoding = 3, text = unicode(tags['title']))
    mp3audio['TPE1'] = TPE1(encoding = 3, text = unicode(tags['artist']))
    if 'album' in tags:
        mp3audio['TALB'] = TALB(encoding = 3, text = unicode(tags['album'])) 
    if 'albumartist' in tags:
        mp3audio['TPE2'] = TPE2(encoding = 3, text = unicode(tags['albumartist'])) 
    if 'date' in tags:
        mp3audio['TDRC'] = TDRC(encoding = 3, text = unicode(tags['date'])) 
    if 'genre' in tags:
        mp3audio['TCON'] = TCON(encoding = 3, text = unicode(tags['genre']))  
    if 'discnumber' in tags and 'totaldiscs' in tags:
        mp3audio['TPOS'] = TPOS(encoding = 3, text = unicode(str(tags['discnumber']) + '/' + str(tags['totaldiscs']))) 
    if 'cover_image' in tags:
        mp3audio['APIC'] = APIC(
                            encoding = 3, 
                            mime = 'image/jpg', 
                            type = 3, # 3 is for the cover image
                            desc = u'Cover',
                            data = tags['cover_image']
                            )
    # Save new tags.
    mp3audio.save()
   
################################################################################
def tagit(folder, tags, info):

    i = 0
    for fileName in os.listdir(folder):
        # Check if the file name contains more than one dot in the name, 
        # if yes this will create issues with splitting the extension.
        if fileName.count('.') == 1: 
            # Check if the filname is a audio file.
            if os.path.isfile(os.path.join(folder, fileName)) and fileName.lower().endswith(('.m4a', '.mp3')):
                # Check if there is a separator '-' for track, title and artist,
                # to check file naming for:
                #     track-title-artist
                #     tilte-artist
                if '-' in fileName:
                    if fileName.count('-') == 2:
                        method = 'withTrack'
                    elif fileName.count('-') == 1:
                        method = 'withOutTrack'
                                        
                # Get audio file extension, should be ".m4a" or ".mp3'
                extension = os.path.splitext(fileName)[1][1:].strip().lower()

                # Assign the tag variables retrieved form file name,
                # dependent for the file naming with out witout track.
                if method == 'withTrack':
                    tags['track'] = string.split(fileName, '-')[0].strip()
                    tags['title'] = string.split(fileName, '-')[1].strip()
                    rest = string.split(fileName, '-')[2].strip()
                    tags['artist'] = string.split(rest, '.')[0].strip()
                elif method == 'withOutTrack':
                    tags['title'] = string.split(fileName, '-' )[0].strip()
                    rest = string.split(fileName, '-')[1].strip()
                    tags['artist'] = string.split(rest, '.')[0].strip()

                audioFile = os.path.join(folder, fileName)  

                if extension == 'mp3':
                    # Get total number of tracks.
                    tags['totaltracks'] = len(glob.glob1(folder, '*.mp3')) 
                    # Tag mp3
                    tagMP3(folder, audioFile, tags, info)

                if extension == 'm4a':
                    # Get total number of tracks.
                    tags['totaltracks'] = len(glob.glob1(folder, '*.m4a'))
                    # Tag mp4
                    tagMP4(folder, audioFile, tags, info)

                # Print the tagging information
                if info:
                    i +=1
                    printTaggingInfo(audioFile, tags, i)    
                      
        else:  
            print('File name: "%s" contains two dots, only one is allowed.' % ( fileName ))
            sys.exit()
            
################################################################################
def renameAudioFolder(oldName, tags, info):
    """Renames the audio folder according the following rules:
        Various artists:            Album name
        Various artists multi disc: Album name + disc no.
        Single artist:              Artsit name + album name
        Single artist multi disc:   Artsit name + album name + disc no.
    """
    print('DEBUG: %s' % tags['totaldiscs'])
    print('DEBUG: %s' % type(tags['totaldiscs']))
    if os.path.isdir(oldName):
        if 'albumartist' in tags and tags['albumartist'] == 'Various Artists':
            if 'totaldiscs' in tags and tags['totaldiscs'] > 1:
                newName = tags['album'].title().replace(' ', '') + 'CD' + str(tags['discnumber'])
            else:
                newName = tags['album'].title().replace(' ', '')
        else:
            if 'totaldiscs' in tags and tags['totaldiscs'] > 1:
                newName = tags['artist'].title().replace(' ', '') + tags['album'].title().replace(' ', '') + 'CD' + str(tags['discnumber'])
            else:    
                newName = tags['artist'].title().replace(' ', '') + tags['album'].title().replace(' ', '')
        if info:
            print('Renaming audio folder from %s to %s.' % (color('1;33', oldName), color('1;33', newName)))
        os.rename(oldName, newName)
    else:
        sys.exit()
    
################################################################################
def main( ):

    rootFolder = os.getcwd( )
    args = usage()
    info = args['info']
    if args['single']:
        albumFolders = [args['single']]
    if args['archive']:
        albumFolders = os.walk('.').next()[1]
    for  albumFolder in albumFolders:
        tags = {}
        if info:
            print('Tagging audio folder: %s' % (color('1;33', albumFolder)))
        folder = os.path.join(rootFolder, albumFolder)
        coverPath = os.path.join(folder, 'cover.jpg')
        coverReturn = createPrompt(coverPath) # True/False
        if coverReturn == 'cover.jpg':
            tags = getCover(folder, tags)   
        elif not coverReturn:
            sys.exit( )
        albumInfoPath = os.path.join(folder, 'album.info')
        albumInfoReturn = createPrompt(albumInfoPath) # True/False
        if albumInfoReturn == 'album.info':
            tags = getAlbumInfo(albumInfoPath, tags)
        elif not albumInfoReturn:
            sys.exit()
        tagit(folder, tags, info)
        if 'album' in tags and 'artist' in tags:
            renameAudioFolder(albumFolder, tags, info)
        else:
            print('Could not rename audio folder, no artist or alblum information found.') 
        print
    print('%s' % (color('1;32', 'Successfully completed!')))
    
if __name__ == '__main__':
    main( )
