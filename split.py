import os
import sys
import traceback
import json
from osgeo import gdal, osr

OUTPUT_FOLDER = "data"

def write_metadata_json(path, metadata):

    with open(os.path.join(OUTPUT_FOLDER, path, 'metadata.json'), 'w') as outfile:
        json.dump(metadata, outfile, indent=4, sort_keys=True)


def get_extent(dataset):

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    transform = dataset.GetGeoTransform()
    minx = transform[0]
    maxx = transform[0] + cols * transform[1] + rows * transform[2]

    miny = transform[3] + cols * transform[4] + rows * transform[5]
    maxy = transform[3]

    return {
        "minX": str(minx), "maxX": str(maxx),
        "minY": str(miny), "maxY": str(maxy),
        "cols": str(cols), "rows": str(rows)
    }

def create_tiles(minx, miny, maxx, maxy, n):

    width = maxx - minx
    height = maxy - miny

    matrix = []

    for j in range(n, 0, -1):
        for i in range(0, n):

            ulx = minx + (width/n) * i # 10/5 * 1
            uly = miny + (height/n) * j # 10/5 * 1

            lrx = minx + (width/n) * (i + 1)
            lry = miny + (height/n) * (j - 1)
            matrix.append([[ulx, uly], [lrx, lry]])

    return matrix


def split(file_name, n):

    print "Splitting ", file_name, "into ", n, " pieces"
    raw_file_name = os.path.splitext(os.path.basename(file_name))[0].replace("_downsample", "")
    driver = gdal.GetDriverByName('GTiff')
    dataset = gdal.Open(file_name)
    band = dataset.GetRasterBand(1)
    transform = dataset.GetGeoTransform()

    extent = get_extent(dataset)

    cols = int(extent["cols"])
    rows = int(extent["rows"])

    print "Columns: ", cols
    print "Rows: ", rows

    minx = float(extent["minX"])
    maxx = float(extent["maxX"])
    miny = float(extent["minY"])
    maxy = float(extent["maxY"])

    # width = maxx - minx
    # height = maxy - miny

    output_path = os.path.join(OUTPUT_FOLDER, raw_file_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # print "GCD", gcd(round(width, 0), round(height, 0))
    # print "Width", width
    # print "height", height

    tiles = create_tiles(minx, miny, maxx, maxy, n)
    transform = dataset.GetGeoTransform()
    x_origin = transform[0]
    y_origin = transform[3]
    pixel_width = transform[1]
    pixel_height = -transform[5]

    print x_origin, y_origin

    tile_num = 0
    metadata = {}
    for tile in tiles:

        minx = tile[0][0]
        maxx = tile[1][0]
        miny = tile[1][1]
        maxy = tile[0][1]

        p1 = (minx, maxy)
        p2 = (maxx, miny)

        i1 = int((p1[0] - x_origin) / pixel_width)
        j1 = int((y_origin - p1[1])  / pixel_height)
        i2 = int((p2[0] - x_origin) / pixel_width)
        j2 = int((y_origin - p2[1]) / pixel_height)

        print i1, j1
        print i2, j2

        new_cols = i2-i1
        new_rows = j2-j1

        data = band.ReadAsArray(i1, j1, new_cols, new_rows)

        #print data

        new_x = x_origin + i1*pixel_width
        new_y = y_origin - j1*pixel_height

        print new_x, new_y

        new_transform = (new_x, transform[1], transform[2], new_y, transform[4], transform[5])

        output_file_base = raw_file_name + "_" + str(tile_num) + ".tif"
        output_file = os.path.join(OUTPUT_FOLDER, raw_file_name, output_file_base)

        tile_dataset = driver.Create(
            output_file,
            new_cols,
            new_rows,
            1,
            gdal.GDT_Float32
        )

        # Writing output raster
        tile_dataset.GetRasterBand(1).WriteArray(data)

        # Setting extension of output raster
        # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
        tile_dataset.SetGeoTransform(new_transform)

        wkt = dataset.GetProjection()

        # Setting spatial reference of output raster
        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)
        export_prj = srs.ExportToWkt()
        tile_dataset.SetProjection(export_prj)

        # Set file-level metadata
        tile_extent = get_extent(tile_dataset)
  
        tile_dataset.SetMetadata(tile_extent)
        print "Metadata set: ", tile_dataset.GetMetadata()

        # Close output raster dataset
        tile_dataset = None

        # Set our metadata info for this tile
        metadata[tile_num] = tile_extent
        metadata[tile_num]["fileSize"] = os.path.getsize(output_file)
        metadata[tile_num]["path"] = output_file

        tile_num += 1

    write_metadata_json(raw_file_name, metadata)
    dataset = None

if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input file not specified"
        else:
            filename = str(sys.argv[1])
            if len(sys.argv) == 3:
                n = int(sys.argv[2])
            else:
                n = 3

            split(filename, n)
            print "...Done!"

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()
