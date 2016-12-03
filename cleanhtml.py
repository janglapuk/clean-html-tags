#!/usr/bin/env python3

__AUTHOR__ = 'TRA'

import glob, os, sys, re

REGEX_TAGS = r'<[^>]*>'
MODE_FILE  = 1
MODE_DIR   = 2

def usage(argv, message='Please provide proper arguments.'):
  print()
  print('INVALID ARGUMENTS: {}'.format(message))
  print()
  print('Usage:')
  print('------')
  print('{} <[filepath|dirpath]> [<ext1[,ext2,ext3,...]>] [recursively=0/1]'.format(argv[0]))
  print()
  print('Example:')
  print('--------')
  print('File : {} {}'.format(argv[0], 'Game.of.Thrones.S06E10.720p.HDTV.x264-AVS.srt'))
  print('Dir  : {} {} {}'.format(argv[0], '/Volumes/Data/Documents/Movies', 'srt,txt'))

def pretty_exception(message, file, func):
  print('Exception on {}: {}'.format(func.__name__, message))
  print('   File: {}'.format(os.path.basename(file)))
  print()

def read_file(file):
  f, c = None, None

  try:
    f = open(file, 'r')
    c = f.read()
  except UnicodeDecodeError:
    f = open(file, 'r', encoding='ISO-8859-1')
    c = f.read()
  except Exception as e:
    pretty_exception(str(e), file, read_file)
    return None
  else:
    f.close()

  return c

def write_file(file, content):
  f = None

  try:
    f = open(file, 'w')
    f.write(content)
  except Exception as e:
    pretty_exception(str(e), file, write_file)
    return False
  else:
    f.close()

  return True

def clean_text(content, regexr=REGEX_TAGS):
  return re.sub(regexr, '', content)

def clean(mode, path, exts=None, recursive=True):
  path = os.path.abspath(path)

  if mode == MODE_FILE:

    content = read_file(path)
    if content == None:
      return -5

    cleaned = clean_text(content)

    if not write_file(path, cleaned):
      return -6
  
  elif mode == MODE_DIR:
    extensions = ['*.{}'.format(e) for e in exts]

    # crawl directory and get matched lists
    ext_files = [glob.glob(os.path.join(path, '**', e), recursive=recursive) for e in extensions]
    
    failed_files = []

    for files in ext_files:
      for file in files:
        content = read_file(file)

        if content == None:
          failed_files.append(file)
          continue

        cleaned = clean_text(content)

        if not write_file(file, cleaned):
          failed_files.append(file)
          continue
    
    num_fails = len(failed_files)
    if num_fails > 0:
      # No error but return numbers of failed files
      return num_fails

  return 0

if __name__ == '__main__':
  argv = sys.argv

  if len(argv) < 2:
    usage(argv)
    exit(-1)

  elif len(argv) == 2:
    file = argv[1]
    if not os.path.isfile(file):
      usage(argv, 'Invalid file!')
      exit(-2)

    retval = clean(MODE_FILE, file)

  elif len(argv) == 3:
    dir = argv[1]
    if not os.path.isdir(dir):
      usage(argv, 'Invalid directory!')
      exit(-3)

    exts = str(argv[2]).split(',')
    empty_ext = '' in exts

    if empty_ext:
      usage(argv, 'Wrong extensions!')
      exit(-4)

    retval = clean(MODE_DIR, dir, exts)

  if retval < 0:
    print('ERROR! Code: {}'.format(retval))
  elif retval > 0:
    print("Some files was cleaned but there\'s {} failed files to clean.".format(retval))

  exit(retval)
