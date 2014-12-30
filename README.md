Sibyl: Question&Answer Analyzer
===============================

## Description

Sibyl aims at extracting information from question and answer sites and storing
it into a database.

## License

Licensed under GNU General Public License (GPL), version 3 or later

## Download

* Home page: https://github.com/MetricsGrimoire/Sibyl
* Releases: https://github.com/MetricsGrimoire/Sibyl/releases
* Latest version: https://github.com/MetricsGrimoire/Sibyl.git


## Requirements

* Python >= 2.7.1
* MySQL >= 5.5
* BeautifulSoup >= 3.2.1
* SQLAlchemy >= 0.8.2
* Python requests >= 1.2.3

## Installation

Locally:

    python setup install
    
In the system:

    sudo python setup install

## Running Sibyl

First, create database as follows:

    CREATE DATABASE <databasename> CHARACTER SET utf8 COLLATE utf8_unicode_ci;

Second, you can easily run Sibyl from the cloned repository as follows:

    ~/MetricsGrimoire/Sibyl/$ python sibyl.py -t ab -l https://ask.openstack.org/ -d <databasename> -u <dbuser> -p <dbpassword>


## Running Tests

You can easily run tests for Sibyl as follows:

    ~/MetricsGrimoire/Sibyl/$ python -m unittest discover  -s ./tests/


## Improving Sibyl

Source code and ITS available on Github: https://github.com/MetricsGrimoire/Sibyl
If you want to receive updates about new versions, and keep in touch with the development team, consider subscribing to the mailing list.
It is a very low traffic list (< 1 msg a day): https://lists.libresoft.es/listinfo/metrics-grimoire


## Contact

* Mailing list at https://lists.libresoft.es/listinfo/metrics-grimoire
* IRC channel in freenode #metrics-grimoire

