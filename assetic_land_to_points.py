'''
a template because it saves time.
'''

import arcpy as ap
import os
import sys
# make sure this path is correct and it contains sendErrorEmail.py script
scriptdir = 'D:\ArcGISCatalog\PYs\email_errors'
sys.path.insert(0, scriptdir)
scriptName = os.path.basename(__file__) 
from sendErrorEmail import sendEmail

gis = r'\\cappgis10\d$\ArcGISCatalog\SDEConnections\cdbpsql20GISgisdba.sde'
##gis = r'C:\Users\ltonkin\Documents\ArcGIS\Projects\43110\43110.gdb'
#gis = r'C:\Users\ltonkin\Documents\ArcGIS\Reference\sde\cdbpsql20GISgisdba.sde'
# system controlled fields are best excepted hence the list 'bad_names'
try:
    bad_names = ['OBJECTID',
                 'Shape.STArea()',
                 'Shape.STLength()']
    in_fc = 'Assetic_Land_Register'
    out_fc = 'Assetic_Land_Register_Centroids'
    in_path_fc = os.path.join(gis, in_fc)
    out_path_fc = os.path.join(gis, out_fc)
    # list field objects to get the name property
    fld_objs = ap.ListFields(in_path_fc)
    # loop through the field objects and append their names to the list
    # excepting the ones which are known to cause issues
    fld_names = [fld_obj.name for fld_obj in fld_objs
                 if fld_obj.name not in bad_names]
    # assign the index position of the shape field in the names list to be
    # used later for replacing with a geometry and obtaining
    # the geometry's centroid
    # replace shape for geometry in the field list, because the geometry's centroid
    # property is an inside point
    # put 'SHAPE@XY' into the fields for the insert cursor
    # because we are going to insert a point geometry into the row object
    shape_pos = fld_names.index('Shape')
    in_flds = ['Shape@' if x == 'Shape' else x for x in fld_names]
    out_flds = ['Shape@XY' if x == 'Shape' else x for x in fld_names]
    # make the insertCursor outside the SearchCursor loop
    out_cur = ap.da.InsertCursor(out_path_fc, out_flds)
    # Truncate the destination featureclass, so it is prepared for population
    ap.TruncateTable_management(out_path_fc)
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
except Exception as error:
    sendEmail(scriptName, str(error))
