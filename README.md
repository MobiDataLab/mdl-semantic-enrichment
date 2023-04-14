## **Semantic enrichment processor**

The notion of **multiple aspect trajectory** (MAT) has
been recently introduced in the literature to represent movement
data that is heavily semantically enriched with dimensions
(aspects) representing various types of semantic information (e.g.,
stops, moves, weather, traffic, events, and points of interest).
Aspects may be large in number, heterogeneous, or structurally
complex. Although there is a growing volume of literature
addressing the modelling and analysis of multiple aspect trajectories, 
the community suffers from a general lack of publicly
available datasets. This is due to privacy concerns that make it
difficult to publish such type of data, and to the lack of tools that
are capable of linking raw spatio-temporal data to different types
of semantic contextual data. With the semantic enrichment processor we want to show
that it is possible to have a component within the transport cloud able
to enrich trajectories with multiple aspects, and that it is able to
use of a variety of external data sources during such process.


## **Semantic enrichment processor installation procedure**

The semantic enrichment processor consists of a set of Python scripts (plus a set of additional assets) which make exclusively use of open-source libraries. In the following we illustrate the installation procedure. The procedure has been tested on Windows 10, Ubuntu (version > 20.x), and macOS.

1. The first step requires installing a Python distribution that includes a package manager. To this end we recommend installing [Anaconda](https://www.anaconda.com/products/distribution), a cross-platform Python package manager and environment-management system which satisfies the above criteria.

2. Once Anaconda has been installed, the next step requires to set up a virtual environment containing the open-source libraries that the processor requires. To this end, we provide a YAML file, i.e., ```mat_builder.yml```, that can be used to set up the environment. The user must first open an Anaconda powershell prompt. Then, the user must type in the prompt ```conda env create -f path\mat_builder.yml -n name_environment```, where ```path``` represents the path in which ```mat_builder.yml``` is located, while ```name_environment``` represents the name the user wants to assign to the virtual environment.

3.	Once the environment has been created, the user must activate it in the prompt by typing ```conda activate name_environment```.


## **Use of the semantic enrichment processor**

The semantic enrichment processor can be used in a variety of ways.
First, one must open a command line and then activate the virtual environment that has been prepared during the installation procedure -- this can be done by typing ```conda activate name_environment```. 
Once this is done, the user can:

1. use the semantic enrichment processor locally via a user interface. To this end, the user must type ```python mat_builder_ui.py```.
In the command line it will then appear an URL pointing to the user interface that the user will be able to access with any web browser of preference. 
We refer the reader to the deliverable 4.7, version 1, for an extensive walkthrough on how to use the user interface. The deliverable can be accessed [here](https://mobidatalab.eu/publications/).

2. The functionalities provided by the various modules included with the processor can also be used in one's own Python script. 
To this end, we refer the reader to the example provided in the script ```mat_builder_cli.py```.

3. Finally, the functionalities of the modules provided with the processor can be used via API end-points. To this end, we refer the reader
to the Python scripts ```mat_builder_api.py```, which sets up the API end-points associated with the various modules, and the script ```examples_api_request.py```, which uses the aforementioned end-points via API requests. 


## **MAT-building pipeline** and **modules**

The semantic enrichment processor revolves around the notion of ***MAT-building pipeline***, which is a
semantic enrichment process conducted according to a sequence of steps. Each step represents a specific macro-task
and is implemented via a module that extends the ``ModuleInterface`` abstract class. Currently, there are three modules that are of interest 
for the project's purposes: ```Preprocessing```, ```Segmentation```, and ```Enrichment```. 
To see how the modules can be used we refer the reader to the aforementioned example scripts.
For detailed information on the modules, we refer the reader to the README.md within the ```core``` folder.
In the following we provide a general overview on such modules. 

The ``Preprocessing`` module takes in input a dataset of raw trajectories and let users:

- remove outliers
- remove trajectories with few points
- compress trajectories

in order to produce a dataset of preprocessed trajectories.

The ``Preprocessing`` module requires the raw trajectory dataset to be stored in a pandas DataFrame and have the following columns:
- ```traj_id```: trajectory ID (string)
- ```user```: user ID (integer)
- ```lat```: latitude of a trajectory sample (float)
- ```lon```: longitude of a trajectory sample (float)
- ```time```: timestamp of a sample (datetime64)

The ``Segmentation`` module takes in input a dataset of trajectories, and segments each trajectory into ***stop*** and ***move segments***. The dataset must be stored in a pandas DataFrame and have the same columns required by the ```Preprocessing``` module.

The ``Enrichment`` module takes in input a dataset of trajectories, as well as their stop and move segments, and enriches trajectories and trajectory users with several aspects (or semantic dimensions). The aspects currently supported by the module are as follows:
- **Regularity**: stop segments are categorized into:
  - *systematic stops*: stops that fall in the same area more than a given number of times. They are augmented with the labels  *Home*, *Work* or *Other*.
  - *occasional stops*: stops that are not systematic.
    
  Both occasional and systematic stops are augmented with the nearest POIs. 
  The POI dataset used to augment the stops can either be downloaded from OpenStreetMap (not recommended, this operation might be quite slow),
  or supplied via a local file. In the latter case, the POI dataset must be stored in a GeoDataFrame, according to the Parquet format, and must
  have the following columns:
  - ```osmid```: POI OSM identifier (integer)
  - ```element_type```: POI OSM element type (string)
  - ```name```: POI native name (string)
  - ```name:en```: POI English name (string) 
  - ```wikidata```: POI WikiData identifier (string)
  - ```geometry```: POI geometry (GeoPandas geometry object)
  - ```category```: POI category (string)
  For viable examples of POI datasets, please have a look at the datasets in the ```datasets``` folder.


- **Move**: trajectories are enriched with the move segments. The segments can also be augmented with the transportation mean probably used.


- **Weather**: trajectories are enriched with weather conditions. Such information must be provided via a pandas DataFrame in the form of daily weather conditions, stored according to the 
  Parquet format, and must have the following columns:
  - ```DATE```: date in which the weather observation was recorded (string or datetime64).
  - ```TAVG_C```: average temperature in celsius (float).
  - ```DESCRIPTION```: weather conditions (string).
  For viable examples of weather conditions datasets, please look at the datasets in the ```datasets``` folder.


- **Social media** : trajectory users are enriched with their social media posts. Social media data must be provided via a pandas DataFrame stored according to 
  the Parquet format and must have the following columns:
  - ```tweet_ID```: ID of the tweet (integer)
  - ```text```: post text (string)
  - ```tweet_created```: timestamp of the tweet (datetime64)
  - ```uid```: identifier of the user who posted the tweet.


## **Datasets**

For more details on the dataset included with the semantic enrichment processor, please see the ```README.md``` in the ```datasets``` folder.
