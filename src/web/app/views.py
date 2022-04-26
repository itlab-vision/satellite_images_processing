from flask import render_template
from flask import request
from app import app
from datetime import date

# генерация главной страницы

@app.route('/')
def main():
    today = date.today()
    return render_template("index.html", today=today.strftime("%Y-%m-%d"))

# сюда будут приходить http запросы, генерируемые javascript скриптами

@app.route('/analyze/', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    marker_1 = (data['marker_1'][0], data['marker_1'][1])
    marker_2 = (data['marker_2'][0], data['marker_2'][1])
    date = data['date']
    # find, download, process,
    # calculate statistic & save statistic to database
    print(marker_1, marker_2, date)
    # debug
    return "analyze completed successfully"


@app.route('/show/', methods=['POST'])
def show():
    pass
