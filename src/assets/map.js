var map;
var marker_1;
var marker_2;
var num = 0;

function alert_markers() {
    alert("Use 2 markers to define area to analyze")
}

function initialize() {
    map = L.map('map').setView([56.29827, 43.98141], 16);

    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    }).addTo(map);

    new QWebChannel(qt.webChannelTransport, function (channel) {
        SatelliteApp = channel.objects.SatelliteApp;
        if (typeof SatelliteApp != 'undefined') {
            var onMapMove = function () { SatelliteApp.onMapMove(map.getCenter().lat, map.getCenter().lng) };
            var onMapClick = function (e) {
                SatelliteApp.addMarker(e.latlng.lat, e.latlng.lng, function (pyval) {
                    num = pyval;
                    if (num == 1) {
                        marker_1 = L.marker(e.latlng).addTo(map);
                    } else if (num == 2) {
                        marker_2 = L.marker(e.latlng).addTo(map);
                    } else {
                        alert("Too many markers");
                    }
                });
            }
            map.on('move', onMapMove);
            onMapMove();
            map.on('click', onMapClick)
        }
    });
}