from datetime import datetime
from pytz import timezone
from starplot import MapPlot, HorizonPlot, Projection, Star, DSO, _
from starplot.styles import PlotStyle, extensions
from timezonefinder import TimezoneFinder 
import io
import base64

class Plot:
    def __init__(self, lat, lng, showConstellations, showMilkyWay, showEquator, showHorizon, showEcliptic, showGalaxies, showOpenCluster, showMoon, showGridLines):
        self.lat = lat
        self.lng = lng
        self.tz = TimezoneFinder().timezone_at(lat=lat, lng=lng)
        self.dt = datetime.now(timezone(self.tz))
        self.showConstellations = showConstellations
        self.showMilkyWay = showMilkyWay
        self.showEquator = showEquator
        self.showHorizon = showHorizon
        self.showEcliptic = showEcliptic
        self.showGalaxies = showGalaxies
        self.showOpenCluster = showOpenCluster
        self.showMoon = showMoon
        self.showGridLines = showGridLines

    def generatePlot(self):

        style = PlotStyle().extend(
            extensions.NORD,
        )


        self.p = MapPlot(
            projection=Projection.ZENITH,
            lat=self.lat,
            lon=-self.lng,
            dt=self.dt,
            style=style,
            resolution=800,
            autoscale=True
        )


        self.p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 2.1])

        # Show azimuth and elevation lines
        if self.showGridLines:
            self.p.gridlines(labels=False)

        # Show constellations lines
        if self.showConstellations:
            self.p.constellations()
        
        # Show horizon, in a circle plot only
        if self.showHorizon:
            self.p.horizon()

        # Show Sun trace line
        if self.showEcliptic:
            self.p.ecliptic()
        
        # Show celestial equator
        if self.showEquator:
            self.p.celestial_equator()

        # Show Galaxies
        if self.showGalaxies:
            self.p.galaxies(where=[_.magnitude < 9], true_size=False, labels=None)

        # Show Open cluster
        if self.showOpenCluster:
            self.p.open_clusters(where=[_.magnitude < 9], true_size=False, labels=None)

        # Show milky way interpolation
        if self.showMilkyWay:
            self.p.milky_way()

        # Show ... the moon phase seems to not works well.
        if self.showMoon:
            self.p.moon(show_phase=True)
        

        # Constellations labels can be shown here but must be at the end to improve positioning
        if self.showConstellations:
            self.p.constellation_labels()

        self.p.planets()

        # self.p.legend()


    def getBase64(self):
        my_stringIObytes = io.BytesIO()
        self.p.fig.savefig(my_stringIObytes, format='svg', bbox_inches="tight", pad_inches=0.1, transparent=True)
        my_stringIObytes.seek(0)
        return base64.b64encode(my_stringIObytes.read()).decode()
    
    def export(self):
        self.p.export("starmap.svg", format="svg", padding=0.1)
