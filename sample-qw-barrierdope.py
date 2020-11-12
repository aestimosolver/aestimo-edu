#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Input File Description:  Barrier doped AlGaAs/GaAs heterostructure.
# -------------------------------------------------------------------
# ----------------
# GENERAL SETTINGS
# ----------------

# TEMPERATURE
T = 60.0 #Kelvin

# COMPUTATIONAL SCHEME
# 0: Schrodinger
# 2: Schrodinger-Poisson
computation_scheme = 2

# QUANTUM
# Total subband number to be calculated for electrons
subnumber_e = 3
# Total subband number to be calculated for electrons (for aestimo_numpy_h)
subnumber_h = 1

# APPLIED ELECTRIC FIELD
Fapplied = 0.00/50e-9 # (V/m)

# --------------------------------
# REGIONAL SETTINGS FOR SIMULATION
# --------------------------------

# GRID
# For 1D, z-axis is choosen
gridfactor = 0.1 #nm
maxgridpoints = 200000 #for controlling the size

# REGIONS
# Region input is a two-dimensional list input.
# An example:
# Si p-n diode. Firstly lets picturize the regional input.
#         | Thickness (nm) | Material | Alloy fraction | Doping(cm^-3) | n or p type |
# Layer 0 |      250.0     |   Si     |      0         |     1e16      |     n       |
# Layer 1 |      250.0     |   Si     |      0         |     1e16      |     p       |
#
# To input this list in Gallium, we use lists as:
material =[[ 10.0, 'AlGaAs', 0.3, 0.0, 'n'],
            [ 5.0, 'AlGaAs', 0.3, 5e17, 'n'],
            [ 5.0, 'AlGaAs', 0.3, 0.0, 'n'],
            [ 11.0, 'GaAs', 0, 0, 'n'],
            [ 5.0, 'AlGaAs', 0.3, 0.0, 'n'],
            [ 5.0, 'AlGaAs', 0.3, 5e17, 'n'],
            [ 10.0, 'AlGaAs', 0.3, 0.0, 'n']]
 

