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
for the IIR, according to the NFR nomenclature.
"""


import utils_constant as const
from routine_u_kca import routine_u_kca_wrapper
from utils_io_file_structure import io_nomenc

#import specific for this script: for the whole inventory
from utils_io_file_structure import io_u_inventory_nfr, io_em_inventory_nfr, io_out_inventory_nfr

import pathlib
root_path = pathlib.Path().resolve()

#===========================================================================
# CHOOSE PROPERTIES
#===========================================================================

#set the base year
#the base year emissions must be found in an NFR table
BY_string = "1990"

#set the reporting year
#RY_string = "2019"
RY_string = "2021"

#Number of simulations for the Monte Carlo uncertainty estimation
no_mc = 1000

use_fuel_used = True
plot_mode = True
make_new_output_folder = False

#======================================================================
# IMPORT FILES SPECIFIC FOR THIS RUN: INVENTORY EMISSIONS
#======================================================================

#automatically set submission year (do not modify)
sub_string = str(int(RY_string)+2)

dict_io_nomenc = io_nomenc(root_path, sub_string)

dict_io_u = io_u_inventory_nfr(root_path, sub_string, BY_string)
dict_io_em = io_em_inventory_nfr(root_path, sub_string)
dict_io_out = io_out_inventory_nfr(root_path, sub_string, make_new_output_folder)

comp_total = const.COMP_TOTAL_IIR
routine = const.ROUTINE_IIR

routine_u_kca_wrapper(
        routine,
        BY_string,
        RY_string,
        comp_total,
        int(round(no_mc)),
        plot_mode,
        dict_io_nomenc,
        dict_io_em,
        dict_io_u,
        dict_io_out,
        use_fuel_used,
        root_path,
              )

