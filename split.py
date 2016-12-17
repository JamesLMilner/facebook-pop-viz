import urllib2
import os
import zipfile
import sys
import traceback
from osgeo import gdal, osr
from fractions import gcd
import math

def split_quarters(file_name):
    raw_file_name = os.path.splitext(os.path.basename(file_name))[0]
    driver = gdal.GetDriverByName('GTiff')
    dataset = gdal.Open(file_name)
    band = dataset.GetRasterBand(1)

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    print "Columns: ", cols
    print "Rows: ", rows

    width = cols
    height = rows
    tilesize = min(width, height) / 2

    k = 0
    for i in range(0, width, tilesize):
        for j in range(0, height, tilesize):
            k += 1
            gdaltranString = "gdal_translate -of GTIFF -srcwin "+str(i)+", "+str(j)+", "+str(tilesize)+", " \
                +str(tilesize)+ " " + filename + " data/" + raw_file_name + "_" + str(k) + ".tif"
            os.system(gdaltranString)


if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input file not specified"
        else:
            filename = str(sys.argv[1])
            split_quarters(filename)
            print "...Done!"

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()
