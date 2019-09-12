import os

import hug
import waitress

# functionality

import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.figure import Figure
from owslib.wms import WebMapService

import base64
from io import BytesIO

matplotlib.use('AGG')

@hug.get('/vandaag', output=hug.output_format.html)
def vandaag():
    projection = ccrs.epsg(28992)
    # projection = ccrs.Mercator.GOOGLE
    fig, ax = plt.subplots(
        figsize=(10, 10), 
        dpi=92,
        subplot_kw=dict(projection=projection))

    # ax = plt.axes(projection=projection)

    # ax.set_extent(extents=[345000, 6600000, 825000, 7100000], crs=projection)
    ax.set_extent(extents=[5000, 300000, 300000, 630000], crs=projection)

    # wms = WebMapService('http://localhost:8383/cgi-bin/mapserv', version=)
    wms = WebMapService('http://localhost:8383/maps/aktes', version='1.1.1')
    img = wms.getmap(layers=['akte_points'],
                     styles='',
                     srs='EPSG:28992',
                     bbox=(5000, 300000, 300000, 630000),
                     size=(1200, 1200),
                     format='image/png',
                     transparent=True)
    # out = open('map.png', 'wb')
    # out.write(img.read())
    # out.close()

    img_buf = BytesIO()
    img_buf.write(img.read())
    # ax.image(img.read())

    # return img.read()

    # ax.add_wms(
    #     wms=wms,
    #     layers='akte_points',
    #     zorder=1)

    ax.add_wmts('https://geodata.nationaalgeoregister.nl/tiles/service/wmts', 'brtachtergrondkaart', zorder=0)

    ax.stock_img()

    # Use `zoom` to control the size of the image
    lat = 5000
    lon = 300000
    imagebox = OffsetImage(img.read(), zoom=0.01)
    imagebox.image.axes = ax
    ab = AnnotationBbox(imagebox, [lat, lon], pad=0, frameon=False)
    ax.add_artist(ab)

    # ?map=/srv/mapserver/aktes.map
    # wms_kwargs={
    #     # 'SERVICE' : 'WMS',
    #     # 'VERSION' : '1.3.0',
    #     # 'REQUEST' : 'GetMap',
    #     # 'BBOX' : '76925.29500608461967,419380.3310261650477,313211.8040464186925,524380.3310261651641',
    #     'CRS' : 'EPSG:28992',
    #     'WIDTH' : '1619',
    #     'HEIGHT' : '719',
    #     'STYLES' : '',
    #     'FORMAT' : 'image/png',
    #     'DPI' : '96',
    #     'MAP_RESOLUTION' : '96',
    #     'FORMAT_OPTIONS' : 'dpi:96',
    #     'TRANSPARENT' : 'TRUE'
    # })
    # plt.show()

    # plt.savefig('map.png', format='png')

    buf = BytesIO()
    # fig.savefig(buf, format="png")
    # FigureCanvas(fig).print_png(buf)
    plt.savefig(buf, format='png')
    # buf.write(img.read())
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<html><body><img src='data:image/png;base64,{data}'/></body></html>"
    # return buf


# hug set up

@hug.response_middleware()
def cors(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.set_header(
        'Access-Control-Allow-Headers',
        'Authorization,Keep-Alive,User-Agent,'
        'If-Modified-Since,Cache-Control,Content-Type'
    )
    response.set_header(
        'Access-Control-Expose-Headers',
        'Authorization,Keep-Alive,User-Agent,'
        'If-Modified-Since,Cache-Control,Content-Type'
    )
    if request.method == 'OPTIONS':
        response.set_header('Access-Control-Max-Age', 1728000)
        response.set_header('Content-Type', 'text/plain charset=UTF-8')
        response.set_header('Content-Length', 0)
        response.status_code = hug.HTTP_204


@hug.get('/health')
def health():
    return 'akte radar is healthy!'


app = hug.API(__name__)

if __name__ == '__main__':
    # vandaag()
    waitress.serve(__hug_wsgi__, port=8000)
