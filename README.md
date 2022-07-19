## **Semantic enrichment demonstrator**

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
of semantic contextual data. With this demonstrator we want to show
that it is possible to devise a semantic enrichment processor that is able
to enrich trajectories with multiple aspects, and that it is able to
use of a variety of external data sources during such process.


## **Installation procedure**

The semantic enrichment demonstrator consists of a set of Python scripts which make exclusively use of open-source libraries. In the following we illustrate the installation procedure needed to execute the semantic enrichment demonstrator. The installation procedure has been tested on Windows 10, Ubuntu (version > 20.x), and macOS.

1. The first step requires installing a Python distribution that includes a package manager. To this end we recommend installing Anaconda, a cross-platform Python package manager and environment-management system which satisfies the above criteria.

2. Once Anaconda has been installed, the next step requires to set up a virtual environment containing the open-source libraries that our demonstrator requires during its execution. To this end we provide a YAML file, ```mat_builder.yml```, that can be used to set the environment up. More precisely, the user must first open an Anaconda powershell prompt. Then, the user must type in the prompt ```conda env create -f path\mat_builder.yml -n name_environment```, where ```path``` represents the path in which ```mat_builder.yml``` is located, while ```name_environment``` represents the name the user wants to assign to the virtual environment.

3.	Once the environment has been created, the user must activate it in the prompt by typing ```conda activate name_environment```. The user is now able to execute and use the demonstrator.


## **Usage**

To use the demonstrator one must first open a command line, then activate the virtual environment
that has been prepared during the installation procedure, and finally type ```python mat_builder.py```.
We refer the reader to the deliverable 4.7, version 1, for more information on how to use the demonstrator.
