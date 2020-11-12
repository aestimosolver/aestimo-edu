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

 Description:  It is a simple config file, however there will
                be multi-input file execution feature in the future.
  
"""
q = 1.602176e-19 #C
meV2J=1e-3*q #meV to Joules

# CONFIGURATION 

# Input File(s)
# -------------
#inputfilename = "sample-qw-barrierdope"
#inputfilename = "sample-qw-qwdope"
#inputfilename = "sample-moddop"
inputfilename = "sample-double-qw"

# Calculation
# -----------
# Aestimo
use_cython = True #provides a speed up for aestimo
# Shooting method parameters for Schrödinger Equation solution
delta_E = 0.5*meV2J #Energy step (Joules) for initial search. Initial delta_E is 1 meV. 
d_E = 1e-5*meV2J #Energy step (Joules) within Newton-Raphson method when improving the precision of the energy of a found level.
E_start = 0.0    #Energy to start shooting method from (if E_start = 0.0 uses minimum of energy of bandstructure)
Estate_convergence_test = 1e-9*meV2J
# FermiDirac
FD_d_E = 1e-9 #Initial and minimum Energy step (meV) for derivative calculation for Newton-Raphson method to find E_F
FD_convergence_test = 1e-6 #meV
np_d_E = 1.0 # Energy step (meV) for dispersion calculations
# Poisson Loop
damping = 0.5    #averaging factor between iterations to smooth convergence.
max_iterations=80 #maximum number of iterations.
convergence_test=1e-6 #convergence is reached when the ground state energy (meV) is stable to within this number between iterations.


# Output Files
# ------------
output_directory = "outputs"
parameters = True
electricfield_out = True
potential_out = True
sigma_out = True
probability_out = True
states_out = True

# Result Viewer
# -------------
resultviewer = True
wavefunction_scalefactor = 200 # scales wavefunctions when plotting QW diagrams
# Messages
# --------
messagesoff = False
logfile = 'aestimo.log'