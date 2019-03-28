// Sets the analysis parameter of the year when the user changes the drop down menu
function yearSelect(analysis_params) {
  var myList=document.getElementById("myYears");
  analysis_params.year = myList.options[myYears.selectedIndex].value;
  return analysis_params
}

// Sets the analysis parameter of the energy when the user changes the drop down menu
function energySelect(analysis_params) {
  var myList=document.getElementById("myEnergy");
  analysis_params.energy = myList.options[myEnergy.selectedIndex].value;
  return analysis_params
}

// Sets the analysis parameter of the potential when the user changes the drop down menu
function potentialSelect(analysis_params) {
  var myList=document.getElementById("myPotential");
  analysis_params.potential = myList.options[myPotential.selectedIndex].value;
  return analysis_params
}

// Sets the analysis parameter of the moisture when the user changes the drop down menu
function moistureSelect(analysis_params) {
  var myList=document.getElementById("myMoisture");
  analysis_params.moisture = myList.options[myMoisture.selectedIndex].value;
  return analysis_params
}

// Sets the analysis parameter of the content when the user changes the drop down menu
function contentSelect(analysis_params) {
  var myList=document.getElementById("myContent");
  analysis_params.content = myList.options[myContent.selectedIndex].value;
  return analysis_params
}

// Sets the analysis parameter of the visualization parameter when the user changes the drop down menu
function vizSelect(analysis_params) {
  var myList=document.getElementById("myViz");
  analysis_params.vizSelection = myList.options[myViz.selectedIndex].value;
  layer_biomass = document.getElementById("county_biom");
  layer_wt = document.getElementById("county_wt");
  layer_thermal = document.getElementById("therm");
  if (myList.options[myViz.selectedIndex].value == 'biomass'){
    layer_biomass.style.display = "block";
    layer_wt.style.display = "block";
    layer_thermal.style.display = "none";
  }
  else{
    layer_biomass.style.display = "none";
    layer_wt.style.display = "none";
    layer_thermal.style.display = "block";
  }

  return analysis_params
}

function countySelect(){
  var myList = document.getElementById('myCounty');
  return myList.options[myCounty.selectedIndex].value;
}

function infoWindow(id) {
    var x = document.getElementById(id);
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

// Sets the styling for the basemap points for AD, COMB, W2E
function setBaseMapPointsStyle(pointLayer, zoom, item, visibility){
  if (zoom>=9){
    scaled_size = 1.5
  }
  else{
    scaled_size = 1
  }
  pointLayer.setStyle(function(feature) {
    if (feature.getProperty('Type') == 'AD_pts'){
      color = 'blue';
      scale = 3.5*scaled_size;
      path = google.maps.SymbolPath.CIRCLE;
      visibility_item = document.getElementById('ADcheckBox').checked;
    }
    if (feature.getProperty('Type') == 'COMB_pts'){
      color = '#b2b2b2';
      scale = 3.5*scaled_size;
      path = google.maps.SymbolPath.CIRCLE;
      visibility_item = document.getElementById('CPcheckBox').checked;
    }
    if (feature.getProperty('Type') == 'W2E_pts'){
      color = 'yellow';
      scale = 5*scaled_size;
      path = google.maps.SymbolPath.CIRCLE;
      visibility_item = document.getElementById('W2EcheckBox').checked;
    }

        return ({cursor: 'pointer',
          visible: visibility_item,
          icon: { 
          path: path,
          strokeWeight: 0.5,
          strokeColor: 'black',
          scale: scale,
          fillColor: color,
          fillOpacity: 1,
        }
              });
	   });
}

// Sets the styling for the basemap polygons for the 2 visualization of biomass and thermal
function setBaseMapPolygonsBiomassStyle(Layer, analysis_params){
  if (analysis_params.vizSelection == 'biomass'){
    vis_biomass = true
  }
  else {
    vis_biomass = false
  }
    Layer.setStyle(function(feature) {
      if (analysis_params.energy == '_dry'){
        moisture = ''
      }
      else{
        moisture = analysis_params.moisture
      }
      column_year = 'county_total' + moisture + analysis_params.energy + analysis_params.content + '_' + analysis_params.year + analysis_params.potential
      if (feature.getProperty(column_year) > 1000000){
        color = '#165906';
      }
      if (feature.getProperty(column_year) > 100000 && feature.getProperty(column_year) < 1000000){
        color = '#219904';
      }
      if (feature.getProperty(column_year) > 1000 && feature.getProperty(column_year) < 100000) {
        color = '#9df28a';
      }
      if (feature.getProperty(column_year) < 1000){
        color = '#ffe554';
      }
      return ({visible: vis_biomass,
              fillColor: color,
              fillOpacity: 0.5,
              strokeWeight: 0.3,
              cursor: 'auto'})
      })
  }

function setBaseMapPolygonsThermalStyle(polyLayer_thermal, analysis_params){
  column_thermal = 'SUM_TotH'
  if (analysis_params.vizSelection == 'thermal_h'){
    column_thermal = 'SUM_TotH';
    vis_thermal = true;
  }
  else if (analysis_params.vizSelection == 'thermal_c'){
    column_thermal = 'SUM_TotC';
    vis_thermal = true;
  }
  else {
    vis_thermal = false
  }
  column_thermal_year = column_thermal + analysis_params.year
  polyLayer_thermal.setStyle(function(feature) {
      if (feature.getProperty(column_thermal_year) > 1){
        if (analysis_params.vizSelection == 'thermal_c'){
                color = '#0a1a3f';
        }
        if (analysis_params.vizSelection == 'thermal_h'){
                color = '#5e0e0e';
        }
      }
      if (feature.getProperty(column_thermal_year) > 0.2 && feature.getProperty(column_thermal_year) < 1){
        if (analysis_params.vizSelection == 'thermal_c'){
                color = '#0938a0';
        }
        if (analysis_params.vizSelection == 'thermal_h'){
                color = '#ce0202';
        }
      }
      if (feature.getProperty(column_thermal_year) > 0.05 && feature.getProperty(column_thermal_year) < 0.2) {
        if (analysis_params.vizSelection == 'thermal_c'){
                color = '#5a85e2';
        }
        if (analysis_params.vizSelection == 'thermal_h'){
                color = '#f47a7a';
        }
      }
      if (feature.getProperty(column_thermal_year) < 0.05){
        if (analysis_params.vizSelection == 'thermal_c'){
                color = '#cefaff';
        }
        if (analysis_params.vizSelection == 'thermal_h'){
                color = '#f7cfcf';
        }
      }
      return ({visible: vis_thermal,
              fillColor: color,
              fillOpacity: 0.6,
              strokeWeight: 0.3,
              cursor: 'auto'})
      })
}

// Sets the styling for the basemap PROC layer for the thermal visualization
function setBaseMapPROCStyle(Layer, zoom){
  if (zoom>=9){
    scaled_size = 1.5
  }
  else{
    scaled_size = 1
  }
  Layer.setStyle(function(feature) {
    if (feature.getProperty('Type') == 'DES_CBG_pts'){
      CapSt = feature.getProperty("CapSt")
      CapHW = feature.getProperty("CapHW")
      CapCW = feature.getProperty("CapCW")
      color = 'black';
      scale = 2.5*scaled_size;
      visibility_item = document.getElementById('DEScheckBox').checked;
      if (CapSt == 0 && CapHW==0 && CapCW==0){
        opacity = 0
      }
      else{
        opacity = 1
      }
    }
    if (feature.getProperty('Type') == 'PROC'){
      avg_pc = feature.getProperty("AVG_PC")
      avg_ph = feature.getProperty("AVG_PH")
      color = '#00e832';
      scale = 2.5*scaled_size;
// if you want PROC points to appear on the map, change this to true!
      visibility_item = false
      if (avg_pc == 0 && avg_ph==0){
        opacity = 0
      }
      else{
        opacity = 1
      }
    }
    return ({cursor: 'pointer',
          icon: { 
          path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
          strokeWeight: 0.5,
          strokeColor: 'black',
          strokeOpacity: opacity,
          scale: scale,
          fillColor: color,
          fillOpacity: opacity,
        },
        visible: visibility_item,
      })
  });
};

// Get max and min values of selected biomass to set the circle size
function getMaxMin(Layer, energy, moisture, content, potential, year){
  max = 0
  min = 99999999
// As thermochemical facilities do not have a tag but are listed as dry we need to do the step below
if (energy == '_dry'){
    moisture = '_dry'
    energy = ''
  }

  Layer.forEach(function(feature){
    type = feature.getProperty("Type");
    if (type == 'crop'){
      if (moisture == ''){
      res_val = getTotalBiomass(feature, energy, '_dry', content, potential, year);
      cull_val = getTotalBiomass(feature, energy, '_wet', content, potential, year);
      biomass_val = res_val + cull_val
    }
      else {
        biomass_val = getTotalBiomass(feature, energy, moisture, content, potential, year);
      }
  }
    else {
      biomass_val = getTotalBiomass(feature, energy, moisture, content, potential, year);
    }
    if (biomass_val>max){
      max=biomass_val
    }
    if (biomass_val<min){
      min=biomass_val
    }
   })
  return ([max, min])
  };

// Calculate the total biomass based on filters.
function getTotalBiomass(feature, energy, moisture, content, potential, year){
  total_biomass = 0
  // As thermochemical facilities do not have a tag but are listed as dry we need to do the step below
  if (energy == '_dry'){
    moisture = '_dry'
    energy = ''
  }
  Object.getOwnPropertyNames(feature['f']).forEach(function (propert){
        if (propert.includes(energy+'_') && propert.includes(content+'_') && propert.includes(potential) && propert.includes(year) && propert.includes(moisture+'_')){
          total_biomass += feature.getProperty(propert);
    }
  })
  return (total_biomass)
};


// Sets the styling for the biomass points when clicked
function setNewPointLayerStyle(Layer, analysis_params){
  max_min = getMaxMin(Layer, analysis_params.energy, analysis_params.moisture, analysis_params.content, analysis_params.potential, analysis_params.year);
  max = max_min[0]
  min = max_min[1]
  var rs = d3.scaleLinear()
          .domain([0, max])
          .range([2,7]);

  Layer.setStyle(function(feature) {
    type = feature.getProperty("Type");
    // As thermochemical facilities do not have a tag but are listed as dry we need to do the step below
    if (analysis_params.energy == '_dry'){
          moisture = '_dry'
        }
      else{
        moisture = analysis_params.moisture
      }
    if (type == 'crop'){
      if (moisture == ''){
        res_val = getTotalBiomass(feature, analysis_params.energy, '_dry', analysis_params.content, analysis_params.potential, analysis_params.year);
        cull_val = getTotalBiomass(feature, analysis_params.energy, '_wet', analysis_params.content, analysis_params.potential, analysis_params.year);
        size = rs(res_val+cull_val)
        if (res_val == 0 && cull_val == 0){
          opacity = 0
        }
        else{
          opacity = 1
        }
      }
      else{
        biomass_val = getTotalBiomass(feature, analysis_params.energy, analysis_params.moisture, analysis_params.content, analysis_params.potential, analysis_params.year);
        size = rs(biomass_val)
        if (biomass_val == 0){
          opacity = 0
        }
        else{
          opacity = 1
        }
      }
    }
    else{
      biomass_val = getTotalBiomass(feature, analysis_params.energy, analysis_params.moisture, analysis_params.content, analysis_params.potential, analysis_params.year);
      size = rs(biomass_val)
      if (biomass_val == 0){
        opacity = 0
      }
      else{
        opacity = 1
      }
    }
    if (size>7){
      size=7
    }
    return ({cursor: 'pointer',
      icon: { 
        path: google.maps.SymbolPath.CIRCLE,
        strokeWeight: 0.5,
        strokeColor: 'black',
        strokeOpacity: opacity,
        scale: size,
        fillColor: 'red',
        fillOpacity: opacity,
      }
    })
  });
};

// Generates the address searchbox
function setSearchBox(map, searchBox, markers){
  var places = searchBox.getPlaces();
  if (places.length == 0) {
    return;
    }
  // Clear out the old markers.
  markers.forEach(function(marker) {
    marker.setMap(null);
  });
  markers = [];

  // For each place, get the icon, name and location.
  var bounds = new google.maps.LatLngBounds();
  places.forEach(function(place) {
    if (!place.geometry) {
      console.log("Returned place contains no geometry");
      return;
    }
    var icon = {
      url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
      size: new google.maps.Size(25, 25),
      origin: new google.maps.Point(0, 0),
      scaledSize: new google.maps.Size(25, 25)
    };

    // Create a marker for each place.
    markers.push(new google.maps.Marker({
      map: map,
      draggable: true,
      icon: icon,
      title: place.name,
      position: place.geometry.location
    }));

    if (place.geometry.viewport) {
      // Only geocodes have viewport.
      bounds.union(place.geometry.viewport);
    } else {
      bounds.extend(place.geometry.location);
    }
    });
  map.fitBounds(bounds);
  return markers
  }

// Generates a marker at the clicked location
function placeMarker(location, positioner) {
    positioner.forEach(function(marker) {
            marker.setMap(null);
          });
    positioner = [];
    positioner.push(new google.maps.Marker({
        position: location, 
        icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        map: map
    }));  
  return positioner
}


// Allows the download functionality
function zipAndDownloadFiles(urls, file_name, filenameSave){
  zip = new JSZip();
  for (i=0;i<urls.length;i++){
    zip.file(file_name[i], urls[i], {binary:true});
  }
  downloadZip(filenameSave)
}

function downloadZip(filenameSave){
   zip.generateAsync({type:"blob"})
      .then(function(content)
      {
        var a = document.createElement("a");
        a.download = filenameSave;
        a.href = URL.createObjectURL(content);
        a.click();
      });
}


// Generates the thermal layer points for PROC and DES_CBG
function setPROCLayer(map, PROCLayer, analysis_params) {
  PROCLayer.setMap(null);
  PROCLayer = new google.maps.Data({map:map});
  if ((analysis_params.vizSelection == 'thermal_h') || (analysis_params.vizSelection == 'thermal_c')){
    right_top_lat = map.getBounds().getNorthEast().lat();
    right_top_lon = map.getBounds().getNorthEast().lng();
    left_bottom_lat = map.getBounds().getSouthWest().lat();
    left_bottom_lon = map.getBounds().getSouthWest().lng();
    right_bottom_lat = right_top_lat
    right_bottom_lon = left_bottom_lon

    $.getJSON("/PROC", {
        left_bottom_lon: left_bottom_lon,
        left_bottom_lat: left_bottom_lat,
        right_top_lon: right_top_lon,
        right_top_lat: right_top_lat,
      }, function(data) {
       setBaseMapPROCStyle(PROCLayer, map.zoom)
       PROCLayer.addGeoJson(data['PROC']);
       PROCLayer.addGeoJson(data['DES_CBG']);

       // Create an infowindow that would pop up when hovering over the PROC layer that would display
       // the number of points in cluster.
       var infowindow = new google.maps.InfoWindow();
       PROCLayer.addListener('click', function(event) {
        if (event.feature.getProperty('Type') == 'PROC'){
          avg_ph = Math.round((event.feature.getProperty("AVG_PH")/1000)).toLocaleString();
          avg_pc = Math.round((event.feature.getProperty("AVG_PC")/1000)).toLocaleString();

          if (event.feature.getProperty("number_of_points") == '1'){
            var html = "Process heating = " + avg_ph + " GW</br> " +
                        "Process cooling = " + avg_pc + " GW</br> ";
          }
          else{ 
          num_process = event.feature.getProperty("number_of_points");
          var html = "Number of processors: " + num_process + "</br> " +
                    "Process heating = " + avg_ph + " MWh/y</br> " +
                    "Process cooling = " + avg_pc + " MWh/y</br> ";
          }
      }
      if (event.feature.getProperty('Type') == 'DES_CBG_pts'){
          steam = Math.round(event.feature.getProperty("CapSt")*10)/10;
          hot_w = Math.round(event.feature.getProperty("CapHW")*10)/10;
          chilled_w = Math.round(event.feature.getProperty("CapCW")*10)/10;
          var html = "Steam Capacity: " + steam + " MW </br>" +
                      "Hot Water Capacity: " + hot_w + " MW </br>"+
                      "Chilled Water Capacity: " + chilled_w + " MW";
      }

        infowindow.setContent(html);
        infowindow.setPosition(event.latLng);
        infowindow.setOptions({disableAutoPan: true});
        infowindow.open(map);
        });
      });
  }
  else {
    PROCLayer.setMap(null);
    PROCLayer = new google.maps.Data({map:map});
  }
  return PROCLayer
}

// Generates the legend depending on the visualization selection (biomass or thermal)
function populateLegend(legend, vizSelection){
  var element =  document.getElementById('legend-title');
  if (typeof(element) != 'undefined' && element != null) {
    element.remove()
  }
    if (vizSelection == 'biomass'){
      html_text = "<div class='tooltip-wrap' id='legend-title'></br><strong>Biomass in County </br> (thousand BDT/year)</strong></br><div>" +
                  "<span class='legend-swatch' style='background-color: #ffe554;opacity: 0.6'></span>" +
                  "<span class='legend-range'><1</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #9df28a;opacity: 0.6'></span>" +
                  "<span class='legend-range'>1 - 100</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #219904;opacity: 0.6'></span>" +
                  "<span class='legend-range'>100 - 1000</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #165906;opacity: 0.6'></span>" +
                  "<span class='legend-range'>1000+</span></div></div>"
          }
    if (vizSelection == 'thermal_c'){
      html_text = "<div id='legend-title'></br><strong>Thermal Consumption in County </br>(kWh/sf-year)</strong></br><div>" +
                  "<span class='legend-swatch' style='background-color: #cefaff;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0 - 0.05</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #5a85e2;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0.05 - 0.2</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #0938a0;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0.2 - 1</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #0a1a3f;opacity: 0.6'></span>" +
                  "<span class='legend-range'>1+</span></div></div>"
          }

    if (vizSelection == 'thermal_h'){
      html_text = "<div id='legend-title'></br><strong>Thermal Consumption in County </br> (kWh/sf-year)</strong></br><div>" +
                  "<span class='legend-swatch' style='background-color: #f7cfcf;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0 - 0.05</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #f47a7a;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0.05 - 0.2</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #ce0202;opacity: 0.6'></span>" +
                  "<span class='legend-range'>0.2 - 1</span></div><div>" +
                  "<span class='legend-swatch' style='background-color: #5e0e0e;opacity: 0.6'></span>" +
                  "<span class='legend-range'>1+</span></div></div>"
          }

    parent = document.getElementById('legend');
    parent.insertAdjacentHTML("beforeend", html_text)
    return parent
}