import arcpy
import os


## Set workspace
##
arcpy.env.workspace = r"C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\phase1_2023.gdb"


## Subset MTBS layer --> Select by Location (R5 Admin Forests) & Filter (1993 > Ig_Year < 2017)
## 
# INSERT CODE HERE

## Convert MTBS datetime object to string for extracting year
##
arcpy.management.CalculateField("mtbs_wildfires_CA_1993_2017", "Ig_Year", "!Ig_Date!.strftime('%m/%d/%Y')", "PYTHON3", '', "DATE", "NO_ENFORCE_DOMAINS")

########## MANUALLY ADD YEAR FIELD HERE ##########

    # Export table,
    # extract YEAR from string in Excel,
    # remove extra fields,
    # join table with feature,
    # export joined feature "..._f1"


## Calculate new acres in MTBS layer after clipping to forest layer
##
arcpy.management.CalculateGeometryAttributes("mtbs_wildfires_CA_1993_2017_f1", "Fire_GIS_Acres AREA_GEODESIC", '', "ACRES_US", 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', "SAME_AS_INPUT")

## Add burn severity rasters to mosaic dataset
##
arcpy.management.AddRastersToMosaicDataset("BurnSevRasters", "Raster Dataset", r"'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2017.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1993.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1994.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1995.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1996.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1997.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1998.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_1999.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2000.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2001.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2002.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2003.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2004.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2005.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2006.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2007.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2008.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2009.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2010.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2011.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2012.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2013.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2014.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2015.tif';'C:\Users\smithke3\OneDrive - Oregon State University\_Thesis\phase1\phase1_2023\MTBS_BSmosaics_CA\mtbs_CA_2016.tif'", "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", r"C:\Users\smithke3\AppData\Local\ESRI\rasterproxies\BurnSevRasters")


## Convert burn severity rasters to points
arcpy.conversion.RasterToPoint("mtbs_CA_1993", "mtbs_1993_pts", "Value")



## Intersect FACTS layers with MTBS layer
##
arcpy.analysis.PairwiseIntersect("S_USA.Activity_SilvReforestation;mtbs_wildfires_CA_1993_2017_f1", "Refor_fires_int", "ALL", None, "INPUT")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_SilvTSI;mtbs_wildfires_CA_1993_2017_f1", "TSI_fires_int", "ALL", None, "INPUT")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_TimberHarvest;mtbs_wildfires_CA_1993_2017_f1", "Harvest_fires_int", "ALL", None, "INPUT")

## Subset unique Stewardship Activities related to reforestation
arcpy.management.SelectLayerByAttribute("S_USA.Activity_StwrdshpCntrctng_PL", "NEW_SELECTION", "ACTIVITY_N = 'Control of Understory Vegetation' Or ACTIVITY_N = 'Stocking Survey' Or ACTIVITY_N = 'Site Preparation for Planting - Mechanical'")
arcpy.analysis.PairwiseIntersect("S_USA.Activity_StwrdshpCntrctng_PL;mtbs_wildfires_CA_1993_2017_f1", "Steward_fires_int", "ALL", None, "INPUT")


## Calculate geometry of treatment polygons after intersecting with MTBS layer (area within fire perimeter)
##
arcpy.management.CalculateGeometryAttributes("Refor_fires_int", "Acres_within_Fire AREA_GEODESIC", '', "ACRES_US", None, "SAME_AS_INPUT")
arcpy.management.CalculateGeometryAttributes("TSI_fires_int", "Acres_within_Fire AREA_GEODESIC", '', "ACRES_US", None, "SAME_AS_INPUT")
arcpy.management.CalculateGeometryAttributes("Harvest_fires_int", "Acres_within_Fire AREA_GEODESIC", '', "ACRES_US", None, "SAME_AS_INPUT")
arcpy.management.CalculateGeometryAttributes("Steward_fires_int", "Acres_within_Fire AREA_GEODESIC", '', "ACRES_US", None, "SAME_AS_INPUT")



## Merge features before using Count Overlapping Features in order to have a single join field for reference 
##
## is Field Mapping needed in order to subset fields? Maybe just merge all and then subset fields in dplyr?
arcpy.management.Merge("Refor_fires_int;TSI_fires_int;Steward_fires_int;Harvest_fires_int", "Merged_Treatments", 'ADMIN_FO_1 "ADMIN_FO_1" true true false 60 Text 0 0,First,#,Refor_fires_int,ADMIN_FO_1,0,60,TSI_fires_int,ADMIN_FO_1,0,60,Steward_fires_int,ADMIN_FO_1,0,150,Harvest_fires_int,ADMIN_FO_1,0,150;ADMIN_DIST "ADMIN_DIST" true true false 60 Text 0 0,First,#,Refor_fires_int,ADMIN_DIST,0,60,TSI_fires_int,ADMIN_DIST,0,60,Steward_fires_int,ADMIN_DIST,0,150,Harvest_fires_int,ADMIN_DIST,0,150;SUID "SUID" true true false 19 Text 0 0,First,#,Refor_fires_int,SUID,0,19,TSI_fires_int,SUID,0,19,Steward_fires_int,SUID,0,19,Harvest_fires_int,SUID,0,19;FACTS_ID "FACTS_ID" true true false 10 Text 0 0,First,#,Refor_fires_int,FACTS_ID,0,10,TSI_fires_int,FACTS_ID,0,10,Steward_fires_int,FACTS_ID,0,10,Harvest_fires_int,FACTS_ID,0,10;SUBUNIT "SUBUNIT" true true false 3 Text 0 0,First,#,Refor_fires_int,SUBUNIT,0,3,TSI_fires_int,SUBUNIT,0,3,Steward_fires_int,SUBUNIT,0,3,Harvest_fires_int,SUBUNIT,0,3;ACTIVITY_N "ACTIVITY_N" true true false 80 Text 0 0,First,#,Refor_fires_int,ACTIVITY_N,0,80,TSI_fires_int,ACTIVITY_N,0,80,Steward_fires_int,ACTIVITY_N,0,80,Harvest_fires_int,ACTIVITY_N,0,80;NBR_UNITS_ "NBR_UNITS_" true true false 8 Double 0 0,First,#,Refor_fires_int,NBR_UNITS_,-1,-1,TSI_fires_int,NBR_UNITS_,-1,-1,Steward_fires_int,NBR_UNITS_,-1,-1,Harvest_fires_int,NBR_UNITS_,-1,-1;NBR_UNITS1 "NBR_UNITS1" true true false 8 Double 0 0,First,#,Refor_fires_int,NBR_UNITS1,-1,-1,TSI_fires_int,NBR_UNITS1,-1,-1,Steward_fires_int,NBR_UNITS1,-1,-1,Harvest_fires_int,NBR_UNITS1,-1,-1;DATE_COMPL "DATE_COMPL" true true false 8 Date 0 0,First,#,Refor_fires_int,DATE_COMPL,-1,-1,TSI_fires_int,DATE_COMPL,-1,-1,Steward_fires_int,DATE_COMPL,-1,-1,Harvest_fires_int,DATE_COMPL,-1,-1;FY_COMPLET "FY_COMPLET" true true false 4 Long 0 0,First,#,Refor_fires_int,FY_COMPLET,-1,-1,TSI_fires_int,FY_COMPLET,-1,-1,Steward_fires_int,FY_COMPLET,0,4,Harvest_fires_int,FY_COMPLET,0,4;COST_PER_U "COST_PER_U" true true false 8 Double 0 0,First,#,Refor_fires_int,COST_PER_U,-1,-1,TSI_fires_int,COST_PER_U,-1,-1,Steward_fires_int,COST_PER_U,-1,-1,Harvest_fires_int,COST_PER_U,-1,-1;METHOD_DES "METHOD_DES" true true false 40 Text 0 0,First,#,Refor_fires_int,METHOD_DES,0,40,TSI_fires_int,METHOD_DES,0,40,Steward_fires_int,METHOD_DES,0,50,Harvest_fires_int,METHOD_DES,0,50;EQUIPMENT1 "EQUIPMENT1" true true false 80 Text 0 0,First,#,Refor_fires_int,EQUIPMENT1,0,80,TSI_fires_int,EQUIPMENT1,0,80,Steward_fires_int,EQUIPMENT1,0,80,Harvest_fires_int,EQUIPMENT1,0,80;PRODUCTI_1 "PRODUCTI_1" true true false 50 Text 0 0,First,#,Refor_fires_int,PRODUCTI_1,0,50,TSI_fires_int,PRODUCTI_1,0,50,Harvest_fires_int,PRODUCTI_1,0,50;LAND_SUI_1 "LAND_SUI_1" true true false 150 Text 0 0,First,#,Refor_fires_int,LAND_SUI_1,0,150,TSI_fires_int,LAND_SUI_1,0,150,Harvest_fires_int,LAND_SUI_1,0,50;SUBUNIT_CN "SUBUNIT_CN" true true false 34 Text 0 0,First,#,Refor_fires_int,SUBUNIT_CN,0,34,TSI_fires_int,SUBUNIT_CN,0,34,Steward_fires_int,SUBUNIT_CN,0,34,Harvest_fires_int,SUBUNIT_CN,0,34;SUBUNIT_SI "SUBUNIT_SI" true true false 8 Double 0 0,First,#,Refor_fires_int,SUBUNIT_SI,-1,-1,TSI_fires_int,SUBUNIT_SI,-1,-1,Steward_fires_int,SUBUNIT_SI,-1,-1,Harvest_fires_int,SUBUNIT_SI,-1,-1;CRC_VALUE "CRC_VALUE" true true false 50 Text 0 0,First,#,Refor_fires_int,CRC_VALUE,0,50,TSI_fires_int,CRC_VALUE,0,50,Steward_fires_int,CRC_VALUE,0,50,Harvest_fires_int,CRC_VALUE,0,50;GIS_ACRES "GIS_ACRES" true true false 8 Double 0 0,First,#,Refor_fires_int,GIS_ACRES,-1,-1,TSI_fires_int,GIS_ACRES,-1,-1,Steward_fires_int,GIS_ACRES,-1,-1,Harvest_fires_int,GIS_ACRES,-1,-1;Event_ID "Event_ID" true true false 254 Text 0 0,First,#,Refor_fires_int,Event_ID,0,254,TSI_fires_int,Event_ID,0,254,Steward_fires_int,Event_ID,0,254,Harvest_fires_int,Event_ID,0,254;Incid_Name "Incid_Name" true true false 254 Text 0 0,First,#,Refor_fires_int,Incid_Name,0,254,TSI_fires_int,Incid_Name,0,254,Steward_fires_int,Incid_Name,0,254,Harvest_fires_int,Incid_Name,0,254;BurnBndAc "BurnBndAc" true true false 4 Long 0 0,First,#,Refor_fires_int,BurnBndAc,-1,-1,TSI_fires_int,BurnBndAc,-1,-1,Steward_fires_int,BurnBndAc,-1,-1,Harvest_fires_int,BurnBndAc,-1,-1;Ig_Date "Ig_Date" true true false 8 Date 0 0,First,#,Refor_fires_int,Ig_Date,-1,-1,TSI_fires_int,Ig_Date,-1,-1,Steward_fires_int,Ig_Date,-1,-1,Harvest_fires_int,Ig_Date,-1,-1;dNBR_offst "dNBR_offst" true true false 4 Long 0 0,First,#,Refor_fires_int,dNBR_offst,-1,-1,TSI_fires_int,dNBR_offst,-1,-1,Steward_fires_int,dNBR_offst,-1,-1,Harvest_fires_int,dNBR_offst,-1,-1;dNBR_stdDv "dNBR_stdDv" true true false 4 Long 0 0,First,#,Refor_fires_int,dNBR_stdDv,-1,-1,TSI_fires_int,dNBR_stdDv,-1,-1,Steward_fires_int,dNBR_stdDv,-1,-1,Harvest_fires_int,dNBR_stdDv,-1,-1;NoData_T "NoData_T" true true false 4 Long 0 0,First,#,Refor_fires_int,NoData_T,-1,-1,TSI_fires_int,NoData_T,-1,-1,Steward_fires_int,NoData_T,-1,-1,Harvest_fires_int,NoData_T,-1,-1;IncGreen_T "IncGreen_T" true true false 4 Long 0 0,First,#,Refor_fires_int,IncGreen_T,-1,-1,TSI_fires_int,IncGreen_T,-1,-1,Steward_fires_int,IncGreen_T,-1,-1,Harvest_fires_int,IncGreen_T,-1,-1;Low_T "Low_T" true true false 4 Long 0 0,First,#,Refor_fires_int,Low_T,-1,-1,TSI_fires_int,Low_T,-1,-1,Steward_fires_int,Low_T,-1,-1,Harvest_fires_int,Low_T,-1,-1;Mod_T "Mod_T" true true false 4 Long 0 0,First,#,Refor_fires_int,Mod_T,-1,-1,TSI_fires_int,Mod_T,-1,-1,Steward_fires_int,Mod_T,-1,-1,Harvest_fires_int,Mod_T,-1,-1;High_T "High_T" true true false 4 Long 0 0,First,#,Refor_fires_int,High_T,-1,-1,TSI_fires_int,High_T,-1,-1,Steward_fires_int,High_T,-1,-1,Harvest_fires_int,High_T,-1,-1;Ig_Date_Str "Ig_Date_Str" true true false 8 Date 0 0,First,#,Refor_fires_int,Ig_Date_Str,-1,-1,TSI_fires_int,Ig_Date_Str,-1,-1,Steward_fires_int,Ig_Date_Str,-1,-1,Harvest_fires_int,Ig_Date_Str,-1,-1;Ig_Year "Ig_Year" true true false 4 Long 0 0,First,#,Refor_fires_int,Ig_Year,-1,-1,TSI_fires_int,Ig_Year,-1,-1,Steward_fires_int,Ig_Year,-1,-1,Harvest_fires_int,Ig_Year,-1,-1;Fire_Acres_R5 "Fire_Acres_R5" true true false 8 Double 0 0,First,#,Refor_fires_int,Fire_Acres_R5,-1,-1,TSI_fires_int,Fire_Acres_R5,-1,-1,Steward_fires_int,Fire_Acres_R5,-1,-1,Harvest_fires_int,Fire_Acres_R5,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Refor_fires_int,Shape_Length,-1,-1,TSI_fires_int,Shape_Length,-1,-1,Steward_fires_int,Shape_Length,-1,-1,Harvest_fires_int,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,Refor_fires_int,Shape_Area,-1,-1,TSI_fires_int,Shape_Area,-1,-1,Steward_fires_int,Shape_Area,-1,-1,Harvest_fires_int,Shape_Area,-1,-1;Acres_within_Fire "Acres_within_Fire" true true false 8 Double 0 0,First,#,Refor_fires_int,Acres_within_Fire,-1,-1,TSI_fires_int,Acres_within_Fire,-1,-1,Steward_fires_int,Acres_within_Fire,-1,-1,Harvest_fires_int,Acres_within_Fire,-1,-1', "ADD_SOURCE_INFO")


## Export subset of Activity_N related to reforestation
##
arcpy.management.SelectLayerByAttribute("Merged_Treatments", "NEW_SELECTION", "FY_COMPLET > Ig_Year", None)
arcpy.analysis.PairwiseClip("Merged_Treatments", "Merged_Treatments", "Merged_Postfire", None)

## arcpy.management.CalculateField("Merged_Postfire", "DATE_COMP_STR", "!DATE_COMPL!.strftime('%m/%d/%Y')", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

arcpy.management.SelectLayerByAttribute("Merged_Postfire", "NEW_SELECTION", "ACTIVITY_N = 'Certification of Natural Regeneration without Site Prep' Or ACTIVITY_N = 'Fill-in or Replant Trees' Or ACTIVITY_N = 'Stocking Survey' Or ACTIVITY_N = 'Plant Trees' Or ACTIVITY_N = 'Salvage Cut (intermediate treatment, not regeneration)' Or ACTIVITY_N = 'Site Preparation for Natural Regeneration - Burning'  Or ACTIVITY_N = 'Site Preparation for Natural Regeneration - Chemical'  Or ACTIVITY_N = 'Site Preparation for Natural Regeneration - Manual'  Or ACTIVITY_N = 'Site Preparation for Natural Regeneration - Mechanical' Or ACTIVITY_N = 'Site Preparation for Planting - Mechanical' Or ACTIVITY_N = 'Tree Release and Weed'", None)
arcpy.analysis.PairwiseClip("Merged_Postfire", "Merged_Postfire", "Merged_Regen_Postfire", None)



##
## Count Overlapping Features for all records in all postfire activities
##      Wherever two or more records overlap, new polygons are generated with distinct IDs
##      This allows for summarization of each treatment type as well as retaining the information of each intra/inter-duplicating record
##      i.e. rates of planting/replanting and/or release treatment within 5 years after fire
##
arcpy.analysis.CountOverlappingFeatures("Merged_Regen_Postfire", "Overlap_Feature", 1, "Overlap_Table")


## Calculate OVERLAP_acres
arcpy.management.CalculateGeometryAttributes("Overlap_Feature", "OVERLAP_acres AREA_GEODESIC", '', "ACRES_US", None, "SAME_AS_INPUT")


## Join tables from Overlap_Table and Merged postfire treatments, linking each overlap to a record from the treatment layer
## Export table
## 
arcpy.management.AddJoin("Overlap_Table", "ORIG_OID", "Merged_Regen_Postfire", "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")
arcpy.conversion.ExportTable("Overlap_Table", "Overlap_Table_joined", '', "USE_ALIAS", None)


## Join Overlap_Feature with joined overlap table and export
##      create table/feature where each overlap is appended with activity record
##
arcpy.management.AddJoin("Overlap_Table_joined", "OVERLAP_OID", "Overlap_Feature", "OBJECTID", "KEEP_ALL", "NO_INDEX_JOIN_FIELDS")



## Export table from joined overlap table to \Data
## arcpy.conversion.TableToTable("Overlap_Table_joined", r"C:\Users\smithke3\OneDrive - Oregon State University\Kelly\Data", "Postfire_Overlaps_f1.csv",'','',-1)
arcpy.conversion.TableToTable("Overlap_Table_joined", r"C:\Users\smithke3\OneDrive - Oregon State University\Kelly\Data", "Postfire_Overlaps_f2.csv", '', 'OVERLAP_OID "OVERLAP_OID" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.OVERLAP_OID,-1,-1;ORIG_OID "ORIG_OID" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.ORIG_OID,-1,-1;ORIG_NAME "ORIG_NAME" true true false 512 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.ORIG_NAME,0,512;ADMIN_FO_1 "ADMIN_FO_1" true true false 60 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.ADMIN_FO_1,0,60;ADMIN_DIST "ADMIN_DIST" true true false 60 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.ADMIN_DIST,0,60;SUID "SUID" true true false 19 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.SUID,0,19;FACTS_ID "FACTS_ID" true true false 10 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.FACTS_ID,0,10;SUBUNIT "SUBUNIT" true true false 3 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.SUBUNIT,0,3;ACTIVITY_N "ACTIVITY_N" true true false 80 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.ACTIVITY_N,0,80;NBR_UNITS_ "NBR_UNITS_" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.NBR_UNITS_,-1,-1;NBR_UNITS1 "NBR_UNITS1" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.NBR_UNITS1,-1,-1;DATE_COMPL "DATE_COMPL" true true false 8 Date 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.DATE_COMPL,-1,-1;FY_COMPLET "FY_COMPLET" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.FY_COMPLET,-1,-1;COST_PER_U "COST_PER_U" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.COST_PER_U,-1,-1;METHOD_DES "METHOD_DES" true true false 40 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.METHOD_DES,0,40;EQUIPMENT1 "EQUIPMENT1" true true false 80 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.EQUIPMENT1,0,80;PRODUCTI_1 "PRODUCTI_1" true true false 50 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.PRODUCTI_1,0,50;LAND_SUI_1 "LAND_SUI_1" true true false 150 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.LAND_SUI_1,0,150;SUBUNIT_CN "SUBUNIT_CN" true true false 34 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.SUBUNIT_CN,0,34;SUBUNIT_SI "SUBUNIT_SI" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.SUBUNIT_SI,-1,-1;CRC_VALUE "CRC_VALUE" true true false 50 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.CRC_VALUE,0,50;GIS_ACRES "GIS_ACRES" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.GIS_ACRES,-1,-1;Event_ID "Event_ID" true true false 254 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Event_ID,0,254;Incid_Name "Incid_Name" true true false 254 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Incid_Name,0,254;BurnBndAc "BurnBndAc" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.BurnBndAc,-1,-1;Ig_Date "Ig_Date" true true false 8 Date 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Ig_Date,-1,-1;dNBR_offst "dNBR_offst" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.dNBR_offst,-1,-1;dNBR_stdDv "dNBR_stdDv" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.dNBR_stdDv,-1,-1;NoData_T "NoData_T" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.NoData_T,-1,-1;IncGreen_T "IncGreen_T" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.IncGreen_T,-1,-1;Low_T "Low_T" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Low_T,-1,-1;Mod_T "Mod_T" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Mod_T,-1,-1;High_T "High_T" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.High_T,-1,-1;Ig_Date_Str "Ig_Date_Str" true true false 8 Date 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Ig_Date_Str,-1,-1;Ig_Year "Ig_Year" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Ig_Year,-1,-1;Fire_Acres_R5 "Fire_Acres_R5" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Fire_Acres_R5,-1,-1;Acres_within_Fire "Acres_within_Fire" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Acres_within_Fire,-1,-1;MERGE_SRC "MERGE_SRC" true true false 255 Text 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.MERGE_SRC,0,255;Shape_Length "Shape_Length" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Shape_Length,-1,-1;Shape_Area "Shape_Area" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Table_joined.Shape_Area,-1,-1;OBJECTID "OBJECTID" false true false 4 Long 0 9,First,#,Overlap_Table_joined,Overlap_Feature.OBJECTID,-1,-1;COUNT_ "COUNT_" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Feature.COUNT_,-1,-1;COUNT_FC "COUNT_FC" true true false 4 Long 0 0,First,#,Overlap_Table_joined,Overlap_Feature.COUNT_FC,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Feature.Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Feature.Shape_Area,-1,-1;OVERLAP_acres "OVERLAP_acres" true true false 8 Double 0 0,First,#,Overlap_Table_joined,Overlap_Feature.OVERLAP_acres,-1,-1', '')
arcpy.conversion.ExportTable("Overlap_Table_joined", r"C:\Users\smithke3\OneDrive - Oregon State University\Kelly\Data\Postfire_Overlaps_f2.csv", '', "USE_ALIAS", None)
