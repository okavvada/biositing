import geopandas as gpd 
import pandas as pd
import json
from shapely.geometry import Point, Polygon
import shapely.wkt
from sklearn.cluster import KMeans
import numpy as np

columns_manure = ['Mclf', 'Mdy', 'Mbf', 'Mhg', 'Mly']
columns_msw_16 = ['MSWlb', 'MSWpp', 'MSWcd', 'MSWfog', 'MSWot', 'MSWfd']
columns_msw_20 = ['MSWlb', 'MSWpp', 'MSWcd', 'MSWfog', 'MSWot', 'MSWfd', 'MSWgn']
columns_msw_50 = ['MSWlb', 'MSWpp', 'MSWcd', 'MSWgn', 'MSWfd', 'MSWfog', 'MSWot', 'MSWgn'] 
columns_crop = ['RES', 'CULL']
columns_manure_nonpts = ['Mlr', 'Mpl', 'Mbr', 'Mtk', 'Mhg', 'Mgt', 'Msh', 'Meq', 'Mdk', 'Blr', 'Bpl', 'Bbr']
columns_proc = ['Pcn', 'Pdeh', 'Pff', 'Pwn', 'Pbry', 'Pdst', 'Prm', 'Ppm', 'Pah', 'Pas', 'Pws', 'Potns', 'Prh', 'Pcgt', 'Pcn', 'Pdeh', 'Pbky', 'Ptll', 'Pgrc', 'PPt']


def gpd_to_geojson(df, properties):
    """
    Converts geodataframe to geojson for visualization
    """
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        if 'geometry' not in df.columns:
            geom = {"geometry": {
          "coordinates": [],
          "type": "Point"
        }
            }
        else:
            geom = row.geometry.__geo_interface__
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':geom,}
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    geojson = json.loads(json.dumps(geojson))
    return geojson

def loadShapefiles(path):
    """
    If initial dataset is in shapefile format, use this to load. It projects the data
    to crs 4326.
    """
    dataset = gpd.read_file(path)
    dataset = dataset.to_crs({'init': 'epsg:4326'})
    return dataset

def loadDatasets(path):
    """
    If initial dataset is in csv format, use this to load. It projects the data
    to crs 4326.
    """
    dataset = pd.read_csv(path)
    geometry = dataset['geometry'].map(shapely.wkt.loads)
    dataset = dataset.drop('geometry', axis=1)
    crs = {'init': 'epsg:4326'}
    dataset_gdf = gpd.GeoDataFrame(dataset, crs=crs, geometry=geometry)
    dataset_gdf = dataset_gdf.fillna(0)
    return dataset_gdf

def convertToMetric(dataframe):
    """
    Converts the dataframe to a metric projection so the buffer calculation can be done.
    The projection is crs 3395.
    """
    dataset_m = dataframe.to_crs({'init': 'epsg:3395'})
    return dataset_m

def getPointGeoDataFrame(coords):
    """
    Generates a geodataframe out of a (lat,lng) and projects it to crs 4326.
    """
    geometry = [Point(xy) for xy in coords]
    df = pd.DataFrame()
    crs = {'init': 'epsg:4326'}
    click_on_map = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)
    return click_on_map

def getPolygonGeoDataFrame(pointList):
    """
    Generates a polygon geodataframe out of points. This is used to set the frame from the 
    locations of the 4 corners of the screen.
    """
    geometry = [Polygon(pointList)]
    df = pd.DataFrame()
    crs = {'init': 'epsg:4326'}
    frame_bounds = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)
    return frame_bounds

def getBiomassInBuffer(click_coords, 
                        buffer_m, 
                        manure_pts, 
                        msw_CBGcntrd_pts, 
                        crp2016_pts,
                        crp2020_pts,
                        crp2050_pts,
                        year,
                        moisture,
                        energy_type, 
                        content,
                        potential):
    """
    Takes as inputs the click coordinates, buffer distance and all the biomass geodatframes. It calculates for each biomass
    which ones fall inside the buffer and calculates the total biomass from the biomass columns. It returns all the biomass 
    geodataframes only containing the points that fall inside the buffer, with biomass totals. It also returns the 
    total biomass amount by combining all the biomass geodataframes.
    """  

    if year == '16':
        crp_year_pts = crp2016_pts
    if year == '20':
        crp_year_pts = crp2020_pts
    if year == '50':
        crp_year_pts = crp2050_pts

    dataset_manure_m = convertToMetric(manure_pts)
    dataset_msw_m = convertToMetric(msw_CBGcntrd_pts)
    dataset_crp_m = convertToMetric(crp_year_pts)
    click_on_map = getPointGeoDataFrame([click_coords])
    click_on_map_m = convertToMetric(click_on_map)
    buffer_pol = click_on_map_m.buffer(buffer_m*1000)

    point_in_buffer = dataset_manure_m[dataset_manure_m.intersects(buffer_pol.unary_union)]
    msw_in_buffer = dataset_msw_m[dataset_msw_m.intersects(buffer_pol.unary_union)]
    crp_in_buffer = dataset_crp_m[dataset_crp_m.intersects(buffer_pol.unary_union)]

    point_in_buffer_map = point_in_buffer.to_crs({'init': 'epsg:4326'})
    msw_in_buffer_map = msw_in_buffer.to_crs({'init': 'epsg:4326'})
    crp_in_buffer_map = crp_in_buffer.to_crs({'init': 'epsg:4326'})

    select_columns = [item for item in manure_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and potential in item and '_wt' not in item]
    select_columns_msw = [item for item in msw_CBGcntrd_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and potential in item and '_wt' not in item]
    select_columns_crp = [item for item in crp_year_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and potential in item and '_wt' not in item]
    select_columns_wt = [item for item in manure_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and '_wt' in item and potential in item]
    select_columns_msw_wt = [item for item in msw_CBGcntrd_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and '_wt' in item and potential in item]
    select_columns_crp_wt = [item for item in crp_year_pts.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and '_'+year in item and '_wt' in item and potential in item]

    column_name = 'tot_' + year
    column_name_wt = 'tot_' + year + '_wt'
    point_in_buffer_map[column_name] = int(point_in_buffer_map[select_columns].sum().sum())
    msw_in_buffer_map[column_name] = int(msw_in_buffer_map[select_columns_msw].sum().sum())
    crp_in_buffer_map[column_name] = int(crp_in_buffer_map[select_columns_crp].sum().sum())
    point_in_buffer_map[column_name_wt] = int(point_in_buffer_map[select_columns_wt].sum().sum())
    msw_in_buffer_map[column_name_wt] = int(msw_in_buffer_map[select_columns_msw_wt].sum().sum())
    crp_in_buffer_map[column_name_wt] = int(crp_in_buffer_map[select_columns_crp_wt].sum().sum())

    total_biomass = (int(point_in_buffer_map[select_columns].sum().sum() +
                        msw_in_buffer_map[select_columns_msw].sum().sum() +
                        crp_in_buffer_map[select_columns_crp].sum().sum()))
    total_biomass_wt = (int(point_in_buffer_map[select_columns_wt].sum().sum() +
                        msw_in_buffer_map[select_columns_msw_wt].sum().sum() +
                        crp_in_buffer_map[select_columns_crp_wt].sum().sum()))

    return point_in_buffer_map, msw_in_buffer_map, crp_in_buffer_map, total_biomass, total_biomass_wt

def getBiomassInSelectCounty(
                            county_name,
                            county_df,
                            manure_pts, 
                            msw_CBGcntrd_pts, 
                            crp2016_pts,
                            crp2020_pts,
                            crp2050_pts,
                            manure_nonpts,
                            proc_non_points,
                            year):
    """
    Selects all data in a county for year.
    """ 

    select_county = county_df[county_df['NAME'] == county_name]

    if year == '16':
        crp_pts = crp2016_pts
    if year == '20':
        crp_pts = crp2020_pts
    if year == '50':
        crp_pts = crp2050_pts
    manure_county = manure_pts[manure_pts.intersects(select_county.unary_union)]
    msw_county = msw_CBGcntrd_pts[msw_CBGcntrd_pts.intersects(select_county.unary_union)]
    crp_county = crp_pts[crp_pts.intersects(select_county.unary_union)]
    manure_nonpts_county = manure_nonpts[manure_nonpts['County'] == county_name]
    proc_nonpts_county = proc_non_points[proc_non_points['COUNTY'] == county_name]

    manure_cols = [item for item in manure_county.columns if '_'+year in item]
    cols_msw = [item for item in msw_county.columns if '_'+year in item]
    cols_crp = [item for item in crp_county.columns if '_'+year in item]
    cols_manure_nonpts = [item for item in manure_nonpts_county.columns if '_'+year in item]
    cols_proc_nonpts = [item for item in proc_nonpts_county.columns if '_'+year in item]

    return manure_county, msw_county, crp_county, manure_nonpts_county, proc_nonpts_county, manure_cols, cols_msw, cols_crp, cols_manure_nonpts, cols_proc_nonpts


def getBiomassInCountiesAll(county_df, 
                            manure_pts, 
                            msw_CBGcntrd_pts, 
                            crp2016_pts,
                            crp2020_pts,
                            crp2050_pts,
                            manure_nonpts,
                            proc_non_points):
    """
    Similar as getBiomasInBuffer, this function calculates the total biomass that fall in a county.
    It takes as inputs the county dataframe and all the biomass geodatframes (points and non points). It calculates for each biomass
    which ones fall inside each county and calculates the total biomass from the biomass columns. It returns the county
    geodataframe containing columns with the total biomass of each type per year and the overall total biomass amount per year.
    """
    county_df['CID'] = county_df.index
    manure_county = gpd.sjoin(manure_pts, county_df, how="left", op='intersects')
    msw_county = gpd.sjoin(msw_CBGcntrd_pts, county_df, how="left", op='intersects')
    crp2016_county = gpd.sjoin(crp2016_pts, county_df, how="left", op='intersects')
    crp2020_county = gpd.sjoin(crp2020_pts, county_df, how="left", op='intersects')
    crp2050_county = gpd.sjoin(crp2050_pts, county_df, how="left", op='intersects')
    manure_nonpts_county = pd.merge(manure_nonpts, county_df, how="left", on='County')
    proc_non_points_county = pd.merge(proc_non_points, county_df, how="left", left_on='COUNTY', right_on='County')

    for moisture in ['', '_wet', '_dry']:
        for energy_type in ['', '_wetad', '_dryad']:
            for content in ['', '_lg', '_hr']:
                for year in ['16', '20', '50']:
                    if year == '16':
                        crop_county = crp2016_county
                    if year == '20':
                        crop_county = crp2020_county
                    if year == '50':
                        crop_county = crp2050_county
                    for potential in ['_gross', '_tech']:
                        select_columns_manure = [item for item in manure_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' not in item]
                        select_columns_manure_wt = [item for item in manure_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' in item]
                        select_columns_msw = [item for item in msw_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' not in item]
                        select_columns_msw_wt = [item for item in msw_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' in item]
                        select_columns_crop = [item for item in crop_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' not in item]
                        select_columns_crop_wt = [item for item in crop_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' in item]
                        select_columns_manure_nonpts = [item for item in manure_nonpts_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' not in item]
                        select_columns_manure_nonpts_wt = [item for item in manure_nonpts_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' in item]
                        select_columns_proc_non_points = [item for item in proc_non_points_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' not in item]
                        select_columns_proc_non_points_wt = [item for item in proc_non_points_county.columns if moisture+'_' in item and energy_type+'_' in item and content+'_' in item and year in item and potential in item and '_wt' in item]
                        select_columns_manure.append('CID')
                        select_columns_manure_wt.append('CID')
                        select_columns_msw.append('CID')
                        select_columns_msw_wt.append('CID')
                        select_columns_crop.append('CID')
                        select_columns_crop_wt.append('CID')
                        select_columns_manure_nonpts.append('CID')
                        select_columns_manure_nonpts_wt.append('CID')
                        select_columns_proc_non_points.append('CID')
                        select_columns_proc_non_points_wt.append('CID')

                        totals_manure = pd.DataFrame(manure_county[select_columns_manure].groupby('CID').sum().sum(axis=1), columns=['manure_biomass' + moisture + energy_type + content + '_' + year + potential])
                        totals_manure_wt = pd.DataFrame(manure_county[select_columns_manure_wt].groupby('CID').sum().sum(axis=1), columns=['manure_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'])
                        totals_msw = pd.DataFrame(msw_county[select_columns_msw].groupby('CID').sum().sum(axis=1), columns=['msw_biomass' + moisture + energy_type + content + '_' + year + potential])
                        totals_msw_wt = pd.DataFrame(msw_county[select_columns_msw_wt].groupby('CID').sum().sum(axis=1), columns=['msw_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'])
                        totals_crop = pd.DataFrame(crop_county[select_columns_crop].groupby('CID').sum().sum(axis=1), columns=['crop_biomass' + moisture + energy_type + content + '_' + year + potential])
                        totals_crop_wt = pd.DataFrame(crop_county[select_columns_crop_wt].groupby('CID').sum().sum(axis=1), columns=['crop_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'])
                        totals_manure_nonpts = pd.DataFrame(manure_nonpts_county[select_columns_manure_nonpts].groupby('CID').sum().sum(axis=1), columns=['manure_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential])
                        totals_manure_nonpts_wt = pd.DataFrame(manure_nonpts_county[select_columns_manure_nonpts_wt].groupby('CID').sum().sum(axis=1), columns=['manure_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'])
                        totals_proc_non_points = pd.DataFrame(proc_non_points_county[select_columns_proc_non_points].groupby('CID').sum().sum(axis=1), columns=['proc_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential])
                        totals_proc_non_points_wt = pd.DataFrame(proc_non_points_county[select_columns_proc_non_points_wt].groupby('CID').sum().sum(axis=1), columns=['proc_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'])
                        
                        county_df = county_df.join(totals_manure, on='CID', how='left')
                        county_df = county_df.join(totals_manure_wt, on='CID', how='left')
                        county_df = county_df.join(totals_msw, on='CID', how='left')
                        county_df = county_df.join(totals_msw_wt, on='CID', how='left')
                        county_df = pd.merge(county_df, totals_crop, left_on='CID', right_index=True, how='left')
                        county_df = pd.merge(county_df, totals_crop_wt, left_on='CID', right_index=True, how='left')
                        county_df = pd.merge(county_df, totals_proc_non_points, left_on='CID', right_index=True, how='left')
                        county_df = pd.merge(county_df, totals_proc_non_points_wt, left_on='CID', right_index=True, how='left')
                        county_df = pd.merge(county_df, totals_manure_nonpts, left_on='CID', right_index=True, how='left')
                        county_df = pd.merge(county_df, totals_manure_nonpts_wt, left_on='CID', right_index=True, how='left')

                        county_totals = county_df.fillna(0)

    county_return = county_totals[['CID', 'geometry', 'NAME']]
    for moisture in ['', '_wet', '_dry']:
        for energy_type in ['', '_wetad', '_dryad']:
            for content in ['', '_lg', '_hr']:
                for year in ['16', '20', '50']:
                    for potential in ['_tech', '_gross']:
                        county_return['county_total' + moisture + energy_type + content + '_' + year + potential] = (county_totals['manure_biomass' + moisture + energy_type + content + '_' + year + potential] + 
                                                                                                                    county_totals['msw_biomass' + moisture + energy_type + content + '_' + year + potential] + 
                                                                                                                    county_totals['crop_biomass' + moisture + energy_type + content + '_' + year + potential] +
                                                                                                                    county_totals['manure_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential] +
                                                                                                                    county_totals['proc_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential])

                        county_return['county_total' + moisture + energy_type + content + '_' + year + '_wt' + potential] = (county_totals['manure_biomass' + moisture + energy_type + content + '_' + year +  potential + '_wt'] + 
                                                                                                                            county_totals['msw_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'] + 
                                                                                                                            county_totals['crop_biomass' + moisture + energy_type + content + '_' + year +  potential + '_wt'] +
                                                                                                                            county_totals['manure_nonpts_biomass' + moisture + energy_type + content + '_' + year + potential + '_wt'] +
                                                                                                                            county_totals['proc_nonpts_biomass' + moisture + energy_type + content + '_' + year  + potential + '_wt'])

    return county_return



def getCountyHover(cid, county_df, year, moisture, energy_type, content): 
    """
    Takes as inputs the cid of the county the user is hovering over, the county geodataframe that has already calculated 
    the biomass totals using the getBiomassInCounty from above and the selected year and it 
    returns a dictionary of the total biomass available in that county that was calculated before.
    """
    total_of_county = county_df[county_df['CID'] == int(cid)]
    if energy_type == '_dry':
        moisture = ''
    if total_of_county.empty:
        total_per_county = {"name": '',
                            "county_total_gross": 0,
                            "county_total_wt_gross": 0,
                            "county_total_tech": 0,
                            "county_total_wt_tech": 0,
                            "thermal_total": 'NaN'
                            }
    else:
        total_per_county = {"name": total_of_county['NAME'].iloc[0],
                            "county_total_gross": total_of_county['county_total' + moisture + energy_type + content + '_' + year + '_gross'].iloc[0],
                            "county_total_wt_gross": total_of_county['county_total' + moisture + energy_type + content + '_' + year + '_wt'+ '_gross'].iloc[0],
                            "county_total_tech": total_of_county['county_total' + moisture + energy_type + content + '_' + year + '_tech'].iloc[0],
                            "county_total_wt_tech": total_of_county['county_total' + moisture + energy_type + content + '_' + year+ '_wt' + '_tech'].iloc[0],
                            "thermal_total": 'NaN'
                            }
    return total_per_county


def getCensusHover(fid, cid, coords, county_df, cbg_thermal, year, energy_type): 
    """
    Takes as inputs the fid of the census block the user is hovering over,  and it 
    returns a dictionary of the total thermal consumption in that census.
    """
    census = cbg_thermal[cbg_thermal['FID'] == int(fid)]
    total_of_county = county_df[county_df['CID'] == int(cid)]
    if energy_type == 'thermal_h':
        column_energy = 'SUM_TotH'
    if energy_type == 'thermal_c':
        column_energy = 'SUM_TotC'
    if census.empty:
        total_of_census = {"name": '',
                            "county_total_gross": 'NaN',
                            "county_total_wt_gross": 'NaN',
                            "county_total_tech": 'NaN',
                            "county_total_wt_tech": 'NaN',
                            "thermal_total": 'NaN'}
    else:
        total_of_census = {"name": '',
                            "county_total_gross": 'NaN',
                            "county_total_wt_gross": 'NaN',
                            "county_total_tech": 'NaN',
                            "county_total_wt_tech": 'NaN',
                            "thermal_total": census[column_energy + year].iloc[0]
                            }
    return total_of_census


def getPointsInFrame(pointList, all_points):
    """
    From a pointlist of the coordinates of the 4 corners of the viewport and a selection of points in a geodataframe,
    it identifies the subset of points that fall inside the viewport. Returns a geodatframe of the points that
    fall iside the viewport.
    """
    frame_bounds = getPolygonGeoDataFrame(pointList)
    points_in_bounds = all_points[all_points.intersects(frame_bounds.unary_union)]
    return points_in_bounds

def getPointsWithScale(points_in_frame):
    """
    From a geodataframe of points it performs a clustering analysis (kmeans) and returns the 100 cluster centroids
    and how many points each cluster was generated from. It returns a geodataframe of cluster centers with a column
    for the number of points each cluster includes.
    """
    n_clusters = 100
    if len(points_in_frame) < 100:
        points_in_frame['number_of_points'] = [1]*len(points_in_frame)
        return points_in_frame
        
    coords = []
    for geom in points_in_frame['geometry']:
         coords.append([geom.x, geom.y]) 
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coords)
    clusters = getPointGeoDataFrame(kmeans.cluster_centers_)
    clusters['number_of_points'] = [0]*len(clusters)
    for i in range(n_clusters):
        clusters.at[i, 'number_of_points'] = list(kmeans.labels_).count(i)
        if list(kmeans.labels_).count(i) == 1:
            clusters.at[i, 'ZIPCODE'] = points_in_frame[kmeans.labels_ == i]['ZIPCODE'].iloc[0]
        else:
            clusters.at[i, 'ZIPCODE'] = 'NaN'
        clusters.at[i, 'AVG_PH'] = int(points_in_frame[kmeans.labels_ == i]['AVG_PH'].sum())
        clusters.at[i, 'AVG_PC'] = int(points_in_frame[kmeans.labels_ == i]['AVG_PC'].sum())
    return clusters

