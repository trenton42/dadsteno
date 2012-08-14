import argparse
import sys
import os
import struct
import random

from PIL import Image
from collections import deque

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file',required=True, help='File to hide')
	parser.add_argument('-i', '--image',required=True, help='Image file. *Will be overwritten!')
	parser.add_argument('-d', '--decrypt', nargs='?', const=True, default=False)
	parser.add_argument('-p', '--password', nargs='?', const=True, default=False)
	args = parser.parse_args()
	
	password = None
	if args.password:
		password = raw_input('Enter Password: ')
	
	try:
		if args.decrypt:
			decrypt(args.image, args.file, password=password)
		else:
			encrypt(args.file, args.image, password=password)
	except Exception as err:
		print 'A bad bad thing happened: ', err
		sys.exit(1)

def encrypt(inf, outf, password=None):
	try:
		fp = open(inf, 'r')
	except IOError:
		raise Exception('Yer input file is NO GOOD. Take it back!')
	
	fs = os.stat(inf).st_size
	try:
		im = Image.open(outf)
	except IOError:
		raise Exception('Yer output file Does NOT work for me. Take it back!')
	av = getAvail(im)
	if fs+8 > av:
		raise Exception("It's not a TARDIS, ya know. Ye got too much stuff!")
	im = im.convert('RGB')
	seq = mergeData(im, fp, password=password)
	im.putdata(list(seq))
	im.save(outf)

def decrypt(inf, outf, password=None):
	try:
		fp = open(outf, 'w')
	except IOError:
		raise Exception('How can you expect me to work in these conditions?! The file you gave me to use for YOUR data does not work!')
	
	try:
		im = Image.open(inf)
	except IOError:
		raise Exception("I don't know what you did with this image, but it doesn't work at all.")
	im = im.convert('RGB')
	g = unmergeData(im, password)
	size = ''
	for i in range(8):
		sn = g.next()
		size += sn
	try:
		size = struct.unpack('Q',size)[0]
	except Exception as err:
		raise Exception("You probably did something wrong. There is nothing like trying to find something where nothing exists.")
	if size+8 > getAvail(im):
		raise Exception("You probably did something wrong. There is nothing like trying to find something where nothing exists.")
	for i in range((size)):
		fp.write(g.next())
	
	fp.close()

def getAvail(im):
	bbox = im.getbbox()
	w = abs(bbox[2] - bbox[0])
	h = abs(bbox[3] - bbox[1])
	tot = int((w*h)*.375)
	return tot

def filePrep(fp, pg):
	''' Generator that yields the stream of data one bit at a time '''
	size = struct.pack('Q', os.fstat(fp.fileno()).st_size)
	for i in size:
		num = ord(i)
		if pg is not None:
			num = num^pg.next()
		
		for j in range(7,-1,-1):
			pos = 2**j
			bit = (num&pos)/pos
			yield bit
			
	for i in fp.read():
		num = ord(i)
		if pg is not None:
			num = num^pg.next()
		
		for j in range(7,-1,-1):
			pos = 2**j
			bit = (num&pos)/pos
			yield bit

def mergeData(im, fp, password=None):
	''' Generator that yields each pixel of the image,
	merging input data with the least significant bit of each color channel.
	'''
	g = iter(im.getdata())
	if password is not None:
		pg = passGen(password)
	else:
		pg = None
	f = filePrep(fp, pg)
	
	while True:
		try:
			pixel = list(g.next())
			for r in range(3):
				pixel[r] = (pixel[r]&254)|f.next()
			yield tuple(pixel)
		except StopIteration:
			yield tuple(pixel)
			break
	
	for i in g:
		yield i

def unmergeData(im, password=None):
	''' Generator yields each character of the hidden data after a full byte has been collected '''
	if password is not None:
		pg = passGen(password)
	else:
		pg = None
	g = iter(im.getdata())
	pq = deque()
	while True:
		out = 0
		for r in range(7,-1,-1):
			if not len(pq):
				pixel = g.next()
				for i in range(3):
					pq.append(1&pixel[i])
			out = out|((2**r)*pq.popleft())
		if pg is not None:
			out = out^pg.next()
			
		yield chr(out)

def passGen(password):
	''' Generator that yields eight bits of psudo random data at a time seeded with the supplied password '''
	random.seed(password)
	state = random.getstate()
	while True:
		random.setstate(state)
		out = random.getrandbits(8)
		state = random.getstate()
		yield out

if __name__ == "__main__":
    main()