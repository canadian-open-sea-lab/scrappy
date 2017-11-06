"""Collection of functions and objects to connect with mapapi."""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKeyConstraint, ForeignKey, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import sessionmaker

import config


class WMSConn:
    """Manage a WMS centric connection to the SLGO mapapi database."""

    def __init__(self, mapapi_database_connector):
        """Store initial variables."""
        self.engine = create_engine(mapapi_database_connector)
        self.m = MetaData()

    def __enter__(self):
        """Create a database connection."""
        self.m.reflect(bind=self.engine)
        self.Base = automap_base(metadata=self.m)
        self.Base.prepare(self.engine, reflect=True)
        self.Session = sessionmaker(bind=self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Tidy up after a connection."""
        self.Session.close_all()

    def get_code(self, layer_title):
        return "".join(layer_title.split())

    def get_session(self):
        """Return a database session."""
        return self.Session()

    def get_source(self, url):
        """Return the database record for the source if it exists."""
        Source = self.Base.classes.source
        session = self.get_session()
        res = session.query(Source).filter(Source.url == url).one_or_none()
        session.close()
        return res

    def add_source(self, wms):
        """Check if source exists, add it if not."""
        Source = self.Base.classes.source
        session = self.get_session()

        if self.get_source(wms.url) is None:
            wms_layer = None
            for c in wms.contents:
                wms_layer = wms.contents[c]
                break
            session.add(Source(
                url=wms.url,
                projection=wms_layer.boundingBox[4],
                type='TileWMS',
                format='image/png',
                wmsversion=wms.version,
                wmslayers=wms_layer.name,
                tilesorigin='%s,%s' % (
                    wms_layer.boundingBox[0],
                    wms_layer.boundingBox[1]
                ),
                istiled=True,
                istimeenabled=False if wms_layer.timepositions is None else True,
            ))
            session.commit()
        session.close()

    def get_layer(self, wms, wms_layer):
        """Return the database record for the layer if it exists."""
        Layer = self.Base.classes.layer
        session = self.get_session()

        source = self.get_source(wms.url)

        res = session.query(Layer).filter(
            Layer.source_id == source.id,
            Layer.code == self.get_code(wms_layer.title)
        ).one_or_none()

        session.close()
        return res

    def add_layer(self, wms, wms_layer, add_source=True):
        """Check if layer exists, add it if not."""
        Layer = self.Base.classes.layer
        session = self.get_session()

        if self.get_layer(wms, wms_layer) is None:
            source = self.get_source(wms.url)
            if source is None and add_source:
                self.add_source(wms)
                source = self.get_source(wms.url)
            elif source is None and not add_source:
                raise Exception("Source doesn't exist and database and add_source is disabled")
            session.add(Layer(
                code=self.get_code(wms_layer.title),
                type='Tile',
                zindex=1,
                opacity=1,
                labelen=wms_layer.title,
                source_id=source.id,
                isbackground=False,
                isvisible=True,
                istimeenabled=False if wms_layer.timepositions is None else True,
            ))
            session.commit()
        session.close()
