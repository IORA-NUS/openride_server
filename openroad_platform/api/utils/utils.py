

def get_country_from_location(location):

    # if location is None:
    #     return "Singapore"
    # else:
    #     raise Exception("unknown Location")

    return "Singapore"


from datetime import datetime
from dateutil.relativedelta import relativedelta
def is_license_valid(driving_license, country):

    if driving_license.country == country and driving_license.expiry >= datetime.today().date() + relativedelta(months=6):
        return True
    else:
        return False


# from flask_jwt_extended import get_jwt, jwt_required
# from eve.utils import config

# @jwt_required()
# def add_user_on_insert(resource_name, items):
#     ''' '''
#     if config.DOMAIN[resource_name]['auto_add_user'] == True:
#         for item in items:
#             item['user'] = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]


from math import atan2,degrees

def get_angle(p1, p2):
    return degrees(atan2(p2[1]-p1[1], p2[0]-p1[0]))


from pyproj import Transformer

TRAN_4326_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")

def transform_lonlat_webmercator(lon, lat):
  return TRAN_4326_TO_3857.transform(lon, lat)

def itransform_lonlat_webmercator(lonlat_points):
#   return TRAN_4326_TO_3857.transform(lon, lat)
  return TRAN_4326_TO_3857.itransform(lonlat_points)

