import os
import sys
import argparse
from shapely.geometry import shape, Polygon, MultiPolygon, MultiLineString
import numpy as np
from sentinelhub import (
    BBoxSplitter,
    SHConfig,
    MimeType,
    CRS,
    BBox,
    SentinelHubRequest,
    DataCollection,
    bbox_to_dimensions,
    read_data
)


def build_argparser():
    parser = argparse.ArgumentParser(
        description='Sentinel-2 downloader', add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                      help='Show this help message and exit.')
    args.add_argument('-i', '--id', type=str, required=False,
                      help='Your sh_client_id from OAuth client profile on page https://apps.sentinel-hub.com/dashboard/#/account/settings.')
    args.add_argument('-s', '--secret', type=str, required=False,
                      help='Your sh_client_secret from OAuth client profile on page https://apps.sentinel-hub.com/dashboard/#/account/settings.')
    args.add_argument('-b', '--bbox', type=str, required=False,
                      help='Area to observe in format "x1 y1 x2 y2" where "x1" and "y1" - lower left longitude and lattitude, "x2" and "y2" - upper right longitude and lattitude')
    args.add_argument('-lb', '--largebbox', type=str, required=False,
                      help='Path to file with coordinates of area to observe')
    args.add_argument('-sd', '--start', type=str, required=True,
                      help='Start date in format YYYY-MM-DD.')
    args.add_argument('-e', '--end', type=str, required=True,
                      help='End date in format YYYY-MM-DD.')
    args.add_argument('-r', '--resolution', type=float, required=True,
                      help='Pixel resolution (in meters).')
    args.add_argument('-n', '--name', type=str, required=False,
                      help='Name of folder')
    return parser

def download(bbox, resolution, start, end, config, name = None):
    size = bbox_to_dimensions(bbox, resolution=resolution)

    print(f"Image shape at {resolution} m resolution: {size} pixels")

    evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                }],
                output: {
                    bands: 13,
                    sampleType: "FLOAT32"
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B01,
                    sample.B02,
                    sample.B03,
                    sample.B04,
                    sample.B05,
                    sample.B06,
                    sample.B07,
                    sample.B08,
                    sample.B8A,
                    sample.B09,
                    sample.B10,
                    sample.B11,
                    sample.B12];
        }
    """
    if name:
        data_folder = os.path.join(os.path.join(os.path.abspath(""), 'sentinel_downloaded'), name)
    else:
        data_folder = os.path.join(os.path.abspath(""), 'sentinel_downloaded')
    request = SentinelHubRequest(
        data_folder=data_folder,
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                # TODO check others collections
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=(start, end),
                mosaicking_order="leastCC",
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],

        bbox=bbox,
        size=size,
        config=config,
    )
    request.save_data()
    return os.path.join(data_folder, request.get_filename_list()[0])
    # Debug
    # import numpy as np
    # import matplotlib.pyplot as plt
    # img = request.get_data()[0]
    # plt.imshow(np.concatenate(
    #     (img[:, :, 3:4]*3.5/255, img[:, :, 2:3]*3.5/255, img[:, :, 1:2]*3.5/255), axis=2))
    # plt.show()

def main():

    args = build_argparser().parse_args()

    config = SHConfig()

    if not args.id or not args.secret:
        if not config.sh_client_id or not config.sh_client_secret:
            print('Please configure your sh_client_id and sh_client_secret to enable downloading requests')
            print('You can do this by editing config.json file of sentinelhub or by passing --id and --secret arguments just once')
            return
    else:
        config.sh_client_id = args.id
        config.sh_client_secret = args.secret
        config.save()

    if args.bbox:
        bbox = args.bbox
        bbox = bbox.split()
        bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        bbox = BBox(bbox=bbox, crs=CRS.WGS84)
        download(bbox, args.resolution, args.start, args.end, config)
        
    else:
        geo_json = read_data(args.largebbox)
        area = shape(geo_json["features"][0]["geometry"])
        bbox_splitter = BBoxSplitter(
            [area], CRS.WGS84, (5, 4), reduce_bbox_sizes=True
        )
        bboxs = bbox_splitter.get_bbox_list()
        for bbox in bboxs:
            if (args.name):
                download(bbox, args.resolution, args.start, args.end, config, args.name)
            else:
                download(bbox, args.resolution, args.start, args.end, config)

if __name__ == '__main__':
    sys.exit(main() or 0)
