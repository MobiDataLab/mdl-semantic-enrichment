This folder contains the ```rome``` archive, which is a multi-file [7Zip](https://7-zip.org/download.html) archive.
The archive contains a dataset of 26395 trajectories from 3181 individuals (see the root folder of the archive).
The trajectories move over the city of Rome and were collected from 
OpenStreetMap. The archive contains also additional datasets, i.e., the set of
POIs within the province of Rome's boundaries (downloaded from OpenStreetMap) (see the ```poi``` subfolder), 
historical weather information (downloaded from [Meteostat](https://meteostat.net/it/)) (see the ```weather``` subfolder), and a
dataset of social media posts from the individuals which was generated synthetically (see the ```tweets``` subfolder).
All the datasets are ```pandas``` dataframes, exception for the POI dataset which is
a ```geopandas``` DataFrame. All the datasets have been stored according to the parquet format.