from skyfield.api import Star, load, wgs84
import numpy as np
from skyfield.data import hipparcos, stellarium
from skyfield.api import N, W, wgs84
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from skyfield.projections import build_stereographic_projection
from skyfield.named_stars import named_star_dict
import pandas as pd

hip_to_name = {v: k for k, v in named_star_dict.items()}

def get_star_name(hip):
    return hip_to_name.get(hip, f"HIP{hip}")

def get_stars_dataframe(magnitude):
        # hipparcos dataset contains star location data
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
        stars = stars[stars['magnitude'] <= magnitude]
        stars["name"] = stars.index.map(get_star_name)
    return stars




def get_constellations():
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
        '/skycultures/modern_st/constellationship.fab')

    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    return constellations

def calculate_alt_az(row, observer):
    star = Star.from_dataframe(row)
    astro = observer.observe(star)
    app = astro.apparent()
    alt, az, distance = app.altaz()

    return pd.Series([alt.degrees, az.degrees, distance], index=['alt', 'az', 'distance'])

def main():
    field_of_view_degrees = 180.0
    # 0 = North  180 = South
    degree = 0
    limiting_magnitude = 4

    eph = load('de421.bsp')
    sun = eph['sun']
    mars = eph['mars']
    earth = eph['earth']



    ts = load.timescale()
    t = ts.now() 
    

    # define an observer using the world geodetic system data
    location = earth + wgs84.latlon(latitude_degrees=46.774294 * N, longitude_degrees=71.297663 * W)
    observer = location.at(t)
    stars = get_stars_dataframe(limiting_magnitude)


    stars[['alt', 'az', 'distance']] = stars.apply(calculate_alt_az, axis=1, observer=observer)


    # define the position in the sky where we will be looking
    position = observer.from_altaz(alt_degrees=25, az_degrees=0)
    # center the observation point in the middle of the sky
    ra, dec, distance = position.radec()
    center_object = Star(ra=ra, dec=dec)
    # find where our center object is relative to earth and build a projection with 180 degree view
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)
    # print(stars.head())

   
    # # Créer un DataFrame Pandas
    # df = pd.DataFrame(star_data)

    # # Enregistrer dans un fichier CSV
    stars.to_csv('./stars.csv', index=False)

    print("Fichier CSV généré avec succès !")


    # # Compute sphereical projection to stereographic (on a flat circle)
    # projection = build_stereographic_projection(center)
    # stars['x'], stars['y'] = projection(star_positions)

    # Create a True/False mask marking the stars bright enough to be
    # included in our plot.  And go ahead and compute how large their
    # markers will be on the plot.

    # bright_stars = (stars.magnitude <= limiting_magnitude)
    # magnitude = stars['magnitude'][bright_stars]
    # marker_size = (0.5 + limiting_magnitude - magnitude) ** 2.0


    # # CONSTELLATIONS
    # constellations = get_constellations()
    # edges = [edge for name, edges in constellations for edge in edges]
    # edges_star1 = [star1 for star1, star2 in edges]
    # edges_star2 = [star2 for star1, star2 in edges]
    # # The constellation lines will each begin at the x,y of one star and end
    # # at the x,y of another.  We have to "rollaxis" the resulting coordinate
    # # array into the shape that matplotlib expects.

    # xy1 = stars[['x', 'y']].loc[edges_star1].values
    # xy2 = stars[['x', 'y']].loc[edges_star2].values
    # lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)



main()