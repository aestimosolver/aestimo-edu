# AESTIMO EDU 1D SELF-CONSISTENT SCHRÖDINGER-POISSON SOLVER 

## Overview

Aestimo 1D Self-consistent Schrödinger-Poisson Solver (simply aestimo) is a simple 1-dimensional (1-D) simulator for semiconductor heterostructures. Aestimo is started as a hobby at the beginning of 2012, and become a usable tool which can be used as a co-tool in an educational and scientific work. **This version of Aestimo is called 'Aestimo EDU'**. Its code is easy to understand and it can be used easily for educational purposes. For the main Aestimo release please visit: https://github.com/aestimosolver/aestimo

Hope that it also works for you. Please do not hesitate to contact us in case of any bugs found.

## Current features
* Material and alloys: GaAs, AlAs , InAs, InP, AlP, GaP, AlGaAs, InGaAs, InGaP and AlInP,
* Band structure for gamma electrons and heavy, light and split-off holes,
* Effective-mass method for electrons and 3x3 k.p method for holes,
* Carrier concentrations for gamma electrons and heavy, light and split-off holes,
* Electric field distribution,
* Electron wavefunctions,
* Non-parabolicity,
* External electric field,
* Strain for valance band calculations,

## Getting Started

See the examples subdirectory of the distribution. Also, detailed information can be found in "Using the Code" part of this document. Subscription to the aestimo-users mailing list is highly recommended for further support. For developers and people interested in latest development issues, there is an aestimo-devel mailing list.

## License

Aestimo EDU is Copyrighted by (C) 2013-2020 by Aestimo group. This software is distributed under the terms of the GNU General Public License v3, see ~/COPYING file or http://www.gnu.org/copyleft/gpl.txt . This means that everyone is free to use, change, share and share the changes.

For the list of contributors, see ~/AUTHORS.md 

## Getting Help

Before asking any question, please visit https://www.aestimosolver.org/ to read many tutorials which includes many important examples. Same tutorials are included in your /doc folder.

To file an issue about the code please use GitHub's Issue management page for Aestimo EDU: https://github.com/aestimosolver/aestimo-edu/issues .

## Download and Installation
-------------------------

The latest version of the program is available in zipped form from the website: https://github.com/aestimosolver/aestimo-edu/archive/main.zip

## Prerequisites

You will need to have a recent version of Python3 installed on your computer. For this, please refer to Python Website, where binary packages for most platforms can be found. Additionally, you need some libraries. If you install matplotlib library, all other necessary libraries will be installed. You can use pip for intallation of matplotlib.

```
pip install matplotlib
```

## Running the Code

The code is written in Python, and thus is platform independent. After extracting the aestimo-edu_x.y.zip file to a folder, user may point the files that are written below in the related folder. Here x.y is the version number.

  main.py - The file that you need to run.
  config.py - A simple configuration file. You must enter the input filename into this configuration file.
  database.py - A database for materials properties.
  aestimo-edu.py - Main program for conduction band calculations and gamma valley electrons. Its code is simple to understand.
  sample-X.py - Some samples files (X) are included in the package with prefix "sample-".
  main_iterating.py - A script for simulating a design several times while varying a parameter over a range of values.
  README.md - A readme file as you noticed.
  README_OUTPUTS - A readme about the structure of output files.
  LICENSE - License of the software.
  AUTHORS.md - List of the committers.
  /outputs - Output folder (If it is not available, it will be created in the first usage automatically.

First of all, user must prepare or use an input file. This file must specified in config.py file. There are other options in config.py file like necessary output files and on/off options for result viewer and in-run messages. After specifiying an input file in config.py, user can run the aestimo easily with executing the command

  ./aestimo-edu.py

For simulating a design several times while varying a parameter over a range of values, edit the 'main_iterating.py' file for your needs, and then execute it as

  ./main_iterating.py


If the output file options are true in config.py file, results can be found in the outputs folder. For Output files, please read README_OUTPUTS.md file.
