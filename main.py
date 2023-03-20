import sqlite3
import os
from osgeo import ogr
from pyproj import CRS

# generate empty geopackage using osgeo ogr library

driver = "GPKG"
filename = "generated.gpkg"

driver = ogr.GetDriverByName(driver)

if os.path.exists(filename):
    driver.DeleteDataSource(filename)

data_source = driver.CreateDataSource(filename)

data_source = None

# connect to geopackage using sqlite3

conn = sqlite3.connect(filename)

cursor = conn.cursor()

# set values for gpkg_spatial_ref_sys fields
# pyproj.CRS used to define EPSG as WKT

srs_name = "OSGB36 / British National Grid"
srs_id = 27700
srs_org = "EPSG"
srs_org_id = 27700
srs_def = CRS.from_epsg(27700).to_wkt()
srs_desc = "Easting / northing, units in meters"

# insert values into gpkg_spatial_ref_sys

cursor.execute(
    "insert into gpkg_spatial_ref_sys VALUES (?, ?, ?, ?, ?, ?)",
    (srs_name, srs_id, srs_org, srs_org_id, srs_def, srs_desc),
)

# create tables and trigger

cursor.executescript(
    """
    CREATE TABLE 'point' (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    geom POINT NOT NULL,
    name TEXT NOT NULL,
    buffer INTEGER NOT NULL
    );

    CREATE TABLE 'poly' (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    geom POLYGON NOT NULL,
    point_id INTEGER,
    FOREIGN KEY(point_id) REFERENCES point(id)
    );

    CREATE TRIGGER insert_buffer_poly
        AFTER INSERT ON point
    BEGIN
        INSERT INTO poly(geom, point_id)
        VALUES(st_buffer(new.geom, new.buffer), new.id);
    END;
"""
)

# insert values into gpkg_contents tables

cursor.execute(
    "insert into gpkg_contents values ('point','features','point','point','2019-02-19T10:49:06.022Z',NULL,NULL,NULL,NULL,27700);"
)
cursor.execute(
    "insert into gpkg_contents values ('poly','features','poly','poly','2019-02-19T10:49:06.022Z',NULL,NULL,NULL,NULL,27700);"
)

# insert values into gpkg_geometry_column tables

cursor.execute(
    "insert into gpkg_geometry_columns values ('point','geom','POINT', 27700, 0, 0 )"
)
cursor.execute(
    "insert into gpkg_geometry_columns values ('poly','geom','POLYGON',27700, 0, 0 )"
)

# commit changes

conn.commit()
