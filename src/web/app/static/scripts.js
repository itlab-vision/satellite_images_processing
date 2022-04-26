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

// кнопка анализа берет маркеры с карты и дату с селектора
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
            // for debug
            success: function (data) {
                alert(data);
            },
        });
    }
}

// наверно для выбора статистики (зависит от реализации)
function select(stat) {

}

