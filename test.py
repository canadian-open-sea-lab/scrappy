from mapapi_connector import Conn
from scrapers import wms
from owslib.wms import WebMapService

connector = 'postgresql://postgres:winner@localhost/postgres'
with Conn(connector) as conn:
	session = conn.get_session()

	Layer = conn.Base.classes.layer


	wms = WebMapService('http://geoserver.emodnet-physics.eu/geoserver/emodnet/wms')
	layers = list(wms.contents)
	for layer_name in layers:
		l = wms.contents[layer_name]
		print("Loading %s" % l.title)
		session.add(Layer(
			code="".join(l.title.split()),
			type='Tile',
			zindex=1,
			opacity=1,
			labelen=l.title,
			source_id=38,
			isbackground=False,
			isvisible=True,
			istimeenabled=False if l.timepositions is None else True,
		))

	session.commit()

	session.close()