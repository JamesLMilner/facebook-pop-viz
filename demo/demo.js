
    console.log("Starting script");
    //var url = "/data/hrsl_mwi_downsample.tif";

    var METADATA = "/data/hrsl_mwi/metadata.json";
    var loadedRasters = [];

    var projection = ol.proj.get('EPSG:4326');

    var date = new Date().getFullYear();
    var attribution = new ol.Attribution({
        html: 'Tiles &copy; <a href="http://services.arcgisonline.com/ArcGIS/' +
            'rest/servicesWorld_Light_Gray_Base/MapServer">Esri ' +date + '</a>'
    });
    var mapLayers = [
        new ol.layer.Tile({
            source: new ol.source.XYZ({
            attributions: [attribution],
            url: 'http://server.arcgisonline.com/ArcGIS/rest/services/' +
                '/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}'
            }),
            opacity: 1
        }),
        new ol.layer.Tile({
            source: new ol.source.XYZ({
            attributions: [attribution],
            url: 'http://server.arcgisonline.com/ArcGIS/rest/services/' +
                '/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
            }),
            opacity: 0.4
        })
    ];

    var zIndex = 3
    mapLayers.forEach(function(layer){
        layer.setZIndex(zIndex--);
    });

    var map = new ol.Map({
        target: document.getElementById("map"),
        controls: ol.control.defaults().extend([new ol.control.ZoomSlider()]),
        layers: mapLayers,
        view: new ol.View({
            center: [0,0],
            projection: projection,
            zoom: 7
        })
    });

    loadRasters(METADATA);

    function combinedCoord(tile, dim) {
        return parseFloat(tile["min" + dim]) +
               parseFloat(tile["max" + dim]);
    }

    function loadRasters() {
        fetch(METADATA)
        .then(function(response){
            return response.json();
        })
        .then(function(json){

            var centerX = 0;
            var centerY = 0
            var count = 0;
            var minX = Infinity;
            var maxX = -Infinity;
            var minY = Infinity;
            var maxY = -Infinity;
            var urls = [];

            for (var key in json){

                var tile = json[key];
                var url = "/"+tile["path"];

                if (tile["minY"] < minY) { minY = parseFloat(tile["minY"])}
                if (tile["minX"] < minX) { minX = parseFloat(tile["minX"])}
                if (tile["maxX"] > maxX) { maxX = parseFloat(tile["maxX"])}
                if (tile["maxY"] > maxY) { maxY = parseFloat(tile["maxY"])}

                centerX += combinedCoord(tile, "X");
                centerY += combinedCoord(tile, "Y");
                count += 2
                urls.push(url);

            }

            centerX = centerX/count;
            centerY = centerY/count;
            console.debug(centerX, centerY);

            map.getView().setCenter([centerX, centerY]);
            map.addControl(new ol.control.ZoomToExtent({
                extent: [minX, minY, maxX, maxY]
            }));

            var promises = [];
            urls.forEach(function() {
                promises.push(loadRaster(url));
            });

            Promise.all(promises).then(function(values){
                console.log("All promises resolved", values);
                loadedRasters = values;
                if (loadedRasters.length > 0) {

                    console.log(plotty.colorscales);
                    var select = document.createElement("select");

                    function onChange() {
                        var selectedValue = select.options[select.selectedIndex].value;
                        loadedRasters.forEach(function(tiff){
                            addRaster(tiff, selectedValue);
                        })    
                    }


                    for(var color in plotty.colorscales) {
                        var option = document.createElement('option');
                        option.text = option.value = color;
                        select.add(option, 0);
                    }

                    select.addEventListener("change", onChange);

                    select.className = "color-select";
                    document.body.appendChild(select);
                }
            });

         });
    }

    function loadRaster(url) {
        return new Promise(function(resolve, reject){

            fetch(url)
            .then(function(response){
                return response.arrayBuffer();
            })
            .then(function(arraybuffer){

                console.debug("Loading GeoTIFF..." + url);
                var tiff = GeoTIFF.parse(arraybuffer);

                addRaster(tiff, "copper");

                resolve(tiff);

            }).catch(function(error){
                reject(error);
            });;

        })

    } // End of loadRaster

    function addRaster(tiff, colorScale) {

        var image = tiff.getImage();
        var metadata = image.getGDALMetadata();

        var extent = [
            metadata.minX, metadata.minY,
            metadata.maxX, metadata.maxY
        ]  // e.g. [15.05, 47.75, 15.40, 47.95]

        console.debug(extent);


        image.readRasters({}, function(rasters) {

            var raster = rasters[0];

            var canvas = document.createElement("canvas");
            canvas.getContext("webgl").fillStyle = 'rgba(255, 255, 255, 0)';

            var plot = new plotty.plot({
                canvas: canvas,
                data: raster,
                width: image.getWidth(),
                height: image.getHeight(),
                domain: [0, 12],
                colorScale: colorScale
            });
            plot.setClamp(true,true);
            plot.setNoDataValue(0);
            plot.render();

            var rasterLayer = new ol.layer.Image({
                source: new ol.source.ImageStatic({
                    url: canvas.toDataURL("image/png"),
                    imageExtent: extent
                }),
                opacity: 1
            })
            map.addLayer(rasterLayer);
        });

    }