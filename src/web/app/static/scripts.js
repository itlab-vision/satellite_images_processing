var marker_1;
var marker_2;
var num = 0;
var map;

function onMapClick(e) {
    if (num == 0) {
        marker_1 = L.marker(e.latlng).addTo(map);
        num = 1;
    } else if (num == 1) {
        marker_2 = L.marker(e.latlng).addTo(map);
        num = 2;
    } else {
        alert("Too many markers");
    }
}

function createMap() {

    var mapOptions = {
        center: [56.29827, 43.98141],
        zoom: 10
    }

    map = new L.map('map', mapOptions);

    var layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');

    map.addLayer(layer);

    map.on('click', onMapClick)
}

function clearMarker() {
    if (num == 2) {
        num = 1;
        map.removeLayer(marker_2);
    }
    else if (num == 1) {
        num = 0;
        map.removeLayer(marker_1);
    }
}

function analyze(date) {
    if (num != 2) {
        alert("Use 2 markers to define area to analyze")
    }
    else {
        $.ajax({
            url: "/analyze/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ 'marker_1': [marker_1.getLatLng().lat, marker_1.getLatLng().lng], 'marker_2': [marker_2.getLatLng().lat, marker_2.getLatLng().lng], 'date': date }),
            success: function (data) {
                // for debug
                alert(data);
                // for release
                /*
                var py_image = data['image'] // will be result of model  
                var width = data['image'].shape[1],
                    height = data['image'].shape[0],
                    buffer = new Uint8ClampedArray(width * height * 4); // have enough bytes
                // The * 4 at the end represent RGBA which we need to be compatible with canvas.

                // Fill the buffer with some data, for example:
                for(var y = 0; y < height; y++) {
                    for(var x = 0; x < width; x++) {
                        var pos = (y * width + x) * 4; // position in buffer based on x and y
                        buffer[pos] = py_image[y][x];
                        buffer[pos+1] = py_image[y][x];
                        buffer[pos+2] = py_image[y][x];
                        buffer[pos+3] = 255;           // set alpha channel
                    }
                }

                // When filled use the buffer as source for canvas:
                // create off-screen canvas element
                var canvas = document.createElement('canvas'),
                    ctx = canvas.getContext('2d');

                canvas.width = width;
                canvas.height = height;

                // create imageData object
                var idata = ctx.createImageData(width, height);

                // set our buffer as source
                idata.data.set(buffer);

                // update canvas with new data
                ctx.putImageData(idata, 0, 0);

                // Now the data in your custom array is copied to the canvas buffer. Next step is to create an image file:
                var dataUri = canvas.toDataURL(); // produces a PNG file

                // Now you can use the data-uri as source for an image:
                document.getElementById('res').src = dataUri
                */
            },
        });
    }
}

// наверно для выбора статистики (зависит от реализации)
function select(stat) {

}

