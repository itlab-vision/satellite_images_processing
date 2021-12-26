from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

# your username & password from https://ers.cr.usgs.gov
username = 'Igniel2'
password = 'VasyaPupkin228'

# Initialize a new API instance and get an access key
api = API(username, password)
ee = EarthExplorer(username, password)

# Search for Landsat TM scenes
scenes = api.search(
    dataset='landsat_8_c1',
    latitude=50.85, # center
    longitude=50.35,
    bbox=(50.65, 50.15, 51.05, 50.55), # +- 0.2 
    start_date='2021-01-01',
    end_date='2021-03-01',
    max_cloud_cover=10
)

print(f"{len(scenes)} scenes found.")

# Process the result
for scene in scenes:
    print(scene['display_id'])

ee.download(identifier=scenes[0]['display_id'], output_dir='./downloaded')

# собрать каналы из архива в единое tif и вывести на экран

ee.logout()
api.logout()