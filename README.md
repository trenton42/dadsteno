dadsteno
========

(yet another) Down and dirty stenography tool

This simple tool takes a PNG image and a file and combines them. The changes to the image are most likely invisible to 
the naked eye, however careful analysis (especially on images with low entropy) could reveal your data. You can optionally
XOR encrypt your data with a psudo random stream seeded with the passphrase you supply (using the -p switch).

## Usage
```
$ dadsteno.py [-h] -f FILE -i IMAGE [-d [DECRYPT]] [-p [PASSWORD]]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File to hide
  -i IMAGE, --image IMAGE
                        Image file. *Will be overwritten!
  -d [DECRYPT], --decrypt [DECRYPT]
  -p [PASSWORD], --password [PASSWORD]
```

## Examples
```
$ python dadsteno.py -i someimage.png -f somefile.txt
```

The contents of somefile.txt are merged into someimage.png. To get the data back:
```
$ python dadsteno.py -i someimage.png -f some_new_file.txt -d
```

This will extract the data from someimage.png placing it in some_new_file.txt. Note that no meta info (file name, file 
type, etc.) are stored in the image, so it is up to you figure out what was saved in the image.