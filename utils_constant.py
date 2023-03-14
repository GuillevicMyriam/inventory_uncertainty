# -*- coding: utf-8 -*-
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

Created on Tue Feb 15 11:48:31 2022

list of constant used through the entire code

PEP 8 stype recommendation: 
    Constants are usually defined on a module level and written in all capital 
    letters with underscores separating words. 
    Examples include MAX_OVERFLOW and TOTAL.

"""
#Set EMEP and IPCC requirements

#===================================================
#OFFICIAL REQUIREMENTS FOR THE UNCERTAINTY ANALYSIS
#===================================================

#The requirements are the same for the EMEP and IPCC guidelines.
#output results: set confidence interval as 95% of distribution
P_DIST = float(0.95) #search interval that covers 95% of distribution
#set edge values for a centered confidence interval
DIST_PPF_EDGE_LOWER = float(0.025)
DIST_PPF_EDGE_UPPER = float(0.975)

#===================================================
#OFFICIAL REQUIREMENTS FOR THE KEY CATEGORY ANALYSIS
#===================================================

#EMEP reporting requirements for key category analysis
KCA_1_P_IIR = float(0.8) #KCA approach 1 (without U), set threshold as 80% of all contributions
KCA_2_P_IIR = float(0.8) #KCA approach 2 (with U),    set threshold as 80% of all contributions
#EMEP extended criteria to display additional, non-key-categories in result lists and tables
KCA_1_P_EXT_IIR = float(0.85)
KCA_2_P_EXT_IIR = float(0.85)

#IPCC reporting requirements for key category analysis
KCA_1_P_NID = float(0.95) #KCA approach 1 (without U), set threshold as 95% of all contributions
KCA_2_P_NID = float(0.9)  #KCA approach 2 (with U),    set threshold as 90% of all contributions
#IPCC extended criteria to display additional, non-key-categories in result lists and tables
KCA_1_P_EXT_NID = float(0.97)
KCA_2_P_EXT_NID = float(0.92)

#Constants to handle input data
#for IIR, input data are all in tons (t) and values ar quite small
#and therefore require a large number of significant digit
#so instead we convert the input data and multiply by a factor thousand,
#results will be expressed in kt
IIR_FACTOR_CONV_EM_UNIT = float(1000.0)

#for NID we use input values as they are, we do not convert to any other unit
NID_FACTOR_CONV_EM_UNIT = float(1.0)

#value to convert s standard deviation (1 sigma) 
#to a 95% confidence interval for a normal distribution
#and vice versa
FACTOR_U_DIST_95_PERCENT = float(1.96) 

#string in the input uncertainty file used to stipulate that two variables are corelated
STRING_CORRELATED_DE = "korreliert" #in German
STRING_CORRELATED_EN = "correlated" #in English
STRING_CORRELATED = STRING_CORRELATED_DE

IIR_UNIT_STRING = "t"

NID_UNIT_STRING = "kt CO2 eq."
NID_UNIT_STRING_SHORT = "kt CO2 eq."
NID_UNIT_STRING_LATEX = "kt CO$_2$ eq."

#===================================================
#SET OUTPUT FORMATTING
#===================================================

#Set output format to write numbers in Excel sheets
#The following style use a comma as thousand separator.
#Note: this is actually not conform with BIPM guidelines.
FORMAT_VAL_U = "#,##0"
FORMAT_VAL_EM = "#,##0.00"
FORMAT_VAL_CONTRIB = "#,##0.000"
FORMAT_VAL_TOTAL = "#,##0.0"

NID_FORMAT_VAL_U_INPUT = "#,##0.0"
IIR_FORMAT_VAL_U_INPUT = "#,##0"

FORMAT_VAL_0D = "#,##0"
FORMAT_VAL_1D = "#,##0.0"
FORMAT_VAL_2D = "#,##0.00"
FORMAT_VAL_3D = "#,##0.000"
FORMAT_VAL_4D = "#,##0.0000"
FORMAT_VAL_5D = "#,##0.00000"
FORMAT_VAL_6D = "#,##0.000000"

#format in excel to allign on the decimal point
#https://www.extendoffice.com/documents/excel/1951-excel-align-decimal-points.html
#use only after appropriate rounding has been applied
#TODO 20230214 this formatting does not work so far.
#FORMAT_VAL_ALIGNED_0D = "#,##0.?"
FORMAT_VAL_ALIGNED_1D = "0.?"
FORMAT_VAL_ALIGNED_2D = "0.??"
FORMAT_VAL_ALIGNED_3D = "0.???"
FORMAT_VAL_ALIGNED_4D = "0.????"
FORMAT_VAL_ALIGNED_5D = "0.?????"
FORMAT_VAL_ALIGNED_6D = "0.??????"


"""
FORMAT_VAL_ALIGNED_1D = "#,##0.?"
FORMAT_VAL_ALIGNED_2D = "#,##0.??"
FORMAT_VAL_ALIGNED_3D = "#,##0.???"
FORMAT_VAL_ALIGNED_4D = "#,##0.????"
FORMAT_VAL_ALIGNED_5D = "#,##0.?????"
FORMAT_VAL_ALIGNED_6D = "#,##0.??????"
"""

"""
FORMAT_VAL_U = "##0"
FORMAT_VAL_EM = "##0.00"
FORMAT_VAL_CONTRIB = "##0.000"
FORMAT_VAL_TOTAL = "##0.0"

NID_FORMAT_VAL_U_INPUT = "##0.0"
IIR_FORMAT_VAL_U_INPUT = "##0"
"""

#max number of lines in an excel table that is later inserted into a Word document
FORMAT_LINE_PER_PAGE_EXCEL = 65

#COLORS
#Use this to convert RGB to Excel code:
#https://www.rapidtables.com/convert/color/rgb-to-hex.html
    
COLOR_ZERO = "BFBFBF"
COLOR_GREY = "BFBFBF"
COLOR_POSITIVE_TREND = "FFCC99" #peach # "FF8080" #salmon

COLOR_BY = "xkcd:goldenrod"
COLOR_RY = 'xkcd:blue'
COLOR_GRID = "xkcd:grey" #light grey


#Constants for Python routines
#assign an integer to each supported distribution type
DIST_UNIFORM = 0
DIST_NORMAL = 1
DIST_TRIANGULAR = 2
DIST_GAMMA = 3
DIST_LOGNORMAL = 4
DIST_FRACTILE = 5


#assign an integer to each supported routine type
ROUTINE_IIR = 0
ROUTINE_NID = 1
ROUTINE_IIR_WITHOUT_U = 2




IIR_NOMENC_CLASS_ID = "NFR"
NID_NOMENC_CLASS_ID = "CRT"

#List of recognised notation keys
NOTATION_KEY = ["NA", "NO", "NE", "IE", "C", "ES"]

INDIRECT_GASES = ["Indirect CO2 from CO", "Indirect CO2 from NMVOC", "Indirect CO2 from CH4"]

#list of compounds to report for a specific "indirect emissions" run
COMP_TOTAL_NID_INDIRECT = ["CO2 fossil ox CH4", "CO2 fossil ox CO", "CO2 fossil ox NMVOC total"]
#list of compounds to report for the NID, for the whole inventory
COMP_TOTAL_NID = ["CO2", "CH4", "N2O", "HFCs", "PFCs", "SF6", "NF3", "CO2 fossil ox. total"]
#list of compounds to report for the IIR, for the whole inventory
COMP_TOTAL_IIR = ["NOx", "NMVOC", "SOx", "NH3", "PM2.5", "PM10"]

PROC_CODE_SECTOR_TOTAL = ["1", "2", "3", "4", "5", "6"]
PROC_CODE_INVENTORY_WITH_WITHOUT_LULUCF = ["Total excl. LULUCF", "Total incl. LULUCF"]

NID_PROC_ID_TOTAL = "CRT Total incl. LULUCF"
IIR_PROC_ID_TOTAL = "NFR Total"
RESO_TOTAL = "Total"
RESO_TOTAL_INTERMEDIATE = "All resources"

PROC_CODE_FUEL_SOLD = ["1A3b", "1A3bi", "1A3bii", "1A3biii", "1A3biv" , "1A3bv" , "1A3bvi" , "1A3bvii"]
PROC_CODE_FUEL_USED = ["1A3b(fu)", "1A3bi(fu)", "1A3bii(fu)", "1A3biii(fu)", "1A3biv(fu)" , "1A3bv(fu)" , "1A3bvi(fu)" , "1A3bvii(fu)"]
