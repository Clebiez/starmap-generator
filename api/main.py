from flask import Flask, request
from plot import Plot

app = Flask(__name__)


@app.route("/")
def generateStarPlot():
    plotStyle = request.args.get('plotStyle', '')
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    date = request.args.get('date', type=str)
    showConstellations = request.args.get('showConstellations', type=bool)
    showMilkyWay = request.args.get('showMilkyWay', type=bool)
    showEquator = request.args.get('showEquator', type=bool)
    showHorizon = request.args.get('showHorizon', type=bool)
    showEcliptic = request.args.get('showEcliptic', type=bool)
    showOpenCluster = request.args.get('showOpenCluster', type=bool)
    showGalaxies = request.args.get('showGalaxies', type=bool)
    showMoon = request.args.get('showMoon', type=bool)
    showGridLines = request.args.get('showGridLines', type=bool)

    plot = Plot(lat=lat, lng=lng, date=date, showConstellations=showConstellations, showMilkyWay=showMilkyWay, showEquator=showEquator, showHorizon=showHorizon,
                showEcliptic=showEcliptic, showOpenCluster=showOpenCluster, showGalaxies=showGalaxies, showMoon=showMoon, showGridLines=showGridLines)
    plot.generatePlot()

    b64 = plot.getBase64()

    return {
        "image": f"data:image/svg+xml;base64,{b64}"
    }
