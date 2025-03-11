import warnings
from datetime import datetime
from geopy import Nominatim
from timezonefinder import TimezoneFinder

from pytz import timezone, utc
import json
import numpy as np

from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

warnings.filterwarnings("ignore")
tf = TimezoneFinder()


def load_data():
    # load celestial data
    # de421 shows position of earth and sun in space
    eph = load('de421.bsp')

    # hipparcos dataset contains star location data
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    # And the constellation outlines come from Stellarium.  We make a list
    # of the stars at which each edge stars, and the star at which each edge
    # ends.

    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
           '/skycultures/modern_st/constellationship.fab')

    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)

    return eph, stars, constellations


def collect_celestial_data(location, when):
    # get latitude and longitude of our location
    # replace myGeocoder with your own unique name if ran into the permission error
    # see error details: https://stackoverflow.com/questions/51503389/geopy-exc-geocoderinsufficientprivileges-http-error-403-forbidden
    locator = Nominatim(user_agent='botstarmap')
    location = locator.geocode(location)
    lat, long = location.latitude, location.longitude
    # load celestial data
    eph, stars, constellations = load_data()
    # lat = 49.1460831
    # long = 0.2255168
    print(lat, long)

    # convert date string into datetime object
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')

    # define datetime and convert to utc based on our timezone
    timezone_str = tf.timezone_at(lat=lat, lng=long)
    local = timezone(timezone_str)

    # get UTC from local timezone and datetime
    local_dt = local.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(utc)

    # load celestial data
    # eph, stars, constellations = load_data()

    # find location of earth and sun and set the observer position
    sun = eph['sun']
    earth = eph['earth']
    # define observation time from our UTC datetime
    ts = load.timescale()
    t = ts.from_datetime(utc_dt)

    # define an observer using the world geodetic system data
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=long).at(t)

    # define the position in the sky where we will be looking
    position = observer.from_altaz(alt_degrees=60, az_degrees=0)
    # center the observation point in the middle of the sky
    ra, dec, distance = position.radec()
    center_object = Star(ra=ra, dec=dec)
    # find where our center object is relative to earth and build a projection with 180 degree view
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    # field_of_view_degrees = 180.0

    # calculate star positions and project them onto a plain space
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)

    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]

    return stars, edges_star1, edges_star2


def create_star_chart(location, when, chart_size, max_star_size, dry_constallations_line):
    stars, edges_star1, edges_star2 = collect_celestial_data(location, when)

    limiting_magnitude = 10

    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]

    marker_size = max_star_size * 10 ** (magnitude / -2.5)

    if dry_constallations_line is True:
        # Draw the constellation lines.
        xy1 = stars[['x', 'y']].loc[edges_star1].values
        xy2 = stars[['x', 'y']].loc[edges_star2].values
        lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)

    when_datetime = datetime.strptime(when, '%Y-%m-%d %H:%M')

    stars = stars.drop(['ra_degrees', 'dec_degrees',
                        'parallax_mas', 'ra_hours', 'epoch_year', 'parallax_mas', 'ra_mas_per_year', 'dec_mas_per_year', 'ra_hours', 'epoch_year', 'parallax_mas'], axis=1)
    data = {}
    data["stars"] = json.loads(stars.to_json(orient='records'))

    # data["lines"] = lines_xy.tolist()
    return data


# call the function above


LOCATION = 'Québec, CA'
WHEN = '2022-03-23 05:14'
CHART_SIZE = 12
MAX_STAR_SIZE = 300
DRY_CONSTELLATIONS_LINE = True

data = create_star_chart(location=LOCATION, when=WHEN, chart_size=CHART_SIZE,
                         max_star_size=MAX_STAR_SIZE, dry_constallations_line=DRY_CONSTELLATIONS_LINE)


print(data["stars"][0])
