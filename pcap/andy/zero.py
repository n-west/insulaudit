#!/usr/bin/python
"""
zero.py - Analyze raw data history segments read from an insulin
pump.
Right now this is really just a hexdumper that can iterate through a
data page in chunks of a given size, and can begin at a given
offset.  See --help for information.  The script prints information
on how to reproduce runs.

The mm_*.data files are bytes collected by the auditing software to
represent the data responses to the commands in the filename.  An
index of commands is found in the project's README.  We know that
the history segments found in the raw logs are bigger than the
medium doing the transport, and that multiple passes of commands are
needed in order to obtain the results.

The Carelink*.csv data contains some overlapping data segments with
the *.data files found here.  It is not likely that all the
information in the csv file is found in the *.data files.  The
serial number of the device, found in code.txt may or may not be
used to encode certain pieces of information.

This script is primed to experiment with decoding chunks of data
read at standard intervals.  It would be a small change to
experiment with ways of decoding these chunks of if one could find a
likely starting place, and a likely size for a first record.

If you enjoy technical puzzles, this is a great one.

-bewest and collaborators.
"""

# stdlib imports
import sys, os, logging
from os.path import getsize
import argparse, itertools

# Requires insulaudit to be in your eg PYTHONPATH=path/to/insulaudit
from insulaudit import lib
from insulaudit.log import logger
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.DEBUG)

# debugging
from pprint import pprint, pformat

# globals
class settings:
  
  CHUNK_SIZE = 32
  PROLOG_SIZE = 0

def get_argparser():
  """Prepare an argument parser."""
  parser = argparse.ArgumentParser( )
  parser.add_argument(
    '--chunk', dest='chunk', type=int,
    default=settings.CHUNK_SIZE,
    help="Default chunksize: %s" % settings.CHUNK_SIZE)
  parser.add_argument(
    '--prolog', dest='prolog', type=int,
    default=settings.PROLOG_SIZE,
    help="Default prologue size: %s" % settings.PROLOG_SIZE)
  parser.add_argument(
    'input', nargs='+', help="Input files")
  return parser

def get_raw_handle(pathish):
  """Obtain a file-like handle from something describing access to
  data."""
  logger.info('opening %s' % (pathish))
  handle = open(pathish)
  return handle

def hex_dump_data(data):
  """My library has a convenient hexdumper, YMMV."""
  print lib.hexdump(bytearray(data))

def read_chunk(handle):
  """read a chunk, and normalize it's representation as a
  bytearray."""
  msg = (settings.CHUNK_SIZE, handle.tell( ))
#  logger.info('start reading (bytes %s) from offset %s' % msg)
  return bytearray(handle.read(settings.CHUNK_SIZE))

def decode_chunk(chunk):
  """
  Experiment: decode a chunk!
  TODO: how do we decode historical data?
  It's likely composed of regions representing records, either with
  some kind of delimiter, or with a common header.

  Looking at the hex dump of chunks, it does indeed look like there
  is some kind of repeating pattern.  But is there an offset to
  begin?  Is each record the same size, or is there a header
  describing the record?

  """
  try:
    record
  except NameError:
    global record 
    record = bytearray() # init for 1st run

  if chunk == 123:
    for byte in record.split():
      print ((int(byte))),
    try:
      rec = record.split()
      print ' ::  index:{index} day={date} {hour}:{minute} 20{year} rate={rawrate}*25={rate}, unknown=0x{unkwn} '.format(index=int(rec[1]), hour=int(rec[4]), minute=int(rec[3]), year=int(rec[6]), date=int(rec[5]), rawrate=int(rec[8]), rate=int(rec[8])*25, unkwn=rec[7])
    except IndexError:
      print '\n'
    record = bytearray(str(chunk)+' ') # clear the record
  else:
    record.extend(str(chunk)+' ')
  

def do_chunk(handle):
  """read a chunk, and call decode_chunk"""
  chunk = read_chunk(handle)
  decode_chunk(chunk[3])

def do_input(pathish):
  """given something that looks like a file path, try to get data
  and decode it.
  
  # first fast forward into some offset.
  # then report on how many chunks we read.
  """
  handle = get_raw_handle(pathish)
  pos  = handle.tell( )
  size = getsize(pathish)
  logger.info('opening %s (%s bytes)' % (pathish, size))

  # first fast forward into some offset.
  logger.info('reading prologue (%s bytes)' % (settings.PROLOG_SIZE))
  prolog = handle.read(settings.PROLOG_SIZE)

  # then report on how many chunks we read.
  for i in itertools.count( ):
    if pos < size:
#      logger.info('chunk: %s' % i)
      do_chunk(handle)
      pos = handle.tell( )
    else:
      break

def main(*args):
  """ some boiler plate to set up logging, reproducible runs, and
  get our little decoder's IO up and running.
  """
  global settings
  settings.CHUNK_SIZE, settings.PROLOG_SIZE
  parser = get_argparser( )
  args = list(args)
  cmd, args = args[0], args[1:]
  opts = parser.parse_args((args))
  #logger.info('opts: %s' % (pformat(args)))
  settings.CHUNK_SIZE = opts.chunk
  settings.PROLOG_SIZE = opts.prolog
  cmdline = [ cmd,
    '--chunk %s' % (settings.CHUNK_SIZE),
    '--prolog %s' % (settings.PROLOG_SIZE) ] + opts.input
  print ' '.join(cmdline)

  logger.info('opening %s' % (opts.input))

  for item in opts.input:
    do_input(item)

if __name__ == '__main__':
  main(*sys.argv)

#####
# EOF
