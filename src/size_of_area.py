from pyproj import Geod
from shapely.geometry import shape, Polygon
from shapely.ops import orient
from sentinelhub import read_data
from area import area
import sys
import argparse

def size_of_area(area):
    geod = Geod(ellps="WGS84")
    poly_area, poly_perimeter = geod.geometry_area_perimeter(orient(area))
    return poly_area

def main():
    parser = argparse.ArgumentParser(
        description='Size calculator', add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-a', '--area', type=str, required=True)
    geo_json = read_data(parser.parse_args().area)
    area = shape(geo_json["features"][0]["geometry"])
    print(size_of_area(area))
    
if __name__ == '__main__':
    sys.exit(main() or 0)