# -*- coding: utf-8 -*-
#%reset -f
"""
Copyright Swiss Federal Office for the Environment FOEN, 2021 - 2023.

This file is part of: inventory_uncertainty_UNFCCC_CLRTAP.

inventory_uncertainty_UNFCCC_CLRTAP is a free software: 
you can redistribute it and/or modify
it under the terms of the BSD 3-Clause "New" or "Revised" License.

inventory_uncertainty_UNFCCC_CLRTAP is distributed 
in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the BSD 3-Clause "New" or "Revised" License for more details.

Created on Thu Dec 15 11:06:36 2022

Stript containing the input variables to run uncertainty estimations
using Monte Carlo simulations
for all input categories to be summed up to get the inventory total
for the NID, according to the CRT nomenclature.
"""


import utils_constant as const
from routine_u_kca import routine_u_kca_wrapper
from utils_io_file_structure import io_nomenc

#import specific for this script: for the whole inventory
from utils_io_file_structure import io_u_inventory_crt, io_em_inventory_crt, io_out_inventory_crt

import pathlib
root_path = pathlib.Path().resolve()
root_path= str(root_path)
#===========================================================================
# CHOOSE PROPERTIES
#===========================================================================

#set the base year
BY_string = "1990"

#set the reporting year
RY_string = "2022"

#Number of Monte Carlo simulations
# use no_mc < 10000 for tests
#use no_mc > 100000 for a "real" run
no_mc = 1000

use_fuel_used = False #set to True to use "fuel used" approach for the CLRTAP reporting
plot_mode = True #Set to True to plot figures
make_new_output_folder = False #Set to True to create a new, unique folder name to store the results

#======================================================================
# IMPORT FILES SPECIFIC FOR THIS RUN: INVENTORY EMISSIONS
#======================================================================

#automatically set submission year (do not modify)
sub_string = str(int(RY_string)+2)

#load nomenclature
dict_io_nomenc = io_nomenc(root_path, sub_string)

#load specific data structure description
dict_io_u = io_u_inventory_crt(root_path, sub_string, BY_string) #for input uncertainties
dict_io_em = io_em_inventory_crt(root_path, sub_string, BY_string) #for input emissions
dict_io_out = io_out_inventory_crt(root_path, sub_string, BY_string, make_new_output_folder) #for target output files

comp_total = const.COMP_TOTAL_NID #list of strings with compounds to report
routine = const.ROUTINE_NID #use ROUTINE_NID for NID reporting, routine_IIR for IIR reporting.

routine_u_kca_wrapper(
        routine = routine,
        BY_string = BY_string,
        RY_string = RY_string,
        comp_total = comp_total,
        no_mc = int(round(no_mc)),
        plot_mode = plot_mode,
        dict_io_nomenc = dict_io_nomenc,
        dict_io_em = dict_io_em,
        dict_io_u = dict_io_u,
        dict_io_out = dict_io_out,
        use_fuel_used = use_fuel_used,
        root_path = root_path,
              )
