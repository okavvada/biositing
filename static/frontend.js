var map;

// Setting the initial analysis parameters to year 2016 and processing type.
var analysis_params = {
    'energy': '',
    'year': '16',
    'vizSelection': 'biomass',
    'potential': '_gross',
    'moisture': '',
    'content': ''
    }

//Storing the markers
var positioner = [];

// Main function that runs with the html page
function initMap() {
  // Initialize the map to center to CA
	map = new google.maps.Map(document.getElementById('map'), {
		center: {
			lat: 37.8553618,
			lng: -119.9742504},
  	zoom: 7,
	});


// Create empty layers for the basemap polygons (polylayer), the basemap points (pointLayer),
// The selected biomass (newpointLayer), and the processors (PROCLayer) which is separate as they change with zooming.
polyLayer = new google.maps.Data({map:map});
polyLayer_thermal = new google.maps.Data({map:map});
pointLayer = new google.maps.Data({map:map});
newpointLayer = new google.maps.Data({map:map});
PROCLayer = new google.maps.Data({map:map});
countyLayer = new google.maps.Data({map:map});


// Style the layers
setBaseMapPointsStyle(pointLayer, map.zoom);
setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
setBaseMapPROCStyle(PROCLayer, map.zoom)

$('#img').show(); 

// Draw basemap point layers from the data
$.getJSON("/points", function(data) {
  pointLayer.addGeoJson(data['AD']);
  pointLayer.addGeoJson(data['W2E']);
  pointLayer.addGeoJson(data['COMB']);
  });

var ADcheckbox = document.getElementById('ADcheckBox');
ADcheckbox.addEventListener("change", function(){
  setBaseMapPointsStyle(pointLayer, map.zoom);
});
var W2Echeckbox = document.getElementById('W2EcheckBox');
W2Echeckbox.addEventListener("change", function(){
  setBaseMapPointsStyle(pointLayer, map.zoom);
});
var CPcheckbox = document.getElementById('CPcheckBox');
CPcheckbox.addEventListener("change", function(){
  setBaseMapPointsStyle(pointLayer, map.zoom);
});
var DEScheckbox = document.getElementById('DEScheckBox');
DEScheckbox.addEventListener("change", function(){
  setBaseMapPROCStyle(PROCLayer, map.zoom)
});

// Add the polygon layer to map and color code based on year
$.getJSON("/basemap", {
}, function(data) {
  	polyLayer.addGeoJson(data['biomass']);
    polyLayer_thermal.addGeoJson(data['thermal']);
    $('#img').hide();
	});

// Listen for user changes in year, energy or visualization and redraw if there are user changes 
var analysis_year = document.getElementById('myYears');
analysis_year.addEventListener("change", function(){
  yearSelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  setNewPointLayerStyle(newpointLayer, analysis_params);
});

var potential = document.getElementById('myPotential');
potential.addEventListener("change", function(){
  potentialSelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  setNewPointLayerStyle(newpointLayer, analysis_params);
});

var moisture = document.getElementById('myMoisture');
moisture.addEventListener("change", function(){
  moistureSelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  setNewPointLayerStyle(newpointLayer, analysis_params);
});

var content = document.getElementById('myContent');
content.addEventListener("change", function(){
  contentSelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  setNewPointLayerStyle(newpointLayer, analysis_params);
});

var analysis_energy = document.getElementById('myEnergy');
analysis_energy.addEventListener("change", function(){
  energySelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  setNewPointLayerStyle(newpointLayer, analysis_params);
});

var analysis_vis = document.getElementById('myViz');
analysis_vis.addEventListener("change", function(){
  vizSelect(analysis_params)
  setBaseMapPolygonsBiomassStyle(polyLayer, analysis_params);
  setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params);
  PROCLayer = setPROCLayer(map, PROCLayer, analysis_params);
  legend = populateLegend(legend, analysis_params.vizSelection);
});

// Listen for viewports bounds changes and redraw the processors layer
google.maps.event.addListener(map, 'bounds_changed', function(event) {
  PROCLayer = setPROCLayer(map, PROCLayer, analysis_params);
  setBaseMapPointsStyle(pointLayer, map.zoom);
});

// Set up the filter accordion menu
var acc = document.getElementsByClassName("accordion");
  for (var i = 0; i < acc.length; i++) {
acc[i].addEventListener("click", function() {
  this.classList.toggle("active");
  /* Toggle between hiding and showing the active panel */
  var panel = this.nextElementSibling;
  if (panel.style.display === "block") {
      panel.style.display = "none";
  } else {
      panel.style.display = "block";
  }
});
}

// Listen for county changes
var county_selected = 'Alameda';
var county_select = document.getElementById('myCounty');
county_select.addEventListener("change", function(){
  county_selected = countySelect()
});

// Download all the data in each county
var download_county_select = document.getElementById('download-all');
download_county_select.addEventListener("click", function(){
  $.getJSON("/county_data", {
    county_nm: county_selected,
    year: analysis_params.year,
  }, function(data) {
    msw_county_all = []
    crop_county_all = []
    manure_county_all = []
    proc_county_all = []
    manure_non_county_all = []
    msw_county_titles = []
    crop_county_titles = []
    manure_county_titles = []
    proc_county_titles = []
    manure_non_county_titles = []
    data['msw_pts']['features'].forEach(function(feature){
      msw_feature = []
      if (msw_county_all.length == 0){
          for (prop in feature['properties']){
            msw_county_titles.push(prop)
            }
          msw_county_all.push(msw_county_titles)
        }
      for (prop in feature['properties']){
          msw_feature.push(feature['properties'][prop])
        }
    msw_county_all.push(msw_feature)
  })
  data['crp_pts']['features'].forEach(function(feature){
    crp_feature = []
      if (crop_county_all.length == 0){
          for (prop in feature['properties']){
          crop_county_titles.push(prop)
          }
          crop_county_all.push(crop_county_titles)
        }
      for (prop in feature['properties']){
          crp_feature.push(feature['properties'][prop])
      }
      crop_county_all.push(crp_feature)
  })
  data['manure_pts']['features'].forEach(function(feature){
    manure_feature = []
      if (manure_county_all.length == 0){
        for (prop in feature['properties']){
        manure_county_titles.push(prop)
        }
        manure_county_all.push(manure_county_titles)
        }
        for (prop in feature['properties']){
            manure_feature.push(feature['properties'][prop])
        }
        manure_county_all.push(manure_feature)
  })
  data['manure_nonpts']['features'].forEach(function(feature){
    manure_non_feature = []
      if (manure_non_county_all.length == 0){
          for (prop in feature['properties']){
          manure_non_county_titles.push(prop)
          }
        manure_non_county_all.push(manure_non_county_titles)
        }
      for (prop in feature['properties']){
          manure_non_feature.push(feature['properties'][prop])
      }
      manure_non_county_all.push(manure_non_feature)
    })
  data['proc_nonpts']['features'].forEach(function(feature){
    proc_feature = []
      if (proc_county_all.length == 0){
          for (prop in feature['properties']){
          proc_county_titles.push(prop)
          }
          proc_county_all.push(proc_county_titles)
        }
      for (prop in feature['properties']){
          proc_feature.push(feature['properties'][prop])
      }
      proc_county_all.push(proc_feature)
    })

    csv_msw_c = msw_county_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_crop_c = crop_county_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_manure_c = manure_county_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_manure_non_c = manure_non_county_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_proc_c = proc_county_all.map(function(d){
                            return d.join();
                        }).join('\n');

var file_name=["msw"+county_selected+".csv","crop"+county_selected+".csv","manure"+county_selected+".csv","manure_nonpts"+county_selected+".csv","proc_nonpts"+county_selected+".csv"];
var urlList =[csv_msw_c,csv_crop_c,csv_manure_c,csv_manure_non_c,csv_proc_c];

var filenameSave ="biomass_in_"+county_selected;

password_field = document.getElementById("password");
password_field.style.display = 'block';
login = document.getElementById("login");
login.addEventListener("click", function(){
  password_choice = document.getElementById("secret_password").value;
  $.getJSON("/check_password", {
  password: password_choice,
}, function(response) {
  password_field = document.getElementById("password");
  password_field.style.display = 'none';
  if (response['validity'] == 'True'){
          zipAndDownloadFiles(urlList, file_name, filenameSave);
        }
        else{
          alert('Wrong Password')
        }
      });
  password_field.style.display = 'none';
    });
  });
});

// Report a data problem by clicking on a point
report = document.getElementById('report');
report_location = document.getElementById('report-location');
report.addEventListener("click", function(){
  report_location.style.display = 'block';
  newpointLayer.addListener('click', function(event) {
    type_clicked = event.feature.getProperty('Type');
    obj_id = event.feature.getProperty('OBJECTID');
    name_id = '';
    facility = 'biomass';
    window.location.href = 'static/submit_form.html?type='+type_clicked+'&facility='+facility+'&id='+obj_id+'&name='+name_id;
  });
  pointLayer.addListener('click', function(event) {
    type_clicked = event.feature.getProperty('Type');
    obj_id = event.feature.getProperty('OBJECTID');
    name_id = event.feature.getProperty('NAME');
    facility = 'energy';
    window.location.href = 'static/submit_form.html?type='+type_clicked+'&facility='+facility+'&id='+obj_id+'&name='+name_id;
  });
})


// Create an infowindow that would pop up when clicking over the basemap points layer that would display
// the capacity of each point
var infowindow = new google.maps.InfoWindow();
pointLayer.addListener('click', function(event) {
  index = event.feature.getProperty("Type");
  if (index == 'AD_pts'){
    cap = (Math.round(event.feature.getProperty("Equivalent Generation")/1000*10)/10).toLocaleString();
    load = (Math.round(event.feature.getProperty("DayloadBDT")*365)).toLocaleString();
    name = event.feature.getProperty("NAME")
    facility_type = event.feature.getProperty("Facility_type")
    feedstock = event.feature.getProperty("Feedstock")
    var html = "<strong>" + name + " WWTP</strong></br>" +
              "Facility type: "+ facility_type +"</br>" +
              "Feedstock: "+ feedstock + "</br>" +
              "Additional Mass Load: " + load + " BDT/y </br>" +
              "(Equivalent Generation: " + cap + " MWh/y)";
  }
  if (index == 'COMB_pts'){
    cap = (Math.round(event.feature.getProperty("Equivalent Generation")/1000*10)/10).toLocaleString();
    load = (Math.round(event.feature.getProperty("YearLoadBDT"))).toLocaleString();
    name = event.feature.getProperty("NAME")
    var html = "<strong>" + name + "</strong></br>" +
                "Additional Mass Load: " + load + " BDT/y </br>" +
                " (Equivalent Generation: " + cap + " MWh/y)";
  }
  if (index == 'W2E_pts'){
    cap = (Math.round(event.feature.getProperty("Equivalent Generation")/1000*10)/10).toLocaleString();
    load = (Math.round(event.feature.getProperty("DayLoadBDT")*365)).toLocaleString();
    name = event.feature.getProperty("Name")
    facility_type = event.feature.getProperty("Facility_type")
    feedstock = event.feature.getProperty("Feedstock")
    var html = "<strong>" + name + "</strong></br>"+
                "Facility type: "+ facility_type +"</br>" +
                "Feedstock: "+ feedstock + "</br>" +
                "Additional Mass Load: " + load + " BDT/y </br>" +
                "(Equivalent Generation: " + cap + " MWh/y)";
  }
    infowindow.setContent(html);
    infowindow.setPosition(event.latLng);
    infowindow.setOptions({disableAutoPan: true});
    infowindow.open(map);

});


// Set the hovering capability over counties to display the county total in the box
polyLayer.addListener('mouseover', function(event) {
  CID = event.feature.getProperty("CID")
  var year = document.getElementById('myYears').value
  $.getJSON("/total_county", {
      cid: CID,
      fid: 0,
      lng: event.latLng.lng(),
      lat: event.latLng.lat(),
      year: year,
      moisture: analysis_params.moisture,
      energy_type: analysis_params.energy,
      content: analysis_params.content,
      vizSelection: analysis_params.vizSelection,
    }, function(data) {
      total = Math.round(data['county_total' + analysis_params.potential])
      total_wt = Math.round(data['county_total_wt' + analysis_params.potential])
      total_thermal = Math.round(data['thermal_total'])

    var results = document.getElementById('county_total');
    var results_wt = document.getElementById('county_total_wt');
    var thermal_results = document.getElementById('thermal_total');
    results.value = total.toLocaleString();
    results_wt.value = total_wt.toLocaleString();
    thermal_results.value = total_thermal.toLocaleString();
    results.style.fontSize = "12px";
    results_wt.style.fontSize = "12px";
    thermal_results.style.fontSize = "12px";
    })
});

// Set the hovering capability over census blocks to display the total in the blocks
polyLayer_thermal.addListener('mouseover', function(event) {
  FID = event.feature.getProperty("FID")
  CID = event.feature.getProperty("CID")
  var year = document.getElementById('myYears').value
  $.getJSON("/total_county", {
      cid: CID,
      fid: FID,
      lng: event.latLng.lng(),
      lat: event.latLng.lat(),
      year: year,
      moisture: analysis_params.moisture,
      energy_type: analysis_params.energy,
      content: analysis_params.content,
      vizSelection: analysis_params.vizSelection,
    }, function(data) {
      total = Math.round(data['county_total'+analysis_params.potential])
      total_thermal = Math.round(data['thermal_total']*1000)/1000
      total_wt = Math.round(data['county_total_wt'+analysis_params.potential])

    var results = document.getElementById('county_total');
    var results_wt = document.getElementById('county_total_wt');
    var thermal_results = document.getElementById('thermal_total');
    results.value = total.toLocaleString();
    results_wt.value = total_wt.toLocaleString();
    thermal_results.value = total_thermal.toLocaleString();
    results.style.fontSize = "12px";
    results_wt.style.fontSize = "12px";
    thermal_results.style.fontSize = "12px";
    })
});

// Create an infowindow that would pop up when clicking over the biomass points layer that would display
// the capacity of each point
var infowindow = new google.maps.InfoWindow();
newpointLayer.addListener('click', function(event) {
  type_biomass = event.feature.getProperty("Type");
  // As thermochemical facilities do not have a tag but are listed as dry we need to do the step below to filter
  if (analysis_params.energy == '_dry'){
          moisture = '_dry'
        }
      else{
        moisture = analysis_params.moisture
      }
  if (type_biomass == 'manure') {;
    biomass_val = Math.round(getTotalBiomass(event.feature, analysis_params.energy, '', analysis_params.content, analysis_params.potential, analysis_params.year))
    biomass_val_str = biomass_val.toLocaleString();
    html = '<strong>' + type_biomass + '</strong> ' + event.feature.getProperty("CAFO") + '</br>' + 'biomass = ' + biomass_val_str + ' BDT/y';
  }
  if (type_biomass == 'msw') {
    biomass_val = Math.round(getTotalBiomass(event.feature, analysis_params.energy, '', analysis_params.content, analysis_params.potential, analysis_params.year))
    biomass_val_str = biomass_val.toLocaleString();
    html = '<strong>Municipal Solid Waste</strong>' + '</br>' + 'biomass = ' + biomass_val_str + ' BDT/y';
  }
  if (type_biomass == 'crop') {
    if (moisture == ''){
      res_val = Math.round(getTotalBiomass(event.feature, analysis_params.energy, '_dry', analysis_params.content, analysis_params.potential, analysis_params.year));
      cull_val = Math.round(getTotalBiomass(event.feature, analysis_params.energy, '_wet', analysis_params.content, analysis_params.potential, analysis_params.year));
      res_val_str = res_val.toLocaleString();
      cull_val_str = cull_val.toLocaleString();
      html = '<strong>' + event.feature.getProperty("CROP") + '</strong>' + '</br>' + 'residual biomass = ' + res_val_str + ' BDT/y' + 
                                                '</br>' + 'cull biomass = ' + cull_val_str + ' BDT/y';
      }
    else {
      res_val = Math.round(getTotalBiomass(event.feature, analysis_params.energy, '_dry', analysis_params.content, analysis_params.potential, analysis_params.year));
      res_val_str = res_val.toLocaleString();
      if (analysis_params.moisture == '_dry' || analysis_params.energy == '_dry') {
        condition = 'residual'
      }
      if (analysis_params.moisture == '_wet') {
        condition = 'cull'
      }
      html = event.feature.getProperty("CROP") + '</br>' + condition+' biomass = ' + res_val_str + ' BDT/year'
    }
  }
    infowindow.setContent(html);
    infowindow.setPosition(event.latLng);
    infowindow.setOptions({disableAutoPan: true});
    infowindow.open(map);
});


// Set up the zoom button, searchbox, legend and results sections
var zoomButton = document.getElementById('buttonZoom')
var legend = document.getElementById('legend')
var results = document.getElementById('results')
var input = document.getElementById('pac-input');
var searchBox = new google.maps.places.SearchBox(input);
legend = populateLegend(legend, analysis_params.vizSelection);
map.controls[google.maps.ControlPosition.RIGHT_TOP].push(zoomButton);
map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);
map.controls[google.maps.ControlPosition.RIGHT_TOP].push(results);
map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

// Bias the SearchBox results towards current map's viewport.
map.addListener('bounds_changed', function() {
  searchBox.setBounds(map.getBounds());
});

// Listen for the event fired when the user selects a prediction and retrieve
// more details for that place.
markers = []
searchBox.addListener('places_changed', function() {
  markers = setSearchBox(map, searchBox, markers)
});

// When the zoom button is clicked zoom extend to CA
$("#buttonZoom").click(function(event) {
  map.panTo({
      lat: 37.8553618,
      lng: -119.9742504});
  map.setZoom(6);
});

// Set up clicking capability on map. When click, creates a buffer and shows the biomass points 
//that fall inside the buffer.
polyLayer.addListener('click', function(event){
  lat_click = event.latLng.lat();
  lng_click = event.latLng.lng()
  CID_click = event.feature.getProperty("CID")
  // First remove any previous points
  newpointLayer.forEach(function(feature) {
    newpointLayer.remove(feature);
  });
  // Create a marker to illustrate the click point and get lat, lng
	positioner = placeMarker(event.latLng, positioner);
	var place_lat_lon = event.latLng

  // Get the buffer radius set by user and year value
  var buffer_radius = document.getElementById('buffer_radius').value
  var year = document.getElementById('myYears').value

  // Send the info to python to perform calculation and returns a geojson of the selected points 
  // which are added to the newpointLayer.
  
	$.getJSON("/lat_lng", {
		lat: lat_click,
		lng: lng_click,
		buffer: buffer_radius,
    year: year,
    moisture: analysis_params.moisture,
    energy_type: analysis_params.energy,
    content: analysis_params.content,
    potential: analysis_params.potential
	}, function(data) {
		newpointLayer.addGeoJson(data['manure']);
    newpointLayer.addGeoJson(data['msw']);
    newpointLayer.addGeoJson(data['crop']);
    setNewPointLayerStyle(newpointLayer, analysis_params);
    column_name = 'total_biomass' + '_' + year

    total_buffer = data['total_biomass'];
    total_buffer_wt = data['total_biomass_wt'];
    msw_all = []
    crop_all = []
    manure_all = []
    msw_titles = []
    crop_titles = []
    manure_titles = []
    newpointLayer.forEach(function(feature){
      msw = []
      crop = []
      manure = []
      if (feature['f']['Type'] == 'msw'){
        if (msw_all.length == 0){
          for (prop in feature['f']){
          msw_titles.push(prop)
          }
          msw_all.push(msw_titles)
        }
        for (prop in feature['f']){
          msw.push(feature['f'][prop])
          }
        msw_all.push(msw)
        }
      if (feature['f']['Type'] == 'crop'){
        if (crop_all.length == 0){
          for (prop in feature['f']){
          crop_titles.push(prop)
          }
          crop_all.push(crop_titles)
        }
        for (prop in feature['f']){
          crop.push(feature['f'][prop])
          }
        crop_all.push(crop)
        }

      if (feature['f']['Type'] == 'manure'){
        if (manure_all.length == 0){
          for (prop in feature['f']){
          manure_titles.push(prop)
          }
          manure_all.push(manure_titles)
        }
        for (prop in feature['f']){
          manure.push(feature['f'][prop])
          }
        manure_all.push(manure)
        }
        
    })

    // Get the total biomass in county clicked
    $.getJSON("/total_county", {
      cid: CID_click,
      fid: 0,
      lng: lng_click,
      lat: lat_click,
      year: year,
      moisture: analysis_params.moisture,
      energy_type: analysis_params.energy,
      content: analysis_params.content,
      vizSelection: analysis_params.vizSelection,
      }, function(data) {
        total_county = Math.round(data['county_total'+analysis_params.potential]);
        total_wt_county = Math.round(data['county_total_wt'+analysis_params.potential])
        var county_name = data['name']

  // Set up the results text
  var total_text = "<br />" + county_name + " County Total =  " + total_county.toLocaleString() + " BDT/y";
  var total_wt_text = "<br /> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp; (" + total_wt_county.toLocaleString() + " wet tonnes/y)</br>";
  var buffer_text = "<br />Inside Buffer Total =  " + total_buffer.toLocaleString() +" BDT/y";
  var buffer_wt_text = "<br /> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp; (" + total_buffer_wt.toLocaleString() +" wet tonnes/y)";
  var results = document.getElementById('results');
  results.style.fontSize = "14px";
  // Remove any previous results
  var elem = document.getElementById('res');
  if (elem !== null) {
    document.getElementById('res').remove()
  }
  var div = document.createElement('div');
  div.id = 'res'
  div.innerHTML = total_text + total_wt_text+ buffer_text+ buffer_wt_text;
  results.appendChild(div);
  })

      // Set up download button
  var download_icon = document.getElementById('download');
  if (download_icon.style.display == ''){
    download_icon.style.display = "inline-block";
  }

});
  });
var download_icon = document.getElementById('download');
  // Set up the download capability to download a geojson of the biomass
  download_icon.addEventListener('click', function(){
    csv_msw = msw_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_crop = crop_all.map(function(d){
                            return d.join();
                        }).join('\n');
    csv_manure = manure_all.map(function(d){
                            return d.join();
                        }).join('\n');

var file_name_buffer=["msw.csv","crop.csv","manure.csv"];

var urlList_buffer =[csv_msw,csv_crop,csv_manure];
var filenameSave_b ="biomass_in_buffer";

password_field = document.getElementById("password_poly");
password_field.style.display = "inline-block";
login = document.getElementById("login_poly");
login.addEventListener("click", function(){
  password_choice = document.getElementById("secret_password_poly").value;
  $.getJSON("/check_password", {
  password: password_choice,
}, function(response) {
  password_field = document.getElementById("password_poly");
  if (response['validity'] == 'True'){
          zipAndDownloadFiles(urlList_buffer, file_name_buffer, filenameSave_b);
        }
        else{
          alert('Wrong Password')
        }
      });
  password_field.style.display = 'none';
    });
  }) 

// Set up clicking capability on map. When click, creates a buffer and shows the biomass points 
//that fall inside the buffer.
polyLayer_thermal.addListener('click', function(event){
  // First remove any previous points
  newpointLayer.forEach(function(feature) {
    newpointLayer.remove(feature);
  });
  // Create a marker to illustrate the click point and get lat, lng
  positioner = placeMarker(event.latLng, positioner);
  var place_lat_lon = event.latLng

  // Get the buffer radius set by user and year value
  var buffer_radius = document.getElementById('buffer_radius').value
  var year = document.getElementById('myYears').value

  // Send the info to python to perform calculation and returns a geojson of the selected points 
  // which are added to the newpointLayer.  
  $.getJSON("/lat_lng", {
    lat: event.latLng.lat(),
    lng: event.latLng.lng(),
    buffer: buffer_radius,
    year: year,
    moisture: analysis_params.moisture,
    energy_type: analysis_params.energy,
    content: analysis_params.content,
    potential: analysis_params.potential,
  }, function(data) {
    newpointLayer.addGeoJson(data['manure']);
    newpointLayer.addGeoJson(data['msw']);
    newpointLayer.addGeoJson(data['crop']);
    setNewPointLayerStyle(newpointLayer, analysis_params);
    column_name = 'total_biomass' + '_' + year

    total_buffer = data['total_biomass'];
    total_buffer_wt = data['total_biomass_wt'];
    msw_all = []
    crop_all = []
    manure_all = []
    msw_titles = []
    crop_titles = []
    manure_titles = []
    newpointLayer.forEach(function(feature){
      msw = []
      crop = []
      manure = []
      if (feature['f']['Type'] == 'msw'){
        if (msw_all.length == 0){
          for (prop in feature['f']){
          msw_titles.push(prop)
          }
          msw_all.push(msw_titles)
        }
        for (prop in feature['f']){
          msw.push(feature['f'][prop])
          }
        msw_all.push(msw)
        }
      if (feature['f']['Type'] == 'crop'){
        if (crop_all.length == 0){
          for (prop in feature['f']){
          crop_titles.push(prop)
          }
          crop_all.push(crop_titles)
        }
        for (prop in feature['f']){
          crop.push(feature['f'][prop])
          }
        crop_all.push(crop)
        }

      if (feature['f']['Type'] == 'manure'){
        if (manure_all.length == 0){
          for (prop in feature['f']){
          manure_titles.push(prop)
          }
          manure_all.push(manure_titles)
        }
        for (prop in feature['f']){
          manure.push(feature['f'][prop])
          }
        manure_all.push(manure)
        }
        
    })

    // Get the total biomass in county clicked
    $.getJSON("/total_county", {
      cid: CID,
      fid: FID,
      lng: event.latLng.lng(),
      lat: event.latLng.lat(),
      year: year,
      moisture: analysis_params.moisture,
      energy_type: analysis_params.energy,
      content: analysis_params.content,
      vizSelection: analysis_params.vizSelection,
      }, function(data) {
        total = Math.round(data['county_total'+analysis_params.potential])
        total_wt = Math.round(data['county_total_wt'+analysis_params.potential])

  // Set up the results text
  var total_text = ''
  var total_wt_text = ''
  var buffer_text = "<br />Inside Buffer Total =  " + total_buffer.toLocaleString() +" BDT/y";
  var buffer_wt_text = "<br /> &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp; (" + total_buffer_wt.toLocaleString() +" wet tonnes/y)";
  var results = document.getElementById('results');
  results.style.fontSize = "14px";
  // Remove any previous results
  var elem = document.getElementById('res');
  if (elem !== null) {
    document.getElementById('res').remove()
  }
  var div = document.createElement('div');
  div.id = 'res'
  div.innerHTML = total_text + total_wt_text+ buffer_text+ buffer_wt_text;
  results.appendChild(div);
  })

  // Set up download button
  var download_icon = document.getElementById('download');
  if (download_icon.style.display == ''){
    download_icon.style.display = "inline-block";
  }
  });
});

var download_icon = document.getElementById('download');
}
