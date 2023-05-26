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
arcpy.AddField_management("mtbs_perims_dd", "Ig_Year", "SHORT")

# Set the local variables
in_table = "mtbs_perims_DD"
field_name = "Ig_Year"
expression = "str(!Ig_Date!)[-4:]"
# Execute AddField
arcpy.AddField_management(in_table, field_name, "SHORT")
# Execute CalculateField
arcpy.CalculateField_management(in_table, field_name, expression, "PYTHON")

# Select records from mtbs_perims_dd that intersect Admin_Forests_R5 and filter where 1993 > Ig_Year < 2017
arcpy.MakeFeatureLayer_management("mtbs_perims_dd", "mtbs_lyr")
arcpy.SelectLayerByLocation_management("mtbs_lyr", "INTERSECT", "Admin_Forests_R5")
arcpy.SelectLayerByAttribute_management("mtbs_lyr", "SUBSET_SELECTION", "Ig_Year > 1993 AND Ig_Year < 2017")
arcpy.SelectLayerByAttribute_management("mtbs_lyr", "SUBSET_SELECTION", "Incid_Type = 'Wildfire'")

# Calculate geometry using US acres in field "Fire_Acres_R5"
arcpy.AddField_management("mtbs_lyr", "Fire_Acres", "SHORT")
arcpy.CalculateField_management("mtbs_lyr", "Fire_Acres", "!shape.area@acres!", "PYTHON3")

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


## Merge features before using Count Overlapping Features in order to have a single join field for reference 
# Set local variables
input_features = [f for f in arcpy.ListFeatureClasses() if "_int" in f]
field_mappings = arcpy.FieldMappings()
keep_fields = ["ADMIN_FO_1", "ADMIN_DIST", "SUID", "FACTS_ID", "SUBUNIT", "ACTIVITY_N", "NBR_UNITS_", "NBR_UNITS1", "DATE_COMPL", "FY_COMPLET", "PRODUCTI_1", "LAND_SUI_1", "SUBUNIT_SI", "CRC_VALUE", "GIS_ACRES", "Incid_Name", "BurnBndAc", "Ig_Year", "Fire_Acres_R5"]
output_feature = "Merged_Treatments"

# Create field mappings
for field in keep_fields:
    field_map = arcpy.FieldMap()
    field_map.addInputField(input_features[0], field)
    field_mappings.addFieldMap(field_map)

# Merge input features
arcpy.Merge_management(input_features, output_feature, field_mappings, "ADD_SOURCE_INFO")
arcpy.AddGeometryAttributes_management(output_feature, "AREA_GEODESIC", Area_Unit="ACRES_US")
arcpy.AlterField_management(output_feature, "AREA_GEO", "Acres_within_Fire", "Acres_within_Fire")

## Export subset of Activity_N related to reforestation
# Select records where FY_COMPLET > Ig_Year and ACTIVITY_N meets the specified criteria
where_clause = '"FY_COMPLET" > "Ig_Year" AND ("ACTIVITY_N" = \'Certification of Natural Regeneration without Site Prep\' Or "ACTIVITY_N" = \'Fill-in or Replant Trees\' Or "ACTIVITY_N" = \'Stocking Survey\' Or "ACTIVITY_N" = \'Plant Trees\' Or "ACTIVITY_N" = \'Salvage Cut (intermediate treatment, not regeneration)\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Burning\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Chemical\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Manual\' Or "ACTIVITY_N" = \'Site Preparation for Natural Regeneration - Mechanical\' Or "ACTIVITY_N" = \'Site Preparation for Planting - Mechanical\' Or "ACTIVITY_N" = \'Tree Release and Weed\')'
arcpy.Select_analysis(output_feature, "Merged_Postfire", where_clause)


## Summarize the burn severity in each reforestation subunit
#
for year in range(1993, 2018):
    if year == 1998:    # no postfire reforestation for fires in 1998
        continue
    # Select records from Merged_Postfire where Ig_Year is equal to the current year
    where_clause = "Ig_Year = {}".format(year)
    arcpy.SelectLayerByAttribute_management("Merged_Postfire", "NEW_SELECTION", where_clause)

    # Use Zonal Statistics as Table tool with Merged_Postfire as feature zone data
    input_raster = "mtbs_CA_{}.tif".format(year)
    output_table = "zonalst_merged_{}".format(year)
    arcpy.sa.ZonalStatisticsAsTable("Merged_Postfire", "SUID", input_raster, output_table, "NODATA", "ALL")
    arcpy.management.CalculateField(output_table, "Ig_Year", "{}".format(year), "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")

# Set the local variables
outTable = "zonalst_merged_allyears"
fieldMappings = arcpy.FieldMappings()
keepFields = ["OBJECTID", "SUID", "Ig_Year", "MIN", "MAX", "MEAN", "MEDIAN", "MAJORITY", "MINORITY"]

# Find all tables containing the text "zonalst_merged" in the name
tableList = [table for table in arcpy.ListTables() if "zonalst_merged" in table]

# Add the tables to the field mappings and retain only the specified fields
for table in tableList:
    fieldMappings.addTable(table)
    for field in fieldMappings.fields:
        if field.name not in keepFields:
            fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))

# Merge the tables
arcpy.Merge_management(tableList, outTable, fieldMappings)

# # Round MEAN field to nearest single digit
# with arcpy.da.UpdateCursor("zonalst_merged_allyears", ["MEAN"]) as cursor:
#     for row in cursor:
#         row[0] = round(row[0])
#         cursor.updateRow(row)

## Join zonal stats table with Merged_Postfire
# Set the local variables
in_data = "Merged_Postfire"
in_field = "SUID"
join_table = "zonalst_merged_allyears"
join_field = "SUID"

# Join the two tables by the SUID field
arcpy.JoinField_management(in_data, in_field, join_table, join_field)



## Count Overlapping Features for all records in all postfire activities

# Wherever two or more records overlap, new polygons are generated with distinct IDs;
# a table identifying each overlap is then joined with the treatment and overlap features.

# This allows for summarization of each treatment type and all treatment combinations 
# as well as retaining the information of each intra/inter-duplicating record.

from arcpy import env
env.workspace = r"C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\phase1_2023.gdb"


# Set local variables
input_features = "Merged_Postfire"
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
arcpy.management.AddJoin("Overlap_Table_Joined", "OVERLAP_OID", output_feature, "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")

# Export table to csv to be used for overlap summarization
arcpy.TableToTable_conversion("Overlap_Table_Joined", r"C:\Users\smithke3\OneDrive - Oregon State University\Kelly\Data", "Postfire_Overlaps.csv")