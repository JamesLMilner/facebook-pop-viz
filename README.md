# Facebook Population Data Viz

Experimenting with visualsing Facebooks population dataset in the web.

# The Data
High Resolution Settlement Layer

Data is available from:
https://ciesin.columbia.edu/data/hrsl/#maps

Data is licensed Creative Commons Attribution 4.0 International License.

# Setup

## Download the Data

You can download the data manually or use the convinence script provided as such:

    python download.py https://ciesin.columbia.edu/data/hrsl/hrsl_gha_v1.zip

This will download and unzip the files to a folder entitled 'rawdata'

## Prequistes for Python Scripts

  * GDAL
  * GDAL Python bindings

## Process the Data

Process the data as such:

    python process.py rawdata/hrsl_gha/hrsl_gha.tif

The data will now be in the 'data' folder.

## Viewing the Data

We can use a web browser to examine the data. To setup the project install node.js and npm. You can then do:

    cd src
    npm install

To get a hot reloading web server that will display the data you can run:

    npm install -g live-server
    live-server

 You just have to change the url variable in the index.html file to the appropriate tif file:


```javascript
var url = "/data/hrsl_mwi_downsample.tif";
```


# Software License
The MIT License (MIT)

Copyright (c) 2016 James Milner
