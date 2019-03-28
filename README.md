# BioSiting_tool_LBL
The tool is located at https://biositing-tool-heroku.herokuapp.com/.


## Input Data
All the input data are currently stored in the `GIS_data` folder. 

The data is stored in excel form inside the `data_biositingtool_withwetweight.xlsx` file. Each sheet of the excel file represents various biomass and energy data. The sheet labeled `key` includes information on the traslation of the column names and data sources. The sheet labeled `file transfer` includes the name of the shapefile that stores the information of the location of each point. 

You can change the values in any sheet of the excel file BUT you cannot alter the column names or add new sheets without editing the code. 

The location data is stored in shapefiles in the `Shapefile_Drafts` folder. They are combined with the data in the `data_biositingtool_withwetweight.xlsx` automatically through the `Data_processing.py` script. The `Data_processing.py` reads all the data from the `data_biositingtool_withwetweight.xlsx` and merges each sheet with its corresponding shapefile. It also does some data preprocessing, e.g. calculating total biomass for each county and total biomass of each type so it can be easily accessible to the user when hovering over counties and exporting data. The output of this script is stored as csv files in the `final_data` folder. This is where the biositing tools reads the information from.


## Update Data
- To save your changes into the remote Heroku repository, you need to be added as a collaborator first. Follow steps in the `Run on Heroku server` section. Once you have access to the heroku repository edit the data as needed and follow the steps below.
- Update any of the data directly into the `data_biositingtool_withwetweight.xlsx`.
- Open your terminal window and navigate into the `BioSiting_tool` folder.
- Run `python Data_processing.py`. This will take a few minutes.
- To save your changes into the remote Heroku repository, run `git add .`, `git commit -m "data update"` and `git push heroku master` to send the updated data on the server.
- If you are running the tool locally with Docker, you will need to uninstall and reinstall your docker to include the new data before re-running (see `Run Locally with Docker` section).


## Run on Heroku server
The tool is currently hosted on [heroku server](https://biositing-tool-heroku.herokuapp.com/).

To access the code on the server please email okavvada@gmail.com to be added as a collaborator. Once access has been grated you can get a local copy of the code to make changes.

- Open your terminal and inside the local repository run `heroku git:remote -a biositing-tool-heroku`. This will connect the heroku server to your local computer.
- Once edits are made add, commit and push your edits back to the heroku server (see Update Data section).


## Run Locally with Docker
### Model Dependencies
The core of the Biositing model is written in Python 2.7. The model can be run through docker. Docker will take care of the dependencies and will create an instance of the tool locally on your computer. Please install [Docker](https://docs.docker.com/docker-for-mac/install/) to be able to run the model.


### Start a local instance
The tool can be run through docker. After you have installed the dependencies you can run a local instance of the webtool. Follow these steps:

- Install [Docker](https://docs.docker.com/docker-for-mac/install/).
- Run Docker on your computer. Double-click Docker.app to run and if successfull, a whale icon will appear in the top status bar that indicates that Docker is running, and accessible from a terminal.
- Clone this repository.
- Navigate your terminal inside the repository.
- Generate a docker image by running `docker build -t flask-biositing-model:latest .` in your terminal. You only need to perform this stem ONCE - only the first time you install the Biositing model (this will take a few minutes). To run the model skip to the next step.
- Start your container by running `docker run -d -p 5000:5000 flask-biositing-model` in your terminal.
- Navigate to `localhost:5000` in Chrome or your favorite browser.
- and Done! Easy!


### Uninstall
As it is a work in progress you would need to uninstall this version before updating to an up-to-date future version. To completely uninstall please follow the steps in your terminal:

- Navigate your terminal inside the repository.
- Run `docker kill $(docker ps -q)` and `docker rm $(docker ps -a -q)` to remove all the containers.
- Run `docker rmi $(docker images -a -q)` to remove the current version.
- To reinstall redo all the steps detailed in the `Start a local instance` section