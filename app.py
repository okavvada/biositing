import flask
import pandas as pd
from flask import Flask, request
from functions import (loadDatasets, getBiomassInBuffer, gpd_to_geojson, getBiomassInCountiesAll, getBiomassInSelectCounty,
                        loadShapefiles, getPointsWithScale, getPointsInFrame, getCountyHover, getCensusHover)

app = Flask(__name__)

# Set data paths
path_counties = 'GIS_data/final_data/counties.csv'
path_manure = 'GIS_data/final_data/AD_pts.csv'
path_manure_nonpts = 'GIS_data/final_data/manure_nonpts.csv'
path_AD_pts = 'GIS_data/final_data/AD_pts.csv'
path_COMB_pts = 'GIS_data/final_data/COMB_pts.csv'
path_W2E_pts = 'GIS_data/final_data/W2E_pts.csv'
path_DES_CBG_pts = 'GIS_data/final_data/DES_CBGcntrd.csv'
path_PROC_ZC_pts = 'GIS_data/final_data/PROC_ZCcntrd.csv'
path_msw_CBGcntrd_pts = 'GIS_data/final_data/DES_CBGcntrd.csv'
path_crp2016_pts = 'GIS_data/final_data/DES_CBGcntrd.csv'
path_crp2020_pts = 'GIS_data/final_data/DES_CBGcntrd.csv'
path_crp2050_pts = 'GIS_data/final_data/DES_CBGcntrd.csv'
#path_proc_pts = 'GIS_data/final_data/proc_pts.csv'
path_proc_nonpts = 'GIS_data/final_data/proc_nonpts.csv'
path_thermal = 'GIS_data/final_data/DES_CBGcntrd.csv'

# Load all data as geodataframes
counties_df = loadDatasets(path_counties)
biomass_pts = loadDatasets(path_manure)
AD_pts = loadDatasets(path_AD_pts)
COMB_pts = loadDatasets(path_COMB_pts)
W2E_pts = loadDatasets(path_W2E_pts)
DES_CBG_pts = loadDatasets(path_DES_CBG_pts)
PROC_ZC_pts = loadDatasets(path_PROC_ZC_pts)
msw_CBGcntrd_pts = loadDatasets(path_msw_CBGcntrd_pts)
crp2016_pts = loadDatasets(path_crp2016_pts)
crp2020_pts = loadDatasets(path_crp2020_pts)
crp2050_pts = loadDatasets(path_crp2050_pts)
manure_nonpts = pd.read_csv(path_manure_nonpts)
proc_nonpts = pd.read_csv(path_proc_nonpts)
thermal = loadDatasets(path_thermal)

# Set the preferred resulted columns for each dataset
cols_counties = counties_df.columns.drop('geometry',1)
cols_biomass = biomass_pts.columns.drop('geometry',1)
cols_msw = msw_CBGcntrd_pts.columns.drop('geometry',1)
cols_crop = crp2016_pts.columns.drop('geometry',1)
cols_manure_nonpts = manure_nonpts.columns
cols_AD_pts = AD_pts.columns.drop('geometry',1)
cols_COMB_pts = COMB_pts.columns.drop('geometry',1)
cols_W2E_pts = W2E_pts.columns.drop('geometry',1)
cols_DES_CBG_pts = DES_CBG_pts.columns.drop('geometry',1)
cols_PROC_ZC_pts = PROC_ZC_pts.columns.drop('geometry',1)
cols_thermal = thermal.columns.drop('geometry',1)


# Set the html file
@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route('/check_password')
def checkPassword():
  password = request.args.get('password')
  if password == 'lblonly':
    return flask.jsonify({'validity': 'True'})
  else:
    return flask.jsonify({'validity': 'False'})

# Set the basemap with county biomass totals to geojson for visualization
@app.route("/basemap")
def getCounties():
  return flask.jsonify({'biomass': gpd_to_geojson(counties_df, cols_counties),
                        'thermal': gpd_to_geojson(thermal, cols_thermal)})

# Convert biomass points to geojson for visualization
@app.route("/points")
def getPoints():
  return flask.jsonify({'AD': gpd_to_geojson(AD_pts, cols_AD_pts),
                        'COMB': gpd_to_geojson(COMB_pts, cols_COMB_pts),
                        'W2E': gpd_to_geojson(W2E_pts, cols_W2E_pts),
                        })

@app.route("/county_data")
def getCounty():
  county_nm = request.args.get('county_nm')
  year = request.args.get('year')
  return flask.jsonify(getPointsCountyGeoJSON(county_name=county_nm, year=year))

def getPointsCountyGeoJSON(county_name, year):
  (manure, msw, crop, manure_nonpoints, proc_nonpoints, 
    manure_cols, cols_msw, cols_crp, cols_manure_nonpts, cols_proc_nonpts) = getBiomassInSelectCounty(county_name, 
                                                                                                      counties_df,
                                                                                                      biomass_pts, 
                                                                                                      msw_CBGcntrd_pts, 
                                                                                                      crp2016_pts,
                                                                                                      crp2020_pts,
                                                                                                      crp2050_pts,
                                                                                                      manure_nonpts,
                                                                                                      proc_nonpts,
                                                                                                      year)

  return {'manure_pts': gpd_to_geojson(manure, manure_cols),
          'msw_pts': gpd_to_geojson(msw, cols_msw),
          'crp_pts': gpd_to_geojson(crop, cols_crp),
          'manure_nonpts': gpd_to_geojson(manure_nonpoints, cols_manure_nonpts),
          'proc_nonpts': gpd_to_geojson(proc_nonpoints, cols_proc_nonpts)
          }

# The thermal processors are too many to visualize so we only visualize cluster centers by 
# selecting the ones that are currently in the frame
@app.route("/PROC")
def getPROCwithScale():
  left_bottom_lon = float(request.args.get('left_bottom_lon'))
  left_bottom_lat = float(request.args.get('left_bottom_lat'))
  right_top_lon = float(request.args.get('right_top_lon'))
  right_top_lat = float(request.args.get('right_top_lat'))
  pointlist = [[left_bottom_lon, left_bottom_lat],
              [left_bottom_lon, right_top_lat],
              [right_top_lon, right_top_lat],
              [right_top_lon, left_bottom_lat]]
  points_in_frame = getPointsInFrame(pointlist, PROC_ZC_pts)
  cluster_centers = getPointsWithScale(points_in_frame)
  cluster_centers['Type'] = 'PROC'
  return flask.jsonify({'PROC': gpd_to_geojson(cluster_centers, ['number_of_points', 'Type', 'AVG_PH', 'AVG_PC']),
                         'DES_CBG': gpd_to_geojson(DES_CBG_pts, cols_DES_CBG_pts)})

# When a user clicks, the click location is stored and a buffer is calculated from the click location.
# It returns the biomass points that fall within the buffer
@app.route("/lat_lng")
def lat_lng():
  lat = float(request.args.get('lat'))
  lng = float(request.args.get('lng'))
  buffer_m = float(request.args.get('buffer'))
  year = request.args.get('year')
  moisture = request.args.get('moisture')
  energy_type = request.args.get('energy_type')
  content = request.args.get('content')
  potential = request.args.get('potential')
  return flask.jsonify(getPointsBufferGeoJSON(lat=lat, lng=lng, buffer_m=buffer_m, year=year, moisture=moisture, energy_type=energy_type, content=content, potential=potential))

# Estimates the biomass in buffer and returns that
def getPointsBufferGeoJSON(lat,lng, buffer_m, year, moisture, energy_type, content, potential):
  biomass, msw, crp, total_biomass, total_biomass_wt = getBiomassInBuffer((lng,lat), 
                                                                          buffer_m, 
                                                                          biomass_pts, 
                                                                          msw_CBGcntrd_pts,
                                                                          crp2016_pts,
                                                                          crp2020_pts,
                                                                          crp2050_pts,
                                                                          year,
                                                                          moisture,
                                                                          energy_type, 
                                                                          content,
                                                                          potential)
  cols_msw = list(msw.columns.values)
  cols_msw.remove('geometry')
  cols_crop = list(crp.columns.values)
  cols_crop.remove('geometry')
  cols_manure = list(biomass.columns.values)
  cols_manure.remove('geometry')

  return {'manure': gpd_to_geojson(biomass, cols_manure),
          'msw': gpd_to_geojson(msw, cols_msw),
          'crop': gpd_to_geojson(crp, cols_crop),
          'total_biomass': total_biomass,
          'total_biomass_wt': total_biomass_wt}

# Gets the total biomass of the county by selecting the column with totals from the CID of the county
# that the users mouse is hovering over
@app.route("/total_county")
def get_cid():
  cid = request.args.get('cid')
  fid = request.args.get('fid')
  year = request.args.get('year')
  moisture = request.args.get('moisture')
  energy_type = request.args.get('energy_type')
  content = request.args.get('content')
  vizSelection = request.args.get('vizSelection')
  lng = float(request.args.get('lng'))
  lat = float(request.args.get('lat'))
  coords = (lng, lat)
  return flask.jsonify(getTotalsCountyGeoJSON(cid=cid, fid=fid, coords=coords, year=year, moisture=moisture, energy_type=energy_type, content=content, vizSelection=vizSelection))

def getTotalsCountyGeoJSON(fid, cid, coords, year, moisture, energy_type, content, vizSelection):
  if vizSelection == 'biomass':
    biomass_dict = getCountyHover(cid, counties_df, year, moisture, energy_type, content)
  if (vizSelection == 'thermal_h') or (vizSelection == 'thermal_c'):
    biomass_dict = getCensusHover(fid, cid, coords, counties_df, thermal, year, vizSelection)
  return biomass_dict

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')