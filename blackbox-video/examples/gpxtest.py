import gpxpy
from gpxpy.parser import GPXParser


def get_points():
    with open('input/zuidhollandrit.gpx','r') as f:
        parser = GPXParser(f)
        gpx = parser.parse()

    route = gpx.routes[0]

    points = []
    for routepoint in route.points:
        points.append((routepoint.longitude,routepoint.latitude))



    return points

if __name__ == '__main__':
    get_points()