from osgeo import gdal, ogr
from os import remove, getcwd
from os.path import isfile, join, basename
import sys
import numpy as np
import traceback
from shutil import copyfile

# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()

def single_band( input_file, output_file ):

    ds = gdal.Open(input_file)
    band = ds.GetRasterBand(1)

    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    xsize = band.XSize
    ysize = band.YSize

    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create(output_file, xsize, ysize, 1, gdal.GDT_Byte )
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(ds.GetProjection())
    band = dst_ds.GetRasterBand(1)
    array = band.ReadAsArray(0,0,xsize,ysize).astype(np.float32)
    band.WriteArray(array)
    dst_ds = None
    return output_file

def downsample_output (input_file, downsample):
    ds_in = gdal.Open(input_file)
    drv = gdal.GetDriverByName( "GTiff" )

    output_file = input_tif.replace(".tif", "") + "_downsample.tif"

    band = ds_in.GetRasterBand(1)
    high_res = band.ReadAsArray(0,0,ds_in.RasterXSize, ds_in.RasterYSize).astype(np.float32)
    random_prefix = ds_in.RasterCount

    # Check for a temporary file
    random_prefix = 0
    while isfile(str(random_prefix) + "_temp.tif") == True:
        random_prefix += 1
    temp_file = str(random_prefix) + "_temp.tif"
    print "Making temporary file " + temp_file + "..."

    ds_out = drv.Create(temp_file, ds_in.RasterXSize, ds_in.RasterYSize, 1, gdal.GDT_Byte )
    ds_out.SetGeoTransform( ds_in.GetGeoTransform())
    ds_out.SetProjection ( ds_in.GetProjectionRef() )
    ds_out.GetRasterBand(1).WriteArray ( high_res )

    geoTransform = ds_in.GetGeoTransform()
    drv = gdal.GetDriverByName( "GTiff" )
    resampled = drv.Create( output_file , ds_in.RasterXSize/downsample, ds_in.RasterYSize/downsample, 1, gdal.GDT_Byte )
    transform = ( geoTransform[0], geoTransform[1]*downsample, geoTransform[2], geoTransform[3],geoTransform[4], geoTransform[5]*downsample )
    resampled.SetGeoTransform( transform )
    resampled.SetProjection ( ds_in.GetProjectionRef() )


    # We can set some meta data for use in the client
    transform = resampled.GetGeoTransform()
    width = resampled.RasterXSize
    height = resampled.RasterYSize

    minx = transform[0]
    maxx = transform[0] + width * transform[1] + height * transform[2]

    miny = transform[3] + width * transform[4] + height * transform[5]
    maxy = transform[3]

    resampled.SetMetadata({
        "minX": str(minx), "maxX": str(maxx),
        "minY": str(miny), "maxY": str(maxy)
    })

    print "Extent: "
    print "Min X", str(minx)
    print "Min Y", str(miny)
    print "Max X", str(maxx)
    print "Max Y", str(maxy)

    gdal.RegenerateOverviews ( ds_out.GetRasterBand(1), [ resampled.GetRasterBand(1) ], 'mode' )

    resampled.GetRasterBand(1).SetNoDataValue ( 0 )
    resampled = None
    ds_out = None
    ds_in = None
    print "Removing temporary file " + temp_file + "..."
    try:
        remove(temp_file)
    except OSError:
        pass

    return output_file


if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input file not specified"
        else:
            input_tif = str(sys.argv[1])
            print "Resampling", input_tif
            
            try:
                oneband = input_tif.replace(".tif", "") + "_oneband.tif"
                single_band(input_tif, oneband)
            except MemoryError:
                print "Raster was too large to to put into memory during extract to single band"
            
            if len(sys.argv) != 3:
                downsample = 5
            else:
                downsample = int(sys.argv[2])

            try:                    
                output_file = downsample_output(input_tif,  downsample)
                copyfile(output_file, join(getcwd(), "data", basename(output_file)))
                print "...Done!"
            except MemoryError:
                print "Raster was too large to put into memory during resampling"    
           

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()
