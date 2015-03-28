#!/usr/bin/python3

import os
import string
import glob
import sys
import fcntl
import termios
import struct
import time
import argparse
from configparser import SafeConfigParser
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, error
from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TALB, TDRC, TCON, TPE2, TPOS, APIC

################################################################################
def usage():
    """Displays usage and processes the input arguments"""
 
    parser = argparse.ArgumentParser(
                description = 
                    'audio file tagger for folder based music archives '
                    'for mp3 and m4a files'
                )

    # Singel and archive will be exclusive arguments
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
        help = 'complete audio file directory archive, starting from the '
                'current directory'
        )

    parser.add_argument(
        '-i', '--info',
        dest='info',
        action = 'store_true',
        help = 'gives a verbose output about the tagging status'
        ) 

    parser.add_argument(
        '-n', '--no-info',
        dest='info',
        action = 'store_false',
        help = 'suppresses the verbose output about the tagging status'
        )
    
    parser.set_defaults(info=True)

    # Hidden arguments, just to store the file names
    parser.add_argument(
        '-c', '--cover',
        action = 'store',
        default = 'cover.jpg',
        help = argparse.SUPPRESS
        )

    parser.add_argument(
        '-f', '--foldertags',
        action = 'store',
        default = 'album.info',
        help = argparse.SUPPRESS
        )    
 
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    return vars(args)

#############################################################################
def queryYesNo(question, default='yes'):
    """Asks a yes/no question via raw_input() and returns True for yes and
        False for no.
    """
    
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
            sys.stdout.write('Please respond with "yes" or "no" '
                                '(or "y" or "n").\n')

################################################################################                             
def createPrompt(path):
    """Checks if a file exists and ask to create it if not."""

    if os.path.isfile(path):
        return os.path.basename(path)
    else:
        TrueFalse = queryYesNo(
                    'File "%s" does not exists, do you want to proceed?' % 
                    os.path.basename(path)
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
    """Reads the album info file and adds the content to the tag dictionary
        as string type.
        Posible album info options are:
        album, albumartist, date, genre, discnumber, totaldiscs
    """
    
    parser = SafeConfigParser()
    parser.read(albumInfoPath)
    for option in parser.options('albuminfo'):
        if parser.has_option('albuminfo', option):
                tags[option] = parser.get('albuminfo', option)
        
    return tags
    
################################################################################    
def getCover(coverPath, tags):
    """Reads the album cover image and adds it to the tag dictionary."""

    tags['cover_image'] = open(coverPath, 'rb').read()
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
    
    print('Tagging audio file: %s' %
          (color('1;33', os.path.basename(fileName)))
          )

    tagNames = [
        'track', 'title', 'artist','album', 'albumartist', 'genre', 'date'
        ]

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
def createAlbumName(tags):
    """Creates the album name according the following rules:
        Various artists:            Album name
        Various artists multi disc: Album name + disc no.
        Single artist:              Artsit name + album name
        Single artist multi disc:   Artsit name + album name + disc no. 
    """    
        
    if 'albumartist' in tags and tags['albumartist'] == 'Various Artists':
        if 'totaldiscs' in tags and int(tags['totaldiscs']) > 1:
            newName = (tags['album'].title() +
                        ' CD' + tags['discnumber'])
        else:
            newName = tags['album'].title()
    else:
        if 'totaldiscs' in tags and int(tags['totaldiscs']) > 1:
            newName = (tags['artist'].title() + '-' +
                        tags['album'].title() + ' ' +
                        'CD' + tags['discnumber'])
        else:    
            newName = (tags['artist'].title() + '-' +
                        tags['album'].title())
    return(newName)

################################################################################
def tagMP4(folder, audioFile, tags, info):
    """Tags the m4a files."""

    # Get mp4 audio file
    mp4audio = MP4(audioFile)

    # Update tags.
    # For m4a old tags are not deleted, because source is abcde ripper.
    #mp4audio.delete(audioFile) 
    
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
        mp4audio['disk'] = [(int(tags['discnumber']), int(tags['totaldiscs']))]
    # Build cover data annd add cover tag
    if 'cover_image' in tags:
        cover = []
        cover.append(MP4Cover(tags['cover_image'] , MP4Cover.FORMAT_PNG))
        mp4audio['covr'] = cover
              
    # Save new tags.
    mp4audio.save( )
    
################################################################################
def tagMP3(folder, audioFile, tags, info):
    """Tags the mp3 files."""
     
    # Get mp3 audio file    
    # and create ID3 tag if not present
    mp3audio = MP3(audioFile, ID3 = ID3)
   
    # Tag everything new.
    # Delete old tags first.
    # For mp3 old tags are delted, because source in unknown.
    mp3audio.delete(audioFile)

    # Adding new tags.
    if 'track' in tags and 'totaltracks' in tags: 
        mp3audio['TRCK'] = TRCK(
                            encoding = 3,
                            text = str(tags['track']) + '/' + 
                                    str(tags['totaltracks'])
                            )
    mp3audio['TIT2'] = TIT2(encoding = 3, text = tags['title'])
    mp3audio['TPE1'] = TPE1(encoding = 3, text = tags['artist'])
    if 'album' in tags:
        mp3audio['TALB'] = TALB(encoding = 3, text = tags['album']) 
    if 'albumartist' in tags:
        mp3audio['TPE2'] = TPE2(encoding = 3, text = tags['albumartist']) 
    if 'date' in tags:
        mp3audio['TDRC'] = TDRC(encoding = 3, text = tags['date']) 
    if 'genre' in tags:
        mp3audio['TCON'] = TCON(encoding = 3, text = tags['genre'])  
    if 'discnumber' in tags and 'totaldiscs' in tags:
        mp3audio['TPOS'] = TPOS(
                            encoding = 3,
                            text = str(tags['discnumber']) + '/' + 
                                    str(tags['totaldiscs'])
                            )
    if 'cover_image' in tags:
        mp3audio['APIC'] = APIC(
                            encoding = 3, 
                            mime = 'image/jpg', 
                            type = 3, # 3 is for the cover image
                            desc = 'Cover',
                            data = tags['cover_image']
                            )
    # Save new tags.
    mp3audio.save()
   
################################################################################
def tagit(folder, tags, info):
    """Tag it parent routine, check the correct tag method foreach file in the
        defined folder and receive the tags form then file name.
    """
    i = 0
    for fileName in os.listdir(folder):
        # Check if the file name contains more than one dot in the name, 
        # if yes this will create issues with splitting the extension.
        if fileName.count('.') == 1: 
            # Check if the filname is a audio file.
            if (os.path.isfile(os.path.join(folder, fileName)) and
                fileName.lower().endswith(('.m4a', '.mp3'))):
                # Check if there is a separator '-' for track, title and artist,
                # to check file naming for:
                #     track-title-artist
                #     tilte-artist
                if '-' in fileName:
                    if fileName.count('-') == 2:
                        method = 'withTrack'
                    elif fileName.count('-') == 1:
                        method = 'withOutTrack'
                    else:
                        sys.exit((color('1;31', 'File name: "%s" contains more than two hyphens, maximum two are allowed.' %
                                (fileName)))
                                )

                # Get audio file extension, should be ".m4a" or ".mp3'
                extension = os.path.splitext(fileName)[1][1:].strip().lower()

                # Assign the tag variables retrieved form file name,
                # dependent for the file naming with or witout track.
                if method == 'withTrack':
                    tags['track'] = fileName.split('-')[0].strip()
                    tags['title'] = fileName.split('-')[1].strip()
                    rest = fileName.split('-')[2].strip()
                    tags['artist'] = rest.split('.')[0].strip()
                elif method == 'withOutTrack':
                    tags['title'] = fileName.split('-' )[0].strip()
                    rest = fileName.split('-')[1].strip()
                    tags['artist'] = rest.split('.')[0].strip()

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
            sys.exit((color('1;31', 'File name: "%s" contains two dots, only one is allowed.' %
                    (fileName)))
                    )
            
################################################################################
def renameAudioFolder(oldName, tags, info):
    """Renames the audio folder according the following rules:
        Various artists:            Album name
        Various artists multi disc: Album name + disc no.
        Single artist:              Artsit name + album name
        Single artist multi disc:   Artsit name + album name + disc no.
    """
    
    if os.path.isdir(oldName):
        newName = createAlbumName(tags)
        os.rename(oldName, newName)
    else:
        sys.exit()
    
################################################################################
def main():
    """Resolves the command line arguments and checks for supporting files
        cover.jpg and album.info.
    """

    rootFolder = os.getcwd()
    args = usage()
    info = args['info']

    if args['single']:
        if os.path.isdir(args['single']):
            albumFolders = [args['single']]
        else:
            sys.exit('%s "%s" %s' % (
                        (color('1;31', 'Folder')),
                        (color('1;31', args['single'])),
                        (color('1;31', 'is no directory!'))
                        )
                    )

    if args['archive']:
        albumFolders = next(os.walk('.'))[1]

    # Looping through all the album folders
    if albumFolders:
        for albumFolder in albumFolders:
            tags = {}
            if info:
                print('Tagging audio folder: %s' % (color('1;33', albumFolder)))
            folder = os.path.join(rootFolder, albumFolder)

            # Album cover check
            coverImage = args['cover']
            coverPath = os.path.join(folder, coverImage)
            coverReturn = createPrompt(coverPath) # True/False
            if coverReturn == coverImage:
                tags = getCover(coverPath, tags)   
            elif not coverReturn:
                sys.exit()

            # Album info file check
            albumInfo = args['foldertags']
            albumInfoPath = os.path.join(folder, albumInfo)
            albumInfoReturn = createPrompt(albumInfoPath) # True/False
            if albumInfoReturn == albumInfo:
                tags = getAlbumInfo(albumInfoPath, tags)
            elif not albumInfoReturn:
                sys.exit()

            # Tag it
            tagit(folder, tags, info)

            # Renaming the album folder
            if 'album' in tags and 'artist' in tags:
                renameAudioFolder(albumFolder, tags, info)
            else:
                print('Could not rename audio folder, '
                        'no artist or alblum information found.'
                    )
            print()

        print('%s' % (color('1;32', 'Successfully completed!')))
    else:
        sys.exit('%s' % (color('1;31', 'Exit, no album folder found!')))   
    
if __name__ == '__main__':
    main()