"""Assetic Land to Points.
Make points from polygons using cursors and SHAPE@XY
"""

import arcpy as ap
import os

gis = r'\\cappgis10\d$\ArcGISCatalog\SDEConnections\cdbpsql20GISgisdba.sde'
gg = 'gis.gisdba.'
# system controlled fields are best excepted hence the list 'bad_names'
bad_names = ['OBJECTID',
             'Shape.STArea()',
             'Shape.STLength()']
in_fc = 'Assetic_Land_Register'
out_fc = 'Assetic_Land_Register_Centroids'
in_path_fc = os.path.join(gis, gg + in_fc)
out_path_fc = os.path.join(gis, gg + out_fc)
# list field objects to get the name property
fld_objs = ap.ListFields(in_path_fc)
# Here we are making a list of good names that
# don't cause errors as we process.
fld_names = [fld_obj.name for fld_obj in fld_objs
             if fld_obj.name not in bad_names]
# Assign the index position of the shape field in the
# names list to be used later for replacing with a
# geometry and obtaining the geometry's centroid.
# Replace shape for geometry in the field list,
# because the geometry's centroid property is an inside point.
# Put 'SHAPE@XY' into the fields for the insert cursor
# so that we end up with a point geometry. 
shape_pos = fld_names.index('Shape')
in_flds = ['Shape@' if x == 'Shape' else x for x in fld_names]
out_flds = ['Shape@XY' if x == 'Shape' else x for x in fld_names]
# make the insertCursor outside the SearchCursor loop
out_cur = ap.da.InsertCursor(out_path_fc, out_flds)
# Delete rows so there will be no duplicates.
ap.DeleteRows_management(out_path_fc)
# build the SearchCursor, think of this as the other half
# of the InsertCursor
with ap.da.SearchCursor((in_path_fc), in_flds) as s_cursor:
    for row in s_cursor:
        # build an outrow constructed of row, replacing the geometry
        # with it's centroid
        outrow = row[:shape_pos] + tuple([row[shape_pos].centroid]) + row[shape_pos + 1:]
        # insert the outrow which has an inside or an on point geometry
        out_cur.insertRow(outrow)
del out_cur 
