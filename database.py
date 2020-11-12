#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Aestimo EDU 1D Schrodinger-Poisson Solver
 Copyright (C) 2013-2020  Aestimo group

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

 Description:  Database file. Using lists for database entries.
                Absolutely, it is not using a parser subroutine.
                Quick and dirty solution for the code.
 References:
  - GaAs,AlAs parameters:
    Properties of Semiconductor Alloys: Group-IV, III-V and II-VI Semiconductors Sadao AdAchi?2009 John Wiley & Sons, Ltd.
    Basic Semiconductor Physics Second Edition,Prof. Chihiro Hamaguchi 2010 Springer
    Physics of Optoelectronic Devices ,S-L.CHUANG ,1995 by John Wiley & Sons. Inc
  
"""

# MATERIAL PROPERTIES
# materialproperties| Material : m_e | m_hh | epsilonStatic | Eg | Bowing_param | m_e_alpha |  Luttinger Parameters γ1,2 & 3 |Elastic constants C11,12|Lattice constant a0| Deformation potentials ac,av & b| delta splitt off|
materialproperty = {
'GaAs':{
'm_e':0.067, #conduction band effective mass (relative to electron mass)
'epsilonStatic':12.90, #dielectric constant
'Eg':1.519,#1.42 # (ev) band gap
'Band_offset':0.65, # conduction band/valence band offset ratio for GaAs - AlGaAs heterojunctions
},
'AlAs':{
'm_e':0.15,
'epsilonStatic':10.06,
'Eg':3.099,#2.980,
'Band_offset':0.53,
},
'InAs':{
'm_e':0.4,
'epsilonStatic':15.15,
'Eg':0.4,
'Band_offset':0.63,
},
'InP':{
'm_e':0.073,
'epsilonStatic':12.50,
'Eg':1.35,
'Band_offset':0.38,
},
'GaP':{
'm_e':0.82,
'epsilonStatic':11.1,
'Eg':2.261,
'Band_offset':0.55,
},
'AlP':{
'm_e':0.22,
'epsilonStatic':10.464,
'Eg':2.48,
'Band_offset':0.55,
}
}

# ALLOY PROPERTIES
# alloyproperties| Alloy : m_e_x=0 | m_e_b  | eps_x=0 | eps_b | Eg | Bowing_param | m_e_alpha
alloyproperty = {
'AlGaAs':{
'Bowing_param':0.37,
'Band_offset':0.65,
'Material1':'AlAs',
'Material2':'GaAs'
},
'InGaAs':{
'Bowing_param':0.58,
'Band_offset':0.63,
'Material1':'InAs',
'Material2':'GaAs'
},
'InGaP':{
'Bowing_param':0.65,
'Band_offset':0.33,
'Material1':'InP',
'Material2':'GaP'
},
'AlInP':{
'Bowing_param':0.13,
'Band_offset':0.52,
'Material1':'AlP',
'Material2':'InP'
}
}



