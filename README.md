## **Semantic enrichment processor**

The notion of **multiple aspect trajectory** (MAT) has been recently introduced in the literature to represent movement data that is heavily semantically enriched with dimensions (aspects) representing various types of semantic information (e.g., stops, moves, weather, traffic, events, and points of interest).
Aspects may be large in number, heterogeneous, or structurally complex. Although there is a growing volume of literature addressing the modelling and analysis of multiple aspect trajectories, the community suffers from a general lack of publicly available datasets. This is due to privacy concerns that make it difficult to publish such type of data, and to the lack of tools that are capable of linking raw spatio-temporal data to different types of semantic contextual data. With the semantic enrichment processor we want to show that it is possible to have a component within the transport cloud able to enrich trajectories with multiple aspects, and that it is able to use of a variety of external data sources during such process.


## **Semantic enrichment processor installation procedure**

The semantic enrichment processor consists of a set of Python scripts (plus a set of additional assets) which make exclusively use of open-source libraries. In the following we illustrate the installation procedure. The procedure has been tested on Windows 10, Ubuntu (version > 20.x), and macOS.

1. The first step requires installing a Python distribution that includes a package manager. To this end we recommend installing [Anaconda](https://www.anaconda.com/products/distribution), a cross-platform Python package manager and environment-management system which satisfies the above criteria.

2. Once Anaconda has been installed, the next step requires to set up a virtual environment containing the open-source libraries that the processor requires. To this end, we provide a YAML file, i.e., ```mat_builder.yml```, that can be used to set up the environment. The user must first open an Anaconda powershell prompt. Then, the user must type in the prompt ```conda env create -f path\mat_builder.yml -n name_environment```, where ```path``` represents the path in which ```mat_builder.yml``` is located, while ```name_environment``` represents the name the user wants to assign to the virtual environment.

3.	Once the environment has been created, the user must activate it in the prompt by typing ```conda activate name_environment```.


## **Use of the semantic enrichment processor**

The semantic enrichment processor can be used in a variety of ways (extensive walkthroughs will be provided in the deliverable 4.8, which will be accessible [here](https://mobidatalab.eu/publications/). Below, we provide some brief explanations. 

First, one must open a command line and then activate the virtual environment that has been prepared during the installation procedure -- this can be done by typing ```conda activate name_environment```. 
Once this is done, the user can:

1. use the semantic enrichment processor locally via an interactive user interface. To this end, the user must type ```python mat_builder_ui.py```.
In the command line it will then appear an URL pointing to the user interface that the user will be able to access with any web browser of preference.

2. The functionalities of the modules provided with the processor can be accessed via API end-points. To this end, we refer the reader
to the Python scripts ```mat_builder_api.py```, which sets up a server with the API end-points associated with the various modules, and the script ```examples_api_request.py```, which remotely access the aforementioned end-points via HTTP POST and GET requests. For more information on the API endpoints the user can use the server '\docs' endpoint.

3. Finally, the functionalities provided by the various modules included with the processor can also be used in one's own Python script. 
To this end, we refer the reader to the example provided in the script ```mat_builder_cli.py```.


## Overview on **MAT-building pipeline**, **modules** and **input datasets**

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

Please, refer to the ```datasets``` folder for a viable example of such dataset.

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
    
  For viable examples of POI datasets, please have a look at the datasets in the ```datasets``` folder. See also the ```misc``` folder for the ```generate dataset POI from OpenStreetMap.ipynb``` notebook,
  which contains an example on how to generate a POI dataset from OpenStreetMap data that is compatible with the semantic enrichment processor.


- **Move**: trajectories are enriched with the move segments. The segments can also be augmented with the transportation mean probably used.


- **Weather**: trajectories are enriched with weather conditions. Such information must be provided via a pandas DataFrame in the form of daily weather conditions, stored according to the 
  Parquet format, and must have the following columns:
  - ```DATE```: date in which the weather observation was recorded (string or datetime64).
  - ```TAVG_C```: average temperature in celsius (float).
  - ```DESCRIPTION```: weather conditions (string).
    
  For viable examples of weather conditions datasets, please look at the datasets in the ```datasets``` folder. See also the ```misc``` folder for the ```generate dataset weather from Meteostat.ipynb``` notebook, which contains an example on how to generate a weather dataset from Meteostat data that is compatible with the semantic enrichment processor.


- **Social media** : trajectory users are enriched with their social media posts. Social media data must be provided via a pandas DataFrame stored according to 
  the Parquet format and must have the following columns:
  - ```tweet_ID```: ID of the tweet (integer)
  - ```text```: post text (string)
  - ```tweet_created```: timestamp of the tweet (datetime64)
  - ```uid```: identifier of the user who posted the tweet.
 
  For a viable example of a social media dataset, please look at the datasets in the ```datasets``` folder.


## **Datasets**

For more details on the datasets included with the semantic enrichment processor, please see the ```README.md``` in the ```datasets``` folder. 
At the moment, a dataset related to the city of Rome has been provided.


## **Details on the datasets of multiple aspect trajectories generated by the semantic enrichment processor**

The Enrichment module within the semantic enrichment processor archives datasets of multiple aspect trajectories in RDF knowledge graphs, saved in the Turtle format.

The content of the knowledge graph is structured according to a slightly customized version of the [STEP v2 ontology](http://talespaiva.github.io/step/), which has been uploaded in the ```ontology``` folder under the file name ```step_derived.owl``` (this can be opened with, e.g., [Protege'](https://protege.stanford.edu/software.php)).

The RDF knowledge graph generated by the semantic enrichment processor can be imported in any popular triplestore of choice (e.g., [GraphDB](https://www.ontotext.com/products/graphdb/)), and queried via SPARQL queries. For examples of SPARQL v1.1 queries, please, see the ```misc/SPARQL``` folder.


## **Scientific literature**

The semantic enrichment processor is built upon the research carried out for the MAT-Builder system. For more detailed information, refer to the scientific literature provided below.

F. Lettich, C. Pugliese, C. Renso and F. Pinelli, "Semantic Enrichment of Mobility Data: A Comprehensive Methodology and the MAT-BUILDER System," in IEEE Access, vol. 11, pp. 90857-90875, 2023.

```
@ARTICLE{10227262,
  author={Lettich, Francesco and Pugliese, Chiara and Renso, Chiara and Pinelli, Fabio},
  journal={IEEE Access}, 
  title={Semantic Enrichment of Mobility Data: A Comprehensive Methodology and the MAT-BUILDER System}, 
  year={2023},
  volume={11},
  number={},
  pages={90857-90875},
  doi={10.1109/ACCESS.2023.3307824}}
```

Lettich, F., Pugliese, C., Renso, C. and Pinelli, F., 2023, March. A general methodology for building multiple aspect trajectories. 
In Proceedings of the 38th ACM/SIGAPP Symposium on Applied Computing (pp. 515-517).

```
@inproceedings{lettich2023general,
  title={A general methodology for building multiple aspect trajectories},
  author={Lettich, Francesco and Pugliese, Chiara and Renso, Chiara and Pinelli, Fabio},
  booktitle={Proceedings of the 38th ACM/SIGAPP Symposium on Applied Computing},
  pages={515--517},
  year={2023}
}
```

C. Pugliese, F. Lettich, C. Renso, F. Pinelli, Mat-builder: a system to build semantically
enriched trajectories. In Proceedings of the 23rd IEEE International Conference on Mobile Data Management, Cyprus, 2022

```
@inproceedings{Pugliese22,
title={Mat-builder: a system to build semantically enriched trajectories},
author={Pugliese, Chiara and Lettich, Francesco and Renso, Chiara and Pinelli, Fabio},
booktitle={2022 23rd IEEE International Conference on Mobile Data Management (MDM)},
pages={274--277},
year={2022},
organization={IEEE}
}
```
