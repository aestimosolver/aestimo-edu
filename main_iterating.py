#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Aestimo 1D Schrodinger-Poisson Solver
 Copyright (C) 2013-2014 Sefer Bora Lisesivdin and Aestimo group

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. See ~/COPYING file or http://www.gnu.org/copyleft/gpl.txt .

    For the list of contributors, see ~/AUTHORS

 Description:  This is an example script for simulating a design several 
               times while varying a parameter over a range of values.
"""
import matplotlib.pyplot as pl
import numpy as np
import os

# aestimo modules
import config
inputfile = __import__(config.inputfilename) 
import database

### Example: Parameter to loop over.
#thickness of first layer of structure
thicknesses = [8,12,14,16,20] #nm

# first value
inputfile.material[1][0] = thicknesses[0]
output_directory = config.output_directory # will be our local copy of the original value
config.output_directory = os.path.join(output_directory,'dz0_%dnm' %thicknesses[0])

import aestimo # this will run aestimo for the initial time (necessary to do 
# we want to use the python module reload function)

#the desired results can be stored for further analysis. 
#e.g.
results=[aestimo.E_state]

# Looping over the parameter
"""we vary the (runtime values of the) variables within inputfile module's 
namespace and then use the reload function on the aestimo module in order 
to run the simulation afresh for each value. Equally, we could vary the 
values in the database module if we wanted to."""
for thickness in thicknesses[1:]:
    inputfile.material[1][0] = thickness
    #other examples -
    #inputfile.Fapplied = ... 
    #inputfile.subnumber_e = ...
    #inputfile.gridfactor = ...
    #database.materialproperty['GaAs']['epsilonStatic']= ...
    
    # Set output directory 
    # aestimo_numpy reads the output directory from the config module, so
    config.output_directory = os.path.join(output_directory,'dz0_%dnm' %thickness)
        
    reload(aestimo) # by reloading the module, we rerun the calculation for the new input parameters
    
    #e.g.
    results.append(aestimo.E_state) #the desired results can be stored for further analysis. 
    
print results
    
print "Simulation is finished. All files are closed."
print "Please control the related files."
