import sys
import os
import argparse
import tarfile
import numpy as np
from landsatxplore.errors import EarthExplorerError
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer


def build_argparser():
    parser = argparse.ArgumentParser(
        description='Landsas-8 downloader', add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                      help='Show this help message and exit.')
    args.add_argument('-u', '--username', type=str, required=True,
                      help='Required. Your username from https://ers.cr.usgs.gov.')
    args.add_argument('-p', '--password', type=str, required=True,
                      help='Required. Your password from https://ers.cr.usgs.gov.')
    args.add_argument('-lat', '--latitude', type=float, required=False,
                      help='Latitude of a point to observe.')
    args.add_argument('-lon', '--longitude', type=float, required=False,
                      help='Longitude of a point to observe.')
    args.add_argument('-b', '--bbox', type=str, required=False,
                      help='Area to observe in format "(xmin ymin xmax ymax)" where "x" - lattitude, "y" - longitude')
    args.add_argument('-s', '--start', type=str, required=False,
                      help='Start date in format YYYY-MM-DD.')
    args.add_argument('-e', '--end', type=str, required=False,
                      help='End date in format YYYY-MM-DD.')
    args.add_argument('-c', '--cloud', type=float, required=False,
                      help='Max cloud cover in percent.')
    args.add_argument('-m', '--max', type=int, required=False,
                      help='Max number of results.')
    args.add_argument('-d', '--download', type=bool, required=False,
                      help='Flag to download. Default False')
    args.add_argument('-i', '--images', type=str, required=False,
                      help='List of specific images to download. Example: LC08_L1TP_169024_20210301_20210311_01_T2 LC08_L1TP_168025_20210105_20210309_01_T2')
    return parser


def main():

    args = build_argparser().parse_args()

    # Initialize a new API instance and get an access key
    username = args.username
    password = args.password
    api = API(username, password)
    ee = EarthExplorer(username, password)

    if args.images:
        scenes = args.images.split()
        download = True
    else:
        # Search for Landsat TM scenes
        download = args.download
        lat = args.latitude
        lon = args.longitude
        bbox = args.bbox
        if bbox:
            bbox = bbox[1:-1].split()
            bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        start = args.start
        end = args.end
        cloud = args.cloud
        if not cloud:
            cloud = 10
        max_res = args.max
        if not max_res:
            max_res = 100

        scenes = api.search(
            dataset='landsat_8_c1',
            latitude=lat,
            longitude=lon,
            bbox=bbox,
            start_date=start,
            end_date=end,
            max_cloud_cover=cloud,
            max_results=max_res
        )
        temp = []
        print(f"{len(scenes)} scenes found from dataset landsat_8_c1.")
        for scene in scenes:
            print(scene['display_id'])
            temp.append(scene['display_id'])
        scenes=temp

    # Download scenes
    if download == True:
        scenes_path = os.path.abspath("")+'\\landsat_downloaded\\zips\\'
        for scene in scenes:
            try:
                ee.download(identifier=scene, output_dir=scenes_path, dataset='landsat_8_c1')
                tar = tarfile.open(scenes_path+scene+'.tar.gz', 'r')
                tar.extractall(path=scenes_path[:-5]+scene)
            except EarthExplorerError as e:
                print(e, end='')
                print(' for ' + scene + ' from dataset landsat_8_c1')

    # Exit
    ee.logout()
    api.logout()


if __name__ == '__main__':
    sys.exit(main() or 0)
