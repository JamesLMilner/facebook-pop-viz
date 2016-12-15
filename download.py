import urllib2
import os
import zipfile
import sys
import traceback


DATA_FOLDER = "rawdata"

def download(input_url):

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    file_name = os.path.join(DATA_FOLDER, url.split('/')[-1])
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

    return file_name


def unzip(zip_file):
    zfile = zipfile.ZipFile(zip_file)
    for name in zfile.namelist():
      (dirname, filename) = os.path.split(name)
      print "Decompressing " + filename + " on " + DATA_FOLDER
      if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
      zfile.extract(name, DATA_FOLDER)

if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input file not specified"
        else:
            url = str(sys.argv[1])
            file_name = download(url)
            unzip(file_name)
            print "...Done!"

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()
