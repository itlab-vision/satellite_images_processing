from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import io
import numpy as np
import imageio


def authentication():
    CLIENT_ID = "84af0729-85f1-4db8-9c46-2c16aea976a6"      # Insert your Client ID
    with open('utils/client_secret.txt') as f:
        CLIENT_SECRET = f.readline()  # Insert your Client Secret
    # set up credentials
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)

    # get an authentication token
    token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                          client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    return token, oauth


def build_request(bbox, time_interval, width, height):
    # evalscript
    evalscript = """
    //VERSION=3

    function setup() {
      return {
        input: ['B02',
                'B03',
                'B04',
                'B06',
                'B07',
              ],
        output: { id: 'default',
                  bands: 5,
                  sampleType: 'AUTO'}
      };
    }

    function evaluatePixel(sample) {
      return [
              sample.B02,
              sample.B03,
              sample.B04,
              sample.B06,
              sample.B07,
              ];
    }
    """

    # request body/payload
    json_request = {
        'input': {
            'bounds': {
                'bbox': bbox,
                'properties': {
                    'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
                }
            },
            'data': [
                {
                    'type': 'landsat-ot-l2',
                    'dataFilter': {
                        'timeRange': {
                            "from": time_interval[0],
                            "to": time_interval[1]
                        },
                        'mosaickingOrder': 'leastRecent',
                    },
                }
            ]
        },
        'output': {
            'width': width,
            'height': height,
            'responses': [
                {
                    'identifier': 'default',
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        'evalscript': evalscript
    }
    return json_request


def download(bbox, time_interval, width=256, height=256, rescale=False,):
    token, oauth = authentication()
    json_request = build_request(bbox, time_interval, width, height)
    # Set the request url and headers
    url_request = 'https://services-uswest2.sentinel-hub.com/api/v1/process'
    headers_request = {
        "Authorization": "Bearer %s" % token['access_token']
    }
    # Send the request
    response = oauth.request(
        "POST", url_request, headers=headers_request, json=json_request
    )
    print("status: {0}".format(response.status_code))
    if response.status_code != 200:
        print("request: {0}".format(json_request))
        print("reason: {0}".format(response.reason))
        raise Exception("response status code: {0}".format(response.status_code))

    x = imageio.imread(io.BytesIO(response.content))
    x = np.asarray(x).astype('float32')
    if rescale:
        x /= np.max(x)
    return x

