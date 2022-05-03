from flask import render_template
from flask import request
from app import app
from datetime import date
from sentinelhub import SHConfig
from models.kumar_roy import KumarRoy64_10
from models.cloud_net import CloudNet
from sentinel_downloader import download
import tifffile as tiff

config = SHConfig()
# TODO use openvino
fire = KumarRoy64_10('C://Users//Никита//Desktop//fire//model.h5')
cloud = CloudNet('C://Users//Никита//Desktop//cloud//model.h5')

# генерация главной страницы

@app.route('/')
def main():
    today = date.today()
    return render_template("index.html", today=today.strftime("%Y-%m-%d"))

# сюда будут приходить http запросы, генерируемые javascript скриптами

@app.route('/analyze/', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    marker_1 = (min(data['marker_1'][0], data['marker_2'][0]), min(data['marker_1'][1], data['marker_2'][1]))
    marker_2 = (max(data['marker_1'][0], data['marker_2'][0]), max(data['marker_1'][1], data['marker_2'][1]))
    start_date = data['start_date']
    end_date = data['end_date']
    # download
    data_path = download(bbox=(marker_1[0], marker_1[1], marker_2[0], marker_2[1]), resolution=60, start=start_date, end=end_date)
    # process
    image = tiff.imread(data_path + 'response.tiff')
    fire_res = fire.process(image)
    cloud_res = cloud.process(image)
    # calculate statistic & save statistic to database
    # return data={'source_image': image, 'fire_image': fire_res, 'cloud_image': cloud_res}
    # debug
    print(data)
    return "analyze completed successfully"


@app.route('/show/', methods=['POST'])
def show():
    pass
