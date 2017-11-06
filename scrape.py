from owslib.wms import WebMapService

import mapapi_connector
import config


def main():
    connector = config.MAPAPI_DATABASE_CONNECTOR
    with mapapi_connector.WMSConn(connector) as conn:
        # Process WMS
        for s in config.wms:
            print("Connecting to: %s" % s)
            wms = WebMapService(s)
            conn.add_source(wms)

            for layer_name in wms.contents:
                print("\tAttempting to add: %s" % layer_name)
                wms_layer = wms.contents[layer_name]
                conn.add_layer(wms, wms_layer)

        # Process WFS
        for s in config.wfs:
            pass
    return


if __name__ == '__main__':
    main()
