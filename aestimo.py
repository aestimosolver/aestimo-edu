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

 Description: This is the aestimo calculator conduction band calculations (Classic version). 
"""
#from scipy.optimize import fsolve
import time
time0 = time.time() # timing audit
import matplotlib.pyplot as pl
import numpy as np
alen = np.alen
import os
import config,database
from math import *
# --------------------------------------
import logging
logger = logging.getLogger('aestimo')
hdlr = logging.FileHandler(config.logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
# LOG level can be INFO, WARNING, ERROR
logger.setLevel(logging.INFO)
# --------------------------------------

#Defining constants and material parameters
q = 1.602176e-19 #C
kb = 1.3806504e-23 #J/K
nii = 0.0
hbar = 1.054588757e-34
m_e= 9.1093826E-31 #kg
pi=np.pi
eps0= 8.8541878176e-12 #F/m

J2meV=1e3/q #Joules to meV
meV2J=1e-3*q #meV to Joules

time1 = time.time() # timing audit
print "Aestimo is starting..."
logger.info("Aestimo is starting...")

# Import from config file
inputfile = __import__(config.inputfilename)
logger.info("inputfile is %s" %config.inputfilename)

## Reading inputs and using local variables

# Loading material list
material = inputfile.material
totallayer = alen(material)

print "Total layer number: ",totallayer
logger.info("Total layer number: %s" %totallayer)

comp_scheme = inputfile.computation_scheme
if comp_scheme in (1,3):
    print "aestimo doesn't yet include non-parabolicity calculations - try aestimo_numpy instead"
    logger.error("aestimo doesn't yet include non-parabolicity calculations - try aestimo_numpy instead")
    exit()
if comp_scheme in (4,5,6):
    print "aestimo doesn't yet include the exchange interaction calculations - try aestimo_numpy instead"
    logger.error("aestimo doesn't yet include the exchange interaction calculations - try aestimo_numpy instead")
    exit()
    
max_val = inputfile.maxgridpoints
Fapp = inputfile.Fapplied
T = inputfile.T
subnumber_e = inputfile.subnumber_e
dx = inputfile.gridfactor*1e-9 #grid in m
x_max = sum([layer[0] for layer in material])*1e-9 #total thickness (m)

def round2int(x):
    """int is sensitive to floating point numerical errors near whole numbers,
    this moves the discontinuity to the half interval. It is also equivalent
    to the normal rules for rounding positive numbers."""
    # int(x + (x>0) -0.5) # round2int for positive and negative numbers
    return int(x+0.5)

# Calculate the required number of grid points and renormalize dx
n_max = round2int(x_max/dx)
if n_max > max_val:
    print "Grid number is exceeding the max number of ", max_val
    logger.error("Grid number is exceeding the max number of %d" %max_val)
    exit()

# Shooting method parameters for Schrödinger Equation solution
delta_E = config.delta_E #0.5*meV2J #Energy step (Joules) for initial search. Initial delta_E is 1 meV.
d_E = config.d_E #1e-5*meV2J #Energy step (Joules) for Newton-Raphson method when improving the precision of the energy of a found level.
E_start = config.E_start #0.0 #Energy to start shooting method from (if E_start = 0.0 uses minimum of energy of bandstructure)
Estate_convergence_test = config.Estate_convergence_test #1e-9*meV2J
# FermiDirac
FD_d_E = config.FD_d_E #1e-9 Initial and minimum Energy step (meV) for derivative calculation for Newton-Raphson method to find E_F
FD_convergence_test = config.FD_convergence_test #1e-6
# Poisson Loop
damping = config.damping #0.5 #averaging factor between iterations to smooth convergence.
max_iterations= config.max_iterations #80 #maximum number of iterations.
convergence_test= config.convergence_test #1e-6 #convergence is reached when the ground state energy (meV) is stable to within this number between iterations.

# Loading materials database
material_property = database.materialproperty
totalmaterial = alen(material_property)

alloy_property = database.alloyproperty
totalalloy = alen(alloy_property)

print "Total number of materials in database: ",totalmaterial+totalalloy
logger.info("Total number of materials in database: %d" %(totalmaterial+totalalloy))

# --------------------------------------

#Vegard's law for alloys
def vegard(first,second,mole):
    return first*mole+second*(1-mole)

# This function returns the value of the wavefunction (psi)
# at +infinity for a given value of the energy.  The solution
# to the energy occurs for psi(+infinity)=0.

# FUNCTIONS for SHOOTING ------------------
if config.use_cython:
    #uses a cython accelerate version of the shooting method function below.
    from psi_at_inf_cython import psi_at_inf

else:
    
    def psi_at_inf(E,fis,cb_meff,n_max,dx):
        """Shooting method for heterostructure as given in Harrison's book"""
        c0 = 2*(dx/hbar)**2
        # boundary conditions
        psi0 = 0.0                 
        psi1 = 1.0
        psi2 = None
        for j in xrange(1,n_max-1,1): # Last potential not used
            c1=2.0/(cb_meff[j]+cb_meff[j-1])
            c2=2.0/(cb_meff[j]+cb_meff[j+1])
            psi2=((c0*(fis[j]-E)+c2+c1)*psi1-c1*psi0)/c2
            psi0=psi1
            psi1=psi2
        return psi2
    


#nb. function was much slower when fi is a numpy array than a python list.
def calc_E_state(numlevels,fi,cb_meff,energyx0): # delta_E,d_E
    """Finds the Eigen-energies of any bound states of the chosen potential.
    numlevels - number of levels to find
    fi - Potential energy (Joules)
    model - any object with attributes: 
        cb_meff - array of effective mass (len n_max)
        n_max - length of arrays
        dx - step size (metres)
    energyx0 - minimum energy for starting subband search (Joules)"""
    energyx=energyx0 #starting energy for subband search (Joules)
    E_state=[0.0]*numlevels #Energies of subbands (meV)
    #fi - Potential energy (J)
    #cb_meff - effective mass of electrons in conduction band (kg)
    #print 'energyx', energyx,type(energyx)
    #print 'cb_meff', cb_meff[0:10], type(cb_meff), type(cb_meff[0])
    #print 'n_max', n_max, type(n_max)
    #print 'fi', fi[0:10], type(fi), type(fi[0])
    #print 'dx', dx, type(dx)
    #exit()
    for i in range(0,numlevels,1):  
        #increment energy-search for f(x)=0
        y2=psi_at_inf(energyx,fi,cb_meff,n_max,dx)
        while True:
            y1=y2
            energyx += delta_E
            y2=psi_at_inf(energyx,fi,cb_meff,n_max,dx)
            if y1*y2 < 0:
                break
        # improve estimate using midpoint rule
        energyx -= abs(y2)/(abs(y1)+abs(y2))*delta_E
        #implement Newton-Raphson method
        while True:
            y = psi_at_inf(energyx,fi,cb_meff,n_max,dx)
            dy = (psi_at_inf(energyx+d_E,fi,cb_meff,n_max,dx)- psi_at_inf(energyx-d_E,fi,cb_meff,n_max,dx))/(2.0*d_E)
            energyx -= y/dy
            if abs(y/dy) < Estate_convergence_test:
                break
        E_state[i]=energyx*J2meV
        # clears x from solution
        energyx += delta_E # finish for i-th state.
    return E_state

# FUNCTIONS for ENVELOPE FUNCTION WAVEFUNCTION--------------------------------
def wf(E,fis,cb_meff):
    """This function returns the value of the wavefunction (psi)
    at +infinity for a given value of the energy.  The solution
    to the energy occurs for psi(+infinity)=0.
    psi[3] wavefunction at z-delta_z, z and z+delta_z 
    i index
    
    E - eigen-energy of state (Joules)
    fis - Potential energy of system (Joules)
    model - an object with atributes:
        cb_meff - array of effective mass (len n_max)
        n_max - length of arrays
        dx - step size (metres)"""
    N = 0.0 # Normalization integral
    psi = []
    psi = [0.0]*3
    # boundary conditions
    psi[0] = 0.0                 
    psi[1] = 1.0
    b = [0.0]*n_max
    b[0] = psi[0]
    b[1] = psi[1]
    N += (psi[0])**2
    N += (psi[1])**2
    for j in range(1,n_max-1,1):
        # Last potential not used
        c1=2.0/(cb_meff[j]+cb_meff[j-1])
        c2=2.0/(cb_meff[j]+cb_meff[j+1])
        psi[2] = ((2*(dx/hbar)**2*(fis[j]-E)+c2+c1)*psi[1]-c1*psi[0])/c2
        b[j+1]=psi[2]
        N += (psi[2])**2
        psi[0]=psi[1]
        psi[1]=psi[2]
    for j in range(0,n_max,1):
        b[j]/=(N)**0.5
    return b # units of dx**0.5
    
# FUNCTIONS for FERMI-DIRAC STATISTICS-----------------------------------------   
def fd2(Ei,Ef,T):
    #integral of Fermi Dirac Equation for energy independent density of states.
    #Ei [meV], Ef [meV], T [K]"""
    return kb*T*log(exp(meV2J*(Ef-Ei)/(kb*T))+1)

def calc_meff_state(wfe,cb_meff):
    #find subband effective mass
    meff_state = [0.0]*alen(wfe)
    for j in range(0,subnumber_e,1):
        total=0.0
        for b,meff in zip(wfe[j],cb_meff):
            total+=float(b)**2/meff
        meff_state[j] = 1.0/total
    return meff_state #kg
    
def fermilevel_0K(Ntotal2d,E_state,meff_state):
    Et,Ef=0.0,0.0
    for i,(Ei,csb_meff) in enumerate(zip(E_state,meff_state)):
        Et+=Ei
        Efnew=(-Ntotal2d*hbar**2*pi/csb_meff*J2meV + Et)/(i+1)
        if Efnew>Ei:
            Ef=Efnew
        else:
            break #we have found Ef and so we should break out of the loop
    else: #exception clause for 'for' loop.
        print "Have processed all energy levels present and so can't be sure that Ef is below next higher energy level."
        logger.warning("Have processed all energy levels present and so can't be sure that Ef is below next higher energy level.")
    N_state=[0.0]*len(E_state)
    for i,(Ei,csb_meff) in enumerate(zip(E_state,meff_state)):
        Ni=(Ef - Ei)*csb_meff/(hbar**2*pi)*meV2J    # populations of levels
        Ni*=(Ni>0.0)
        N_state[i]=Ni
    return Ef,N_state #Fermi levels at 0K (meV), number of electrons in each subband at 0K
    
def fermilevel(Ntotal2d,T,E_state,meff_state):
    #find the Fermi level (meV)
    def func(Ef,E_state,meff_state,Ntotal2d,T):
        #return Ntotal2d - sum( [csb_meff*fd2(Ei,Ef,T) for Ei,csb_meff in zip(E_state,meff_state)] )/(hbar**2*pi)
        diff = -Ntotal2d
        for Ei,csb_meff in zip(E_state,meff_state):
            diff -= csb_meff*fd2(Ei,Ef,T)/(hbar**2*pi)
        return diff
    Ef_0K,N_states_0K = fermilevel_0K(Ntotal2d,E_state,meff_state)
    #Ef=fsolve(func,Ef_0K,args=(E_state,meff_state,Ntotal2d,T))[0]
    #return float(Ef)
    #implement Newton-Raphson method
    Ef = Ef_0K
    d_E = FD_d_E #Energy step (meV)
    while True:
        y = func(Ef,E_state,meff_state,Ntotal2d,T)
        dy = (func(Ef+d_E,E_state,meff_state,Ntotal2d,T)- func(Ef-d_E,E_state,meff_state,Ntotal2d,T))/(2.0*d_E)
        if dy == 0.0: #increases interval size for derivative calculation in case of numerical error
            d_E*=2.0
            continue #goes back to start of loop, therefore d_E will increase until a non-zero derivative is found
        Ef -= y/dy
        if abs(y/dy) < FD_convergence_test:
            break
        #reduces the interval by a couple of notches ready for the next iteration
        for i in range(2):
            if d_E>FD_d_E: 
                d_E*=0.5
    return Ef #(meV)


def calc_N_state(Ef,T,Ns,E_state,meff_state):
    # Find the subband populations, taking advantage of step like d.o.s. and analytic integral of FD
    N_state=[fd2(Ei,Ef,T)*csb_meff/(hbar**2*pi) for Ei,csb_meff in zip(E_state,meff_state)]
    return N_state # number of carriers in each subband
    
# FUNCTIONS for SELF-CONSISTENT POISSON--------------------------------
def dop0():
    position = 0.0 # metres
    for layer in material:
        startindex = round2int(position/dx)
        position += layer[0]*1e-9 # update position to end of the layer
        finishindex = round2int(position/dx)
        if layer[4] == 'n':  
            chargedensity = -layer[3]*1e6 #charge density in m**-3 (conversion from cm**-3)
        elif layer[4] == 'p': 
            chargedensity = layer[3]*1e6 #charge density in m**-3 (conversion from cm**-3)
        for j in range(startindex,finishindex):
            dop[j] = chargedensity
    return dop


def calc_sigma(wfe,N_state,dop):
    # This function calculates `net' areal charge density
    # i index over z co-ordinates
    # is index over states
    sigma = [0.0]*n_max
    for i in range(0,n_max,1):
        for j in range(0,subnumber_e,1):
            sigma[i] = sigma[i] - N_state[j]*(float(wfe[j][i])**2)
            # n-type dopants give -ve *(N+j) representing electrons, hence 
            # addition of +ve ionised donors requires -*(Nda+i), note Nda is still a
            # volume density, the delta_z converts it to an areal density
        sigma[i] = sigma[i] - dop[i]*dx # This may be one tab indented.

    return sigma
    
##
def calc_field(sigma,eps):
    # F electric field as a function of z-
    # i index over z co-ordinates
    # j index over z' co-ordinates

    # For wave function initialise F
    #for i in range(0,n_max,1): #It isn't really necessary to zero everything when using the running integral form.
    #    F[i] = 0.0
    F = [0.0]*n_max
    # Do zeroth case explicitly - in fact, normally we can assume that the total electric field is zero (?)
    for j in range(1,n_max,1):
        # Note sigma is a number density per unit area, needs to be converted to Couloumb per unit area
        F[0] -= q*sigma[j]/(2.0*eps[0]) #CMP'deki i ve j yer değişebilir - de + olabilir
    # Do running integral
    for i in range(1,n_max,1):
        # Note sigma is a number density per unit area, needs to be converted to Couloumb per unit area
        F[i] = F[i-1]*(eps[i-1]/eps[i]) + q*(sigma[i-1]+sigma[i])/(2.0*eps[i]) #CMP'deki i ve j yer değişebilir - de + olabilir
    return F

def calc_field_old(sigma,eps):
    # F electric field as a function of z-
    # i index over z co-ordinates
    # j index over z' co-ordinates

    # For wave function initialise F
    F[i] = [0.0]*n_max
    for i in range(0,n_max,1):
        for j in range(0,n_max,1):
            # Note sigma is a number density per unit area, needs to be converted to Couloumb per unit area
            F[i] = F[i] + q*sigma[j]*cmp(i,j)/(2*eps[i]) #CMP'deki i ve j yer değişebilir - de + olabilir
    return F

def calc_potn(F):
    # This function calculates the potential (energy actually)
    # V electric field as a function of z-
    # i	index over z co-ordinates
    
    #Calculate the potential, defining the first point as zero
    V = [0.0] * n_max
    for i in range(1,n_max,1):
        V[i]=V[i-1]+q*F[i]*dx #+q -> electron -q->hole? 
    return V


# --- FUNCTION TO SET UP CALCULATION (INITIALISING STRUCTURE ARRAYS (LISTS)

def fill_structure_lists():
    # initialise arrays/lists for structure
    position = 0.0 # metres
    for layer in material:
        startindex = round2int(position/dx)
        position += layer[0]*1e-9 # update position to end of the layer
        finishindex = round2int(position/dx)
        #
        matType = layer[1]
        
        if matType in material_property:
            matprops = material_property[matType]
            for i in range(startindex,finishindex):
                cb_meff[i] = matprops['m_e']*m_e
                fi[i] = matprops['Band_offset']*matprops['Eg']*q #Joule
                eps[i] = matprops['epsilonStatic']*eps0
            
        elif matType in alloy_property:
            alloyprops = alloy_property[matType]
            for i in range(startindex,finishindex):
                x = layer[2] #alloy ratio
                cb_meff[i] = (x*material_property[alloyprops['Material1']]['m_e'] + (1-x)* material_property[alloyprops['Material2']]['m_e'])*m_e
                fi[i] = alloyprops['Band_offset']*(x*material_property[alloyprops['Material1']]['Eg'] + (1-x)* material_property[alloyprops['Material2']]['Eg']-alloyprops['Bowing_param']*x*(1-x))*q # for electron. Joule
                eps[i] = (x*material_property[alloyprops['Material1']]['epsilonStatic'] + (1-x)* material_property[alloyprops['Material2']]['epsilonStatic'] )*eps0
 
# ----------------------------------------------------

# Preparing empty subband energy lists.
E_state = [0.0]*subnumber_e     # Energies of subbands/levels (meV)
N_state = [0.0]*subnumber_e     # Number of carriers in subbands  

# Creating and Filling material arrays
cb_meff = [0.0]*n_max	#conduction band effective mass
fi = [0.0]*n_max	#Bandstructure potential
fitot = [0.0]*n_max	#Energy potential = Bandstructure + Coulombic potential
eps =[0.0]*n_max	#dielectric constant
dop = [0.0]*n_max	#doping distribution
sigma = [0.0]*n_max	#charge distribution (donors + free charges)
F = [0.0]*n_max		#Electric Field
V = [0.0]*n_max		#Electric Potential
Vapp = [0.0]*n_max	#Electric Potential

# Subband wavefunction for electron list. 2-dimensional: [i][j] i:stateno, j:wavefunc
wfe = np.zeros((subnumber_e,n_max),dtype = float)

# Initialise arrays/lists
fill_structure_lists()

# Setup the doping
dop = dop0()
Ntotal = sum(dop) # calculating total doping density m-3
Ntotal2d = Ntotal*dx
#print "Ntotal ",Ntotal,"m**-3"
print "Ntotal2d ",Ntotal2d," m**-2"
logger.info("Ntotal2d %g m**-2" %Ntotal2d)
    
# Applied Field
x0=dx*n_max/2.0 # Finding the middle point (z0) of z-axis for Fapp
for i in range(0,n_max,1):
    Vapp[i] = q*Fapp*(i*dx-x0)

#delta_acc = 1e-6

# STARTING SELF CONSISTENT LOOP
time2 = time.time() # timing audit
iteration = 1   #iteration counter
previousE0= 0   #(meV) energy of zeroth state for previous iteration(for testing convergence)
#fitot = list(fi) #For initial iteration just copy fi. list(seq) returns a copy of the original rather than just an alias.
for i in range(0,n_max,1):
    fitot[i] = fi[i] + Vapp[i]  # Adding field qF(z-z0)

fi_min= min(fitot) #minimum potential energy of structure (for limiting the energy range when searching for states)
if abs(E_start)>1e-3*meV2J: #energyx is the minimum energy (meV) when starting the search for bound states.
    energyx = E_start
else:
    energyx = fi_min

while True:
    if not(config.messagesoff) :
        print "Iteration:",iteration
        logger.info("Iteration: %d" %iteration)
    if iteration> 1:
        energyx = fi_min
        for i in range(0, n_max, 1):
            # Find fi-minimum --may got error.
            if fitot[i] < energyx:
                energyx = fitot[i]
    
    E_state=calc_E_state(subnumber_e,fitot,cb_meff,energyx)
    
    # Envelope Function Wave Functions
    for j in range(0,subnumber_e,1):
        if not(config.messagesoff) :
            print "Working for subband no:",j+1
            logger.info("Working for subband no: %d"%(j+1))
        wfe[j] = wf(E_state[j]*meV2J,fitot,cb_meff) #wavefunction units dx**0.5
    
    # Calculate the effective mass of each subband
    meff_state = calc_meff_state(wfe,cb_meff)
    
    ## Self-consistent Poisson
    
    # Calculate the Fermi energy and subband populations at 0K
    #E_F_0K,N_state_0K=fermilevel_0K(Ntotal2d,E_state,meff_state)
    # Calculate the Fermi energy at the temperature T (K)
    E_F = fermilevel(Ntotal2d,T,E_state,meff_state)
    # Calculate the subband populations at the temperature T (K)
    N_state=calc_N_state(E_F,T,Ntotal2d,E_state,meff_state)
    # Calculate `net' areal charge density
    sigma=calc_sigma(wfe,N_state,dop) #one more instead of subnumber_e
    # Calculate electric field
    F=calc_field(sigma,eps)
    # Calculate potential due to charge distribution
    Vnew=calc_potn(F)
    #       
    #status
    if not(config.messagesoff):
        for i,level in enumerate(E_state):
            print "E[",i,"]=",level,"meV" #can be written on file.
            logger.info("E[%d]= %f meV"%(i,level))
        for i,meff in enumerate(meff_state):
            print 'meff[',i,']= ',meff/m_e
            logger.info("meff[%d]= %f"%(i,meff/m_e))
        for i,Ni in enumerate(N_state):
            print 'N[',i,']= ',Ni,' m**-2'
            logger.info("N[%d]= %f m**-2"%(i,Ni))            
        #print 'Efermi (at 0K) = ',E_F_0K,' meV'
        #for i,Ni in enumerate(N_state_0K):
        #    print 'N[',i,']= ',Ni
        print 'Efermi (at %gK) = ' %T, E_F,' meV'
        print "total donor charge = ",sum(dop)*dx,"m**-2"
        print "total level charge = ",sum(N_state),"m**-2"
        print "total system charge = ",sum(sigma),"m**-2"
        logger.info('Efermi (at %gK) = %g meV' %(T, E_F))
        logger.info("total donor charge = %g m**-2" %(sum(dop)*dx))
        logger.info("total level charge = %g m**-2" %(sum(N_state)))
        logger.info("total system charge = %g m**-2" %(sum(sigma)))
    #
    if comp_scheme in (0,1): 
        #if we are not self-consistently including Poisson Effects then only do one loop
        break 
        
    # Combine band edge potential with potential due to charge distribution
    # To increase convergence, we calculate a moving average of electric potential 
    #with previous iterations. By dampening the corrective term, we avoid oscillations.
    for i in range(0,n_max,1):
        V[i] = V[i] + damping*(Vnew[i] - V[i])
        fitot[i] = fi[i] + V[i] + Vapp[i]
        
    if abs(E_state[0]-previousE0) < convergence_test: #Convergence test
        break
    elif iteration > max_iterations: #Iteration limit
        print "Have reached maximum number of iterations"
        logger.warning("Have reached maximum number of iterations")
        break
    else:
        iteration += 1
        previousE0 = E_state[0]
        
# END OF SELF-CONSISTENT LOOP
time3 = time.time() # timing audit

logger.info("total running time (inc. loading libraries) %g s" %(time3 - time0))
logger.info("total running time (exc. loading libraries) %g s" %(time3 - time1))
logger.info("calculation time  %g s" %(time3 - time2))

# Write the simulation results in files

xaxis = np.arange(0,n_max)*dx   #metres

if not os.path.isdir(config.output_directory):
    os.makedirs(config.output_directory)

def saveoutput(fname,datatuple,header=None):
    fname2 = os.path.join(config.output_directory,fname)
    fobj = file(fname2,'wb')
    if header: fobj.write(header+'\n')
    np.savetxt(fobj,np.column_stack(datatuple),fmt='%.6e', delimiter=' ')
    fobj.close()

def saveoutput2(fname2,datatuple,header=None,fmt='%.6g',delimiter=', '):
    fname2 = os.path.join(config.output_directory,fname2)
    fobj = file(fname2,'wb')
    if header: fobj.write(header+'\n')
    np.savetxt(fobj,np.column_stack(datatuple),fmt=fmt, delimiter=delimiter)
    fobj.close()

if config.parameters:
    saveoutput2("parameters.dat",header=('T (K), Fapp (V/m), E_F (meV)'),
                datatuple=(T,Fapp,E_F))
if config.sigma_out:
    saveoutput("sigma.dat",(xaxis,sigma))
if config.electricfield_out:
    saveoutput("efield.dat",(xaxis,F))
if config.potential_out:
    saveoutput("potn.dat",(xaxis,fitot))
if config.states_out:
    rel_meff_state = [meff/m_e for meff in meff_state] #going to report relative effective mass.
    header = "State No.    Energy (meV) N (m**-2)    Subband m* (kg)"
    saveoutput("states.dat",(range(subnumber_e),E_state,N_state,rel_meff_state), header)
if config.probability_out:
    saveoutput("wavefunctions.dat",(xaxis,wfe.transpose()) )

# Resultviewer
    
if config.resultviewer:
    pl.figure(figsize=(10,8))
    pl.suptitle('Aestimo Results')
    pl.subplots_adjust(hspace=0.4,wspace=0.4)
                          
    #Plotting Sigma
    #figure(0)
    pl.subplot(2,2,1)
    pl.plot(xaxis, sigma)
    pl.xlabel('Position (m)')
    pl.ylabel('Sigma (e/m^2)')
    pl.title('Sigma')
    pl.grid(True)

    #Plotting Efield
    #figure(1)
    pl.subplot(2,2,2)
    pl.plot(xaxis, F)
    pl.xlabel('Position (m)')
    pl.ylabel('Electric Field strength (V/m)')
    pl.title('Electric Field')
    pl.grid(True)

    #Plotting Potential
    #figure(2)
    pl.subplot(2,2,3)
    pl.plot(xaxis, fitot)
    pl.xlabel('Position (m)')
    pl.ylabel('E_c (J)')
    pl.title('Potential')
    pl.grid(True)

    #Plotting State(s)
    #figure(3)
    pl.subplot(2,2,4)
    for j,state in enumerate(wfe):
        pl.plot(xaxis, state, label='state %d' %j)
    pl.xlabel('Position (m)')
    pl.ylabel('Psi')
    pl.title('First state')
    pl.grid(True)
    
    #QW representation
    #figure(5)
    pl.figure(figsize=(10,8))
    pl.suptitle('Aestimo Results')
    pl.subplot(1,1,1)
    pl.plot(xaxis,np.array(fitot)*J2meV,'k')
    for level,state in zip(E_state,wfe): 
        pl.axhline(level,0.1,0.9,color='g',ls='--')
        pl.plot(xaxis, np.array(state)*config.wavefunction_scalefactor+level,'b')
        #pl.plot(xaxis, np.array(state)**2*1e-9/dx*200.0+level,'b')
    pl.axhline(E_F,0.1,0.9,color='r',ls='--')
    pl.xlabel('Position (m)')
    pl.ylabel('Energy (meV)')
    pl.grid(True)
    pl.show()
    
print "Simulation is finished. All files are closed."
print "Please control the related files."
logger.info("""Simulation is finished. All files are closed.Please control the related files.
-----------------------------------------------------------------""")

#example load function. This should be placed in a separate file if you wish to
#use it since importing a function from this module will cause the simulation to
#run.
def load_results():
    """Loads the data stored in the output folder"""
    class Results(): pass
    results = Results()
    
    output_directory = config.output_directory
            
    def loadoutput(fname,header=False,unpack=True):
        fname2 = os.path.join(output_directory,fname)
        fobj = file(fname2,'rb')
        if header: header = fobj.readline()
        else: header = ''
        data = np.loadtxt(fobj,delimiter=' ',unpack=unpack)
        fobj.close()
        return data,header
    
    if config.parameters:
        results.T,results.Fapp,results.E_F = np.loadtxt(
                      open(os.path.join(output_directory,"parameters.dat"),'rb'),
                      unpack=True,delimiter=',',skiprows=1)
    if config.sigma_out:
        (results.xaxis,results.sigma),hdr = loadoutput("sigma.dat")
    if config.electricfield_out:
        (results.xaxis,results.F),hdr = loadoutput("efield.dat")
    if config.potential_out:
        (results.xaxis,results.fitot),hdr = loadoutput("potn.dat")
    if config.states_out:
        (states,results.E_state,results.N_state,rel_meff_state),hdr = loadoutput("states.dat", header=True)
        results.subnumber_e = max(states)
        results.meff_state = rel_meff_state*m_e
    if config.probability_out:
        _wfe,hdr = loadoutput("wavefunctions.dat",unpack=False)
        results.xaxis = _wfe[:,0]
        results.wfe = _wfe[:,1:].transpose()
    
    #missing variables
    #results.V
    results.dx = np.mean(results.xaxis[1:]-results.xaxis[:-1])
    #results.level_dispersions = level_dispersions
    
    return results