# gis information
import math
import numpy as np
import geopandas as gpd
import shapely


def nodes_gdf(nodes):
    return gpd.GeoDataFrame(nodes.copy(), crs='EPSG:26910',
                            geometry=[shapely.geometry.Point(v) for v in nodes.values])


def elements_gdf(nodes, elements):
    '''
    Adds polygons translating the simplex information to build a Polygon (left to right node transversal)
    '''
    geomarr = []
    for i in range(len(elements)):
        x = elements.iloc[i, 0:4]
        p = nodes.loc[x[x != 0], :]
        geomarr.append(shapely.geometry.Polygon(p.to_records(index=False).tolist()))
    return gpd.GeoDataFrame(elements.copy(), crs='EPSG:26910', geometry=geomarr)


def interp(xp, yp, x, y):
    if len(x) == 3 and len(y) == 3:
        return interp_tri(xp, yp, x, y)
    elif len(x) == 4 and len(y) == 4:
        return interp_quad(xp, yp, x, y)
    else:
        raise "Can only interpolate to triangular or quadrilateral elements"


def interp_quad(xp, yp, x, y):
    coeff = np.full((4,), -1, dtype='f')
    a = (y[0]-y[1])*(x[2]-x[3])-(y[2]-y[3])*(x[0]-x[1])
    bo = y[0]*x[3]-y[1]*x[2]+y[2]*x[1]-y[3]*x[0]
    bx = -y[0]+y[1]-y[2]+y[3]
    by = x[0]-x[1]+x[2]-x[3]
    b = bo+bx*xp+by*yp
    co = -(y[0]+y[1])*(x[2]+x[3])+(y[2]+y[3])*(x[0]+x[1])
    cx = y[0]+y[1]-y[2]-y[3]
    cy = -x[0]-x[1]+x[2]+x[3]
    c = co+2.0*(cx*xp+cy*yp)
    if (a == 0.0):
        if (b == 0.0):
            raise('Polygon geometry is a point or line!')
        xt = -c/(2.0*b)
    else:
        xt = b*b-a*c
        if (xt < 0.0):
            raise ('Polygon shape is invalid!')
        xt = (-b+math.sqrt(xt))/a
    xt = max(-1.0, min(xt, 1.0))
    a = (y[1]-y[2])*(x[0]-x[3])-(y[0]-y[3])*(x[1]-x[2])
    bo = y[0]*x[1]-y[1]*x[0]+y[2]*x[3]-y[3]*x[2]
    bx = -y[0]+y[1]-y[2]+y[3]
    by = x[0]-x[1]+x[2]-x[3]
    b = bo+bx*xp+by*yp
    co = -(y[0]+y[3])*(x[1]+x[2])+(y[1]+y[2])*(x[0]+x[3])
    cx = y[0]-y[1]-y[2]+y[3]
    cy = -x[0]+x[1]+x[2]-x[3]
    c = co+2.0*(cx*xp+cy*yp)
    if (a == 0.0):
        if (b == 0.0):
            raise('Polygon geometry is a point or line!')
        yt = -c/(2.0*b)
    else:
        yt = b*b-a*c
        if (yt < 0.0):
            raise('Polygon shape is invalid')
        yt = (-b-math.sqrt(yt))/a
    yt = max(-1.0, min(yt, 1.0))
    coeff[0] = 0.25*(1.0-xt)*(1.0-yt)
    coeff[1] = 0.25*(1.0+xt)*(1.0-yt)
    coeff[2] = 0.25*(1.0+xt)*(1.0+yt)
    coeff[3] = 0.25*(1.0-xt)*(1.0+yt)
    return coeff


def interp_tri(xp, yp, x, y):
    coeff = np.full((3,), -1, dtype='f')
    # Triangular element
    xij = x[0]-x[1]
    xjk = x[1]-x[2]
    xki = x[2]-x[0]
    yij = y[0]-y[1]
    yjk = y[1]-y[2]
    yki = y[2]-y[0]
    xt = (-x[0]*y[2]+x[2]*y[0]+yki*xp-xki*yp)/(-xki*yjk+xjk*yki)
    xt = max(0.0, xt)
    yt = (x[0]*y[1]-x[1]*y[0]+yij*xp-xij*yp)/(-xki*yjk+xjk*yki)
    yt = max(0.0, yt)
    coeff[0] = 1.0-min(1.0, xt+yt)
    coeff[1] = xt
    coeff[2] = yt
    return coeff
