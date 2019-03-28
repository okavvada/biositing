import pandas as pd
import geopandas as gpd
import os, sys
import numpy as np
from functions import getBiomassInCountiesAll, loadDatasets, getPointGeoDataFrame

class dataProcess():
    def __init__(self, xls_path):
        pd.options.mode.chained_assignment = None
        print("Reading in data...")
        print("this will take a few minutes, please wait...")
        self.read_xls_data(xls_path)
        self.drop_duplicate_data()
        print("Reading in shapefiles...")
        self.read_shapefiles()
        print("Processing data...")
        self.cbg_thermalrun_gpd_all = self.simplify_thermal_shapes()
        self.cbg_thermalrun_gpd_all_dissolved = self.dissolve_thermal_shapes()
        self.merge_data_shapefiles()
        self.reproject_shapefiles()
        self.county_with_totals = self.calculate_county_totals()
        self.cbg_thermalrun_gpd_all_dissolved_county = self.add_county_to_thermal()
        self.fill_nas()
        print("Saving to file...")
        self.save_to_csvs()


    def read_xls_data(self, xls_path):
        """
        Reads in the tabs from the xls file listed in the bottom of the file
        """
        self.manure_pts = pd.read_excel(xls_path, sheetname='manure_pts')
        self.manure_nonpts = pd.read_excel(xls_path, sheetname='manure_nonpts')
        self.msw_CBGcntrd = pd.read_excel(xls_path, sheetname='msw_CBGcntrd')
        self.crp2016_pts = pd.read_excel(xls_path, sheetname='crp2016_pts')
        self.crp2020_pts = pd.read_excel(xls_path, sheetname='crp2020_pts')
        self.crp2050_pts = pd.read_excel(xls_path, sheetname='crp2050_pts')
        self.proc_pts = pd.read_excel(xls_path, sheetname='proc_pts')
        self.proc_nonpts = pd.read_excel(xls_path, sheetname='proc_nonpts')
        self.DES_CBGcntrd = pd.read_excel(xls_path, sheetname='DES_CBGcntrd')
        self.MUD_nonpt = pd.read_excel(xls_path, sheetname='MUD_nonpt')
        self.PROC_ZCcntrd = pd.read_excel(xls_path, sheetname='PROC_ZCcntrd')
        self.COMB_pts = pd.read_excel(xls_path, sheetname='COMB_pts')
        self.AD_pts = pd.read_excel(xls_path, sheetname='AD_pts')
        self.W2E_pts = pd.read_excel(xls_path, sheetname='W2E_pts')

    def drop_duplicate_data(self):
        """
        Drops in case there are duplicate entries in the xls
        """
        columns_manure = self.manure_pts.columns.drop(['FID', 'OBJECTID', u'WDID'],1)
        columns_manure_nonpts = self.manure_nonpts.columns.drop(['OBJECTID'],1)
        columns_msw_CBGcntrd = self.msw_CBGcntrd.columns.drop(['FID', 'OBJECTID'],1)
        columns_crp2016_pts = self.crp2016_pts.columns.drop(['FID'],1)
        columns_crp2020_pts = self.crp2020_pts.columns.drop(['FID'],1)
        columns_crp2050_pts = self.crp2050_pts.columns.drop(['FID','OBJECTID'],1)
        columns_proc_pts = self.proc_pts.columns.drop(['FID'],1)
        columns_proc_nonpts = self.proc_nonpts.columns.drop(['OBJECTID'],1)
        columns_DES_CBGcntrd = self.DES_CBGcntrd.columns.drop([u'FID', u'CBGID', u'Name', u'System', u'OBJECTID'],1)
        columns_MUD_nonpt = self.MUD_nonpt.columns.drop(['OBJECTID'],1)
        columns_PROC_ZCcntrd = self.PROC_ZCcntrd.columns.drop(['OBJECTID'],1)
        columns_COMB_pts = self.COMB_pts.columns.drop(['OBJECTID'],1)
        columns_AD_pts = self.AD_pts.columns.drop(['FID', 'OBJECTID'],1)
        columns_W2E_pts = self.W2E_pts.columns.drop(['OBJECTID'],1)

        self.manure_pts = self.manure_pts.drop_duplicates(subset=columns_manure)
        self.manure_nonpts = self.manure_nonpts.drop_duplicates(subset=columns_manure_nonpts)
        self.msw_CBGcntrd = self.msw_CBGcntrd.drop_duplicates(subset=columns_msw_CBGcntrd)
        self.crp2016_pts = self.crp2016_pts.drop_duplicates(subset=columns_crp2016_pts)
        self.crp2020_pts = self.crp2020_pts.drop_duplicates(subset=columns_crp2020_pts)
        self.crp2050_pts = self.crp2050_pts.drop_duplicates(subset=columns_crp2050_pts)
        self.proc_pts = self.proc_pts.drop_duplicates(subset=columns_proc_pts)
        self.proc_nonpts = self.proc_nonpts.drop_duplicates(subset=columns_proc_nonpts)
        self.DES_CBGcntrd = self.DES_CBGcntrd.drop_duplicates(subset=columns_DES_CBGcntrd)
        self.MUD_nonpt = self.MUD_nonpt.drop_duplicates(subset=columns_MUD_nonpt)
        self.PROC_ZCcntrd = self.PROC_ZCcntrd.drop_duplicates(subset=columns_PROC_ZCcntrd)
        self.COMB_pts = self.COMB_pts.drop_duplicates(subset=columns_COMB_pts)
        self.AD_pts = self.AD_pts.drop_duplicates(subset=columns_AD_pts)
        self.W2E_pts = self.W2E_pts.drop_duplicates(subset=columns_W2E_pts)

    def read_shapefiles(self):
        """
        Reads in the shapefiles
        """
        self.manure_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/CAFO.shp')
        self.crp2016_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/crop_groupcentroid2016.shp')
        self.crp2020_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/crop_groupcentroid2020.shp')
        self.crp2050_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/crop_groupcentroid2050.shp')
        self.msw_CBGcntrd_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/CTcentroidformMSW.shp')
        self.proc_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/FoodProcessors_LBNL_7_20_17wcounty.shp')
        self.DES_CBGcntrd_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/CBGcentroidforDES.shp')
        self.MUD_nonpt_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/CA_Counties_Simple.shp')
        self.PROC_ZCcntrd_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/Zccentroidfoodprocenergy.shp')
        self.COMB_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/COMB_rev.shp')
        self.AD_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/WWTFbynearestcity.shp')
        self.W2E_pts_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/organics_facilities.shp')
        self.counties_gpd = gpd.read_file('GIS_data/Shapefile_Drafts/CA_Counties_Simple.shp')

    def simplify_thermal_shapes(self):
        """
        Simplifies the thermal shapes by dusing a simplified census boundary
        """
        cbg_thermalrun02016 = gpd.read_file('GIS_data/Shapefile_Drafts/2016cbgRun0_simple.shp')
        cbg_thermalrun02016_original = gpd.read_file('GIS_data/Shapefile_Drafts/2016cbgRun0.shp')
        cbg_thermalrun02020_original = gpd.read_file('GIS_data/Shapefile_Drafts/2020cbgRun0.shp')
        cbg_thermalrun02050_original = gpd.read_file('GIS_data/Shapefile_Drafts/2050cbgRun0.shp')

        crs_init = cbg_thermalrun02016_original.crs
        cbg_thermalrun02016.crs = crs_init
        crs = {'init': 'epsg:4326'}
        cbg_thermalrun02016 = cbg_thermalrun02016.to_crs(crs)

        cbg_thermalrun02016_original = cbg_thermalrun02016_original.drop(['geometry'], axis=1)
        cbg_thermalrun02020_original = cbg_thermalrun02020_original.drop(['geometry'], axis=1)
        cbg_thermalrun02050_original = cbg_thermalrun02050_original.drop(['geometry'], axis=1)

        cbg_thermalrun02016_gpd = pd.merge(cbg_thermalrun02016_original, cbg_thermalrun02016, left_index=True, right_index=True, how='left')

        cbg_thermalrun02016_gpd.loc[:,('SUM_TotC16')] = cbg_thermalrun02016_gpd['CDenArea']
        cbg_thermalrun02016_gpd.loc[:,('SUM_TotH16')] = cbg_thermalrun02016_gpd['HDenArea']
        cbg_thermalrun02020_original.loc[:,('SUM_TotC20')] = cbg_thermalrun02020_original['CDenArea']
        cbg_thermalrun02020_original.loc[:,('SUM_TotH20')] = cbg_thermalrun02020_original['HDenArea']
        cbg_thermalrun02050_original.loc[:,('SUM_TotC50')] = cbg_thermalrun02050_original['CDenArea']
        cbg_thermalrun02050_original.loc[:,('SUM_TotH50')] = cbg_thermalrun02050_original['HDenArea']
        cbg_thermalrun02020_gpd = cbg_thermalrun02020_original[['OBJECTID', 'SUM_TotC20', 'SUM_TotH20']]
        cbg_thermalrun02050_gpd = cbg_thermalrun02050_original[['OBJECTID', 'SUM_TotC50', 'SUM_TotH50']]
        cbg_thermalrun_gpd = pd.merge(cbg_thermalrun02016_gpd, cbg_thermalrun02020_gpd, left_on='OBJECTID', right_on='OBJECTID', how='left')
        cbg_thermalrun_gpd = cbg_thermalrun_gpd[['OBJECTID', 'SUM_TotC20', 'SUM_TotH20', 'SUM_TotC16', 'SUM_TotH16', 'geometry']]

        cbg_thermalrun_gpd_all = gpd.GeoDataFrame(pd.merge(cbg_thermalrun_gpd, cbg_thermalrun02050_gpd, left_on='OBJECTID', right_on='OBJECTID', how='left'))
        cbg_thermalrun_gpd_all.crs = crs
        return cbg_thermalrun_gpd_all

    def dissolve_thermal_shapes(self):
        """
        Simplifies the thermal shapes by dissolving together all the polygons that have 0 values for all 3 years
        """
        self.cbg_thermalrun_gpd_all.loc[:,('Dissolve')] = np.where(((self.cbg_thermalrun_gpd_all['SUM_TotH16']==0) & 
                                           (self.cbg_thermalrun_gpd_all['SUM_TotC16']==0) & 
                                           (self.cbg_thermalrun_gpd_all['SUM_TotC50']==0) & 
                                           (self.cbg_thermalrun_gpd_all['SUM_TotH50']==0) &
                                           (self.cbg_thermalrun_gpd_all['SUM_TotC20']==0) & 
                                           (self.cbg_thermalrun_gpd_all['SUM_TotH20']==0)), 'novals', 'havevals')
        dissolved = self.cbg_thermalrun_gpd_all.dissolve(by='Dissolve')
        dissolved.loc[:,('Dissolve')] = dissolved.index
        cbg_dissolved_novals = dissolved[dissolved['Dissolve']=='novals']
        cbg_thermalrun_gpd_withvals = self.cbg_thermalrun_gpd_all[self.cbg_thermalrun_gpd_all['Dissolve']=='havevals']
        cbg_thermal_gpd_final = gpd.GeoDataFrame(pd.concat([cbg_thermalrun_gpd_withvals,cbg_dissolved_novals], ignore_index=True))
        cbg_thermal_gpd_final.crs = {'init': 'epsg:4326'}
        return cbg_thermal_gpd_final

    def add_county_to_thermal(self):
        """
        Adds a column with the CID of the county in which the census block is in
        """
        counties_df_geom = self.county_with_totals[['CID', 'geometry']]
        cbg_thermalrun_gpd = gpd.sjoin(self.cbg_thermalrun_gpd_all_dissolved, counties_df_geom, how="left", op='intersects')
        cbg_thermal_gpd_final_dup = cbg_thermalrun_gpd.drop_duplicates(subset=['OBJECTID'])
        cbg_thermalrun_gpd_all_dissolved_county = cbg_thermal_gpd_final_dup.copy()
        cbg_thermalrun_gpd_all_dissolved_county.loc[:,('FID')] = cbg_thermal_gpd_final_dup.loc[:,('OBJECTID')]
        return cbg_thermalrun_gpd_all_dissolved_county

    def merge_data_shapefiles(self):
        """
        Merge the data from the xls file to the shapefiles to get geometries
        """
        self.PROC_ZCcntrd_gpd.loc[:,('ZIPCODE')] = [int(item) for item in self.PROC_ZCcntrd_gpd['ZIP_CODE']]
        manure_pts_gpd = self.manure_pts_gpd[['geometry', 'OBJECTID']]
        crp2016_pts_gpd = self.crp2016_pts_gpd[['geometry']]
        crp2020_pts_gpd = self.crp2020_pts_gpd[['geometry']]
        crp2050_pts_gpd = self.crp2050_pts_gpd[['geometry']]
        msw_CBGcntrd_gpd = self.msw_CBGcntrd_gpd[['geometry']]
        proc_pts_gpd = self.proc_pts_gpd[['geometry']]

        DES_CBGcntrd_gpd = self.DES_CBGcntrd_gpd[['geometry']]
        MUD_nonpt_gpd = self.MUD_nonpt_gpd[['geometry', 'NAME']]
        self.counties_gpd = self.counties_gpd[['geometry', 'NAME']]
        PROC_ZCcntrd_gpd = self.PROC_ZCcntrd_gpd[['geometry', 'ZIPCODE']]
        COMB_pts_gpd = self.COMB_pts_gpd[['geometry', 'NAME']]
        AD_pts_gpd = self.AD_pts_gpd[['geometry', 'NAME']]
        W2E_pts_gpd = self.W2E_pts_gpd[['geometry', 'NAME']]
        self.counties_gpd.loc[:,('County')] = self.counties_gpd['NAME']

        self.manure_pts_gpd_final = pd.merge(manure_pts_gpd, self.manure_pts, left_on='OBJECTID', right_on='OBJECTID', how='right')
        self.crp2016_pts_gpd_final = pd.merge(crp2016_pts_gpd, self.crp2016_pts, left_index=True, right_on='FID', how='right')
        self.crp2020_pts_gpd_final = pd.merge(crp2020_pts_gpd, self.crp2020_pts, left_index=True, right_on='FID', how='right')
        self.crp2050_pts_gpd_final = pd.merge(crp2050_pts_gpd, self.crp2050_pts, left_index=True, right_on='FID', how='right')
        self.msw_CBGcntrd_gpd_final = pd.merge(msw_CBGcntrd_gpd, self.msw_CBGcntrd, left_index=True, right_on='FID', how='right')
        self.proc_pts_gpd_final = pd.merge(proc_pts_gpd, self.proc_pts, left_index=True, right_on='FID', how='right')
        self.DES_CBGcntrd_gpd_final = pd.merge(DES_CBGcntrd_gpd, self.DES_CBGcntrd, left_index=True, right_on='FID', how='right')
        self.MUD_nonpt_gpd_final = pd.merge(MUD_nonpt_gpd, self.MUD_nonpt, left_on='NAME', right_on='County', how='right')
        self.PROC_ZCcntrd_gpd_final = pd.merge(PROC_ZCcntrd_gpd, self.PROC_ZCcntrd, left_on='ZIPCODE', right_on='ZIPCODE', how='right')
        self.COMB_pts_gpd_final = pd.merge(COMB_pts_gpd, self.COMB_pts, left_on='NAME', right_on='NAME', how='right')
        self.AD_pts_gpd_final = pd.merge(AD_pts_gpd, self.AD_pts, left_on='NAME', right_on='NAME', how='right')
        self.W2E_pts_gpd_final = pd.merge(W2E_pts_gpd, self.W2E_pts, left_on='NAME', right_on='City', how='right')

        self.PROC_ZCcntrd_gpd_final = self.PROC_ZCcntrd_gpd_final[~self.PROC_ZCcntrd_gpd_final['geometry'].isnull()]

        self.proc_pts_gpd_final.loc[:,('TYPE')] = 'PROC'
        self.DES_CBGcntrd_gpd_final.loc[:,('TYPE')] = 'DES_CBG'
        self.AD_pts_gpd_final.loc[:,('Type')] = 'AD_pts'
        self.COMB_pts_gpd_final.loc[:,('Type')] = 'COMB_pts'
        self.W2E_pts_gpd_final.loc[:,('Type')] = 'W2E_pts'
        self.DES_CBGcntrd_gpd_final.loc[:,('Type')] = 'DES_CBG_pts'
        self.PROC_ZCcntrd_gpd_final.loc[:,('Type')] = 'PROC_ZC_pts'
        self.manure_pts_gpd_final.loc[:,('Type')] = 'manure'
        self.crp2016_pts_gpd_final.loc[:,('Type')] = 'crop'
        self.crp2020_pts_gpd_final.loc[:,('Type')] = 'crop'
        self.crp2050_pts_gpd_final.loc[:,('Type')] = 'crop'
        self.msw_CBGcntrd_gpd_final.loc[:,('Type')] = 'msw'


    def reproject_shapefiles(self):
        """
        Reproject geometries so all are in the same projection system
        """
        crs = {'init': 'epsg:4326'}
        self.manure_pts_gpd_final = self.manure_pts_gpd_final.to_crs(crs)
        self.msw_CBGcntrd_gpd_final = self.msw_CBGcntrd_gpd_final.to_crs(crs)
        self.proc_pts_gpd_final = self.proc_pts_gpd_final.to_crs(crs)
        self.counties_gpd = self.counties_gpd.to_crs(crs)
        self.DES_CBGcntrd_gpd_final = self.DES_CBGcntrd_gpd_final.to_crs(crs)
        self.COMB_pts_gpd_final = self.COMB_pts_gpd_final.to_crs(crs)
        self.AD_pts_gpd_final = self.AD_pts_gpd_final.to_crs(crs)
        self.W2E_pts_gpd_final = self.W2E_pts_gpd_final.to_crs(crs)
        self.PROC_ZCcntrd_gpd_final = self.PROC_ZCcntrd_gpd_final.to_crs(crs)
        self.crp2016_pts_gpd_final = self.crp2016_pts_gpd_final.to_crs(crs)
        self.crp2020_pts_gpd_final = self.crp2020_pts_gpd_final.to_crs(crs)
        self.crp2050_pts_gpd_final = self.crp2050_pts_gpd_final.to_crs(crs)

    def calculate_county_totals(self):
        """
        Calculates the total biomass in each county to assist with the hovering later
        """
        county_with_totals = getBiomassInCountiesAll(self.counties_gpd, 
                                                self.manure_pts_gpd_final, 
                                                self.msw_CBGcntrd_gpd_final, 
                                                self.crp2016_pts_gpd_final,
                                                self.crp2020_pts_gpd_final,
                                                self.crp2050_pts_gpd_final,
                                                self.manure_nonpts,
                                                self.proc_nonpts)
        return county_with_totals


    def fill_nas(self):
        """
        Fills N/A values with 0 to avoid errors
        """
        self.county_with_totals = self.county_with_totals.fillna(0)
        self.manure_pts_gpd_final = self.manure_pts_gpd_final.fillna(0)
        self.crp2016_pts_gpd_final = self.crp2016_pts_gpd_final.fillna(0)
        self.crp2020_pts_gpd_final = self.crp2020_pts_gpd_final.fillna(0)
        self.crp2050_pts_gpd_final = self.crp2050_pts_gpd_final.fillna(0)
        self.msw_CBGcntrd_gpd_final = self.msw_CBGcntrd_gpd_final.fillna(0)
        self.proc_pts_gpd_final = self.proc_pts_gpd_final.fillna(0)

        self.DES_CBGcntrd_gpd_final = self.DES_CBGcntrd_gpd_final.fillna(0)
        self.MUD_nonpt_gpd_final = self.MUD_nonpt_gpd_final.fillna(0)
        self.PROC_ZCcntrd_gpd_final = self.PROC_ZCcntrd_gpd_final.fillna(0)
        self.COMB_pts_gpd_final = self.COMB_pts_gpd_final.fillna(0)
        self.AD_pts_gpd_final = self.AD_pts_gpd_final.fillna(0)
        self.W2E_pts_gpd_final = self.W2E_pts_gpd_final.fillna(0)
        self.manure_nonpts = self.manure_nonpts.fillna(0)
        self.proc_nonpts = self.proc_nonpts.fillna(0)


    def save_to_csvs(self):
        """
        Saves final data
        """
        self.county_with_totals.to_csv('GIS_data/final_data/counties.csv')
        self.manure_pts_gpd_final.to_csv('GIS_data/final_data/manure_pts.csv')
        self.crp2016_pts_gpd_final.to_csv('GIS_data/final_data/crp2016_pts.csv')
        self.crp2020_pts_gpd_final.to_csv('GIS_data/final_data/crp2020_pts.csv')
        self.crp2050_pts_gpd_final.to_csv('GIS_data/final_data/crp2050_pts.csv')
        self.msw_CBGcntrd_gpd_final.to_csv('GIS_data/final_data/msw_CBGcntrd.csv')
        self.proc_pts_gpd_final.to_csv('GIS_data/final_data/proc_pts.csv')
        self.DES_CBGcntrd_gpd_final.to_csv('GIS_data/final_data/DES_CBGcntrd.csv')
        self.MUD_nonpt_gpd_final.to_csv('GIS_data/final_data/MUD_nonpt.csv')
        self.PROC_ZCcntrd_gpd_final.to_csv('GIS_data/final_data/PROC_ZCcntrd.csv')
        self.COMB_pts_gpd_final.to_csv('GIS_data/final_data/COMB_pts.csv')
        self.AD_pts_gpd_final.to_csv('GIS_data/final_data/AD_pts.csv')
        self.W2E_pts_gpd_final.to_csv('GIS_data/final_data/W2E_pts.csv')
        self.manure_nonpts.to_csv('GIS_data/final_data/manure_nonpts.csv')
        self.proc_nonpts.to_csv('GIS_data/final_data/proc_nonpts.csv')

        self.cbg_thermalrun_gpd_all_dissolved_county.to_csv('GIS_data/final_data/cbg_thermalrun_gpd_dissolve.csv')


if __name__ == '__main__':
    dataProcess('GIS_data/data_biositingtool_withwetweight_versiontags.xlsx')
    print("*** Data Update Successful ***")






