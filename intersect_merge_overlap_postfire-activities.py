## Refine MTBS and FACTS datasets from initial download to create a table 
# and a feature layer that depict all postfire reforestation activities,
# splitting treatment records where overlapping polygons occur.

# Author: Kelly Smith

import arcpy
import os


## Set workspace
##
arcpy.env.workspace = r"C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\phase1_2023.gdb"

# Select records from "S_USA.AdministrativeForest" where REGION = 05
arcpy.MakeFeatureLayer_management("S_USA.AdministrativeForest", "admin_forests_lyr")
arcpy.SelectLayerByAttribute_management("admin_forests_lyr", "NEW_SELECTION", "REGION = '05'")
# Copy feature as "Admin_Forests_R5"
arcpy.CopyFeatures_management("admin_forests_lyr", "Admin_Forests_R5")


## Subset MTBS perimeter layer
# Extract the Year from the field Ig_Date in the layer mtbs_perims_DD.shp
# arcpy.AddField_management("mtbs_perims_dd", "Ig_Year", "SHORT")

# Set the local variables
in_table = "mtbs_perims_DD"
field_name = "Ig_Year"
expression = "str(!Ig_Date!)[-4:]"
# Execute AddField
arcpy.AddField_management(in_table, field_name, "SHORT")
# Execute CalculateField
arcpy.CalculateField_management(in_table, field_name, expression, "PYTHON")

# Subset MTBS layer to include only wildfires in R5 from 1993-2017
arcpy.MakeFeatureLayer_management("mtbs_perims_dd", "mtbs_lyr")
arcpy.SelectLayerByLocation_management("mtbs_lyr", "INTERSECT", "Admin_Forests_R5")
arcpy.SelectLayerByAttribute_management("mtbs_lyr", "SUBSET_SELECTION", "Ig_Year > 1993 AND Ig_Year < 2017")
arcpy.SelectLayerByAttribute_management("mtbs_lyr", "SUBSET_SELECTION", "Incid_Type = 'Wildfire'")
arcpy.analysis.PairwiseIntersect("mtbs_lyr;Admin_Forests_R5", "mtbs_lyr", "ALL", None, "INPUT")

# Calculate acres in field "Fire_Acres"
arcpy.management.CalculateGeometryAttributes("mtbs_lyr", "Fire_Acres AREA_GEODESIC", '', "ACRES", None, "SAME_AS_INPUT")

# Preserve only the fields Incid_Name, BurnBndAc, Ig_Year, and Fire_Acres_R5
field_mappings = arcpy.FieldMappings()
field_mappings.addTable("mtbs_lyr")
for field in field_mappings.fields:
    if field.name not in ["Incid_Name", "BurnBndAc", "Ig_Year", "Fire_Acres"]:
        field_mappings.removeFieldMap(field_mappings.findFieldMapIndex(field.name))
# Save output as mtbs_wildfires_CA_1993_2017
arcpy.FeatureClassToFeatureClass_conversion("mtbs_lyr", arcpy.env.workspace, "mtbs_wildfires_CA_1993_2017", field_mapping=field_mappings)
arcpy.AlterField_management("mtbs_wildfires_CA_1993_2017", "Fire_Acres", "Fire_Acres_R5", "Fire_Acres_R5")



## Intersect FACTS layers with MTBS layer
##
arcpy.analysis.PairwiseIntersect("S_USA.Activity_SilvReforestation;mtbs_wildfires_CA_1993_2017_f1", "Refor_fires_int", "ALL", None, "INPUT")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_SilvTSI;mtbs_wildfires_CA_1993_2017_f1", "TSI_fires_int", "ALL", None, "INPUT")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_TimberHarvest;mtbs_wildfires_CA_1993_2017_f1", "Harvest_fires_int", "ALL", None, "INPUT")

## Subset unique Stewardship Activities related to reforestation
arcpy.management.SelectLayerByAttribute("S_USA.Activity_StwrdshpCntrctng_PL", "NEW_SELECTION", "ACTIVITY_N = 'Control of Understory Vegetation' Or ACTIVITY_N = 'Stocking Survey' Or ACTIVITY_N = 'Site Preparation for Planting - Mechanical'")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_StwrdshpCntrctng_PL;mtbs_wildfires_CA_1993_2017_f1", "Steward_fires_int", "ALL", None, "INPUT")


### ALTERNATIVE
## Merge raw FACTS layers for input into Young code

# reforestation = "S_USA.Activity_SilvReforestation"
# tsi = "S_USA.Activity_SilvTSI"
# harvest = "S_USA.Activity_TimberHarvest"
# stewardship = "S_USA.Activity_StwrdshpCntrctng_PL"

# raw_facts = [f for f in arcpy.ListFeatureClasses() if "S_USA.Act" in f]
# field_mappings = arcpy.FieldMappings()
# # keep_fields = ["ADMIN_FO_1", "ADMIN_DIST", "SUID", "FACTS_ID", "SUBUNIT", "ACTIVITY_N", "NBR_UNITS_", "NBR_UNITS1", "DATE_COMPL", "FY_COMPLET", "PRODUCTI_1", "LAND_SUI_1", "SUBUNIT_SI", "CRC_VALUE", "GIS_ACRES"]
# keep_fields = ["ADMIN_FO_1", "ADMIN_DIST", "SUID", "FACTS_ID", "SUBUNIT", "ACTIVITY_N", "NBR_UNITS_", "NBR_UNITS1", "DATE_COMPL", "FY_COMPLET", "SUBUNIT_SI", "CRC_VALUE", "GIS_ACRES"]
# output_feature = "merged_facts"

# # Create field mappings
# for field in keep_fields:
#     field_map = arcpy.FieldMap()
#     field_map.addInputField(raw_facts[0], field)
#     field_mappings.addFieldMap(field_map)

# # Merge input features
# arcpy.Merge_management(raw_facts, output_feature, field_mappings, "ADD_SOURCE_INFO")



## Merge features before using Count Overlapping Features in order to have a single join field for reference 
# Set local variables
input_features = [f for f in arcpy.ListFeatureClasses() if "_int" in f]
field_mappings = arcpy.FieldMappings()
keep_fields = ["ADMIN_FO_1", "ADMIN_DIST", "SUID", "FACTS_ID", "SUBUNIT", "ACTIVITY_N", "NBR_UNITS_", "NBR_UNITS1", "DATE_COMPL", "FY_COMPLET", "PRODUCTI_1", "LAND_SUI_1", "SUBUNIT_SI", "CRC_VALUE", "GIS_ACRES", "Incid_Name", "BurnBndAc", "Ig_Year", "Ig_Date", "Fire_Acres_R5"]
output_feature = "Merged_Treatments"

# Create field mappings
for field in keep_fields:
    field_map = arcpy.FieldMap()
    field_map.addInputField(input_features[0], field)
    field_mappings.addFieldMap(field_map)

# Merge input features
arcpy.Merge_management(input_features, output_feature, field_mappings, "ADD_SOURCE_INFO")
arcpy.AddGeometryAttributes_management(output_feature, "AREA_GEODESIC", Area_Unit="ACRES")
arcpy.AlterField_management(output_feature, "AREA_GEO", "Acres_within_Fire", "Acres_within_Fire")

post_clause = '"FY_COMPLET" > "Ig_Year"'
arcpy.Select_analysis(output_feature, "Merged_Treatments_Postfire", post_clause)

## Export subset of Activity_N related to reforestation
# Select records where FY_COMPLET > Ig_Year and ACTIVITY_N meets the specified criteria
where_clause = '"FY_COMPLET" > "Ig_Year" AND ("ACTIVITY_N" = \'Fill-in or Replant Trees\' Or "ACTIVITY_N" = \'Stocking Survey\' Or "ACTIVITY_N" = \'Plant Trees\' Or "ACTIVITY_N" = \'Salvage Cut (intermediate treatment, not regeneration)\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Burning\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Chemical\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Manual\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Mechanical\' Or "ACTIVITY_N" = \'Site Preparation for Planting - Mechanical\' Or "ACTIVITY_N" = \'Tree Release and Weed\' Or "ACTIVITY_N" = \'Group Selection Cut (UA/RH/FH)\' Or "ACTIVITY_N" = \'Coppice Cut (w/leave trees) (EA/RH/FH)\' Or "ACTIVITY_N" = \'Sanitation Cut\' Or "ACTIVITY_N" = \'Seed-tree Seed Cut (with and without leave trees) (EA/RH/NFH)\' Or "ACTIVITY_N" = \'Single-tree Selection Cut (UA/RH/FH)\' Or "ACTIVITY_N" = \'Stand Clearcut (EA/RH/FH)\' Or "ACTIVITY_N" = \'Stand Clearcut (w/ leave trees) (EA/RH/FH)\' Or "ACTIVITY_N" = \'Fertilization\' Or "ACTIVITY_N" = \'Precommercial Thin\' Or "ACTIVITY_N" = \'Prune\')'
arcpy.Select_analysis("Merged_Treatments_Postfire", "postfire_treatments_final", where_clause)


## Export merged treatment table before running Count Overlap
in_feature = "postfire_treatments_final"
out_path = "C:/Users/smithke3/OneDrive - Oregon State University/Kelly/Data/"
arcpy.TableToTable_conversion(in_feature, out_path, "postfire_treatments_final.csv")

## Count Overlapping Features for all records in all postfire activities

# Wherever two or more records overlap, new polygons are generated with distinct IDs;
# a table identifying each overlap is then joined with the treatment and overlap features.

# This allows for summarization of each treatment type and all treatment combinations 
# as well as retaining the information of each intra/inter-duplicating record.

from arcpy import env
env.workspace = r"C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\phase1_2023.gdb"


# Set local variables
input_features = "postfire_treatments_final"
output_feature = "Overlap_Feature"
output_table = "Overlap_Table"

# Count overlapping features
arcpy.analysis.CountOverlappingFeatures(input_features, output_feature, 1, output_table)

# Calculate geometry of Overlap_Feature in US acres
arcpy.AddGeometryAttributes_management(output_feature, "AREA_GEODESIC", Area_Unit="ACRES")
arcpy.AlterField_management(output_feature, "AREA_GEO", "Overlap_Acres", "Overlap_Acres")

# Join the field "ORIG_OID" in Overlap_Table with "OBJECTID" in Merged_Postfire
arcpy.management.AddJoin(output_table, "ORIG_OID", input_features, "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")
arcpy.TableToTable_conversion(output_table, env.workspace, "Overlap_Table_Joined")

# Join "OVERLAP_OID" in Overlap_Table_Joined with "OBJECTID" in Overlap_feature
# arcpy.management.AddJoin("Overlap_Table_Joined", "OVERLAP_OID", output_feature, "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")

# Join "OBJECTID" in Overlap_Feature_Joined with "OVERLAP_OID" in Overlap_Table
arcpy.management.AddJoin(output_feature, "OBJECTID", "Overlap_Table_Joined", "OVERLAP_OID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")
arcpy.management.CopyFeatures("Overlap_Feature", "Overlap_Feature_Joined", '', None, None, None)


for year in range(1993, 2018):
    if year == 1998:    # no postfire reforestation for fires in 1998
        continue
    # Select records from Overlap_Feature where Ig_Year is equal to the current year and Overlap_Table_Joined_Ig_Year < Overlap_Table_Joined_FY_COMPLET
    where_clause = "Overlap_Table_Joined_Ig_Year = {} AND Overlap_Table_Joined_Ig_Year < Overlap_Table_Joined_FY_COMPLET".format(year)
    arcpy.SelectLayerByAttribute_management("Overlap_Feature_Joined", "NEW_SELECTION", where_clause)

    # # Check if Overlap_Table_Joined_FY_COMPLET is greater than or equal to year
    # with arcpy.da.SearchCursor("Overlap_Feature_Joined", ["Overlap_Table_Joined_FY_COMPLET"]) as cursor:
    #     for row in cursor:
    #         if row[0] < year:
    #             continue

    # Use Tabulate Area tool with OVERLAP_OID as feature zone data
    input_zone = "Overlap_Feature_Joined"
    zone_field = "Overlap_Table_Joined_OBJECTID"
    input_raster = "mtbs_CA_{}.tif".format(year)
    class_field = "Value"
    output_tabulate = "tabulate_postfire_{}".format(year)
    output_zonal = "zonal_postfire_{}".format(year)
    
    # ZONAL STATS
    arcpy.sa.ZonalStatisticsAsTable(input_zone, zone_field, input_raster, output_zonal, "NODATA", "ALL")
    # Add field to output_zonal that equals value of Overlap_Table_OVERLAP_OID field for that record
    arcpy.management.AddField(output_zonal, "Overlap_Table_Joined_OBJECTID", "LONG")
    arcpy.management.CalculateField(output_zonal, "Overlap_Table_Joined_OBJECTID", "!{}!".format(zone_field), "PYTHON3")
    # Add Ig_Year field to output_zonal and set its value to the current year   
    arcpy.management.CalculateField(output_zonal, "Ig_Year_zonal", "{}".format(year), "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")
    
    # TABULATE AREA
    arcpy.sa.TabulateArea(input_zone, zone_field, input_raster, class_field, output_tabulate)
    arcpy.management.CalculateField(output_tabulate, "Ig_Year_tab", "{}".format(year), "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")


# Find all tables containing the text "tabulate_postfire" in the name and merge them
outTable = "tabulate_allyears"
tableList = [table for table in arcpy.ListTables() if "tabulate_postfire" in table]
# Merge the annual tables
arcpy.Merge_management(tableList, outTable)


# Find all tables containing the text "zonal_postfire" in the name and merge them
# Set the local variables
outTable = "zonal_allyears"
fieldMappings = arcpy.FieldMappings()
keepFields = ["OBJECTID", "Overlap_Table_Joined_OBJECTID", "Ig_Year_zonal", "MEAN", "MEDIAN", "MAJORITY"]

# Find all tables containing the text "zonalst_merged" in the name
tableList = [table for table in arcpy.ListTables() if "zonal_postfire" in table]

# Add the tables to the field mappings and retain only the specified fields
for table in tableList:
    fieldMappings.addTable(table)
    for field in fieldMappings.fields:
        if field.name not in keepFields:
            fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
# Merge the annual zonal tables
arcpy.Merge_management(tableList, outTable, fieldMappings)


# Join the merged Tabulate & Zonal tables by the OVERLAP_OID fields
in_data = "Overlap_Feature_Joined"
in_field = "OBJECTID"
in_field_zonal = "Overlap_Table_Joined_OBJECTID"
in_field_tabulate = "Overlap_Table_Joined_OBJECTID"
out_data = "postfire_overlaps"

join_table_zonal = "zonal_allyears"
join_field_zonal = "Overlap_Table_Joined_OBJECTID"
join_table_tabulate = "tabulate_allyears"
join_field_tabulate = "OVERLAP_TABLE_JOINED_OBJECTID"

arcpy.management.MakeFeatureLayer(in_data, "input_lyr")
arcpy.management.AddJoin("input_lyr", in_field_tabulate, join_table_tabulate, join_field_tabulate, "KEEP_COMMON")
arcpy.management.AddJoin("input_lyr", in_field_zonal, join_table_zonal, join_field_zonal, "KEEP_COMMON")
arcpy.management.CopyRows("input_lyr", out_data)

# Remove prefixes in field names generated by AddJoin
# Set the feature class
fc = "postfire_overlaps"

# Get a list of fields in the feature class
fields = arcpy.ListFields(fc)

# Loop through the fields
for field in fields:
    # Skip the OBJECTID field
    if "OBJECTID" in field.name:
        continue

    # Get the field alias
    field_alias = field.aliasName

    # Rename the field to match its alias using the AlterField tool
    arcpy.AlterField_management(fc, field.name, field_alias)


# Join "OVERLAP_OID" in Overlap_Table_Joined with "OBJECTID" in Overlap_feature
# arcpy.management.AddJoin("Overlap_Table_Joined", "OVERLAP_OID", "Overlap_Feature_Joined_Severity", "Overlap_Feature_Joined_Overlap_Table_Joined_OVERLAP_OID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")


# Export table to csv to be used for overlap summarization
arcpy.TableToTable_conversion("postfire_overlaps", r"C:\Users\smithke3\OneDrive - Oregon State University\Kelly\Data", "Postfire_Overlaps.csv")


from collections import defaultdict

input_table = 'postfire_overlaps'
output_table = 'postfire_overlaps_final'
fields = ['OVERLAP_OID', 'CRC_VALUE', 'FY_COMPLET', 'Ig_Year', 'Acres_within_Fire']

# Create a new table with the same schema as the input table
arcpy.CreateTable_management(arcpy.env.workspace, output_table, input_table)

# Create a dictionary to store the records for each OVERLAP_OID
overlap_dict = defaultdict(list)

# Search the input table and add the records to the dictionary
with arcpy.da.SearchCursor(input_table, fields) as cursor:
    for row in cursor:
        overlap_dict[row[0]].append(row)

# Loop through the dictionary and process the records for each OVERLAP_OID
for overlap_oid, records in overlap_dict.items():
    if len(records) > 1:
        # Find the record with the maximum difference in FY_COMPLET - Ig_Year
        max_diff = max(records, key=lambda x: x[2] - x[3])
        # Check if there is a record with a maximum difference
        if max_diff[2] - max_diff[3] > 0:
            # Add the record with the maximum difference to the output table
            with arcpy.da.InsertCursor(output_table, fields) as cursor:
                cursor.insertRow(max_diff)
        else:
            # Find the record with the maximum Acres_within_Fire value
            max_acres = max(records, key=lambda x: x[4])
            # Add the record with the maximum Acres_within_Fire value to the output table
            with arcpy.da.InsertCursor(output_table, fields) as cursor:
                cursor.insertRow(max_acres)
    else:
        # Add the single record to the output table
        with arcpy.da.InsertCursor(output_table, fields) as cursor:
            cursor.insertRow(records[0])