
// кнопка анализа берет маркеры с карты и дату с селектора
function analyze(marker_1, marker_2, date) {
    $.ajax({
        url: "/analyze/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({'marker_1': marker_1, 'marker_2': marker_2, 'date': date}),
        // for debug
        success: function (data) {
            alert(data);
        },
    });
}

// наверно для выбора статистики (зависит от реализации)
function select(stat) {
    
}
