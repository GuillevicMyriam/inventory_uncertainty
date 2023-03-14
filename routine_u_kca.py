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

"""

import pandas as pd
import numpy as np
import time

import utils_constant as const


from utils_io_read_check import\
read_excel_nomenc_def,\
input_em_data_check,\
input_u_data_preparation,\
input_u_data_check_completeness_per_year,\
merge_with_proc,\
check_main,\
check_duplicate,\
merge_with_main,\
input_u_data_check_correlation,\
find_index_inventory_total

from utils_compute import\
groupby_one_attribute_pd,\
compute_U_propagation_em_pd,\
compute_U_propagation_trend_pd,\
compute_U_propagation_normalisation_pd,\
generate_random_value,\
find_interval_np #, find_interval, find_interval_pd, find_interval_np_zeronan

from utils_plot import\
plot_distributions_EM_trend,\
tornado_plot_EM_BY_RY

from utils_io_write_to_excel import write_pr_mc_results



def routine_u_kca_wrapper(
        routine: int,
        BY_string: str,
        RY_string: str,
        comp_total: list,
        no_mc: int,
        plot_mode: bool,
        dict_io_nomenc: dict,
        dict_io_em: dict,
        dict_io_u: dict,
        dict_io_out: dict,
        use_fuel_used: bool,
        root_path: str,
        ):

    
    """Script to compute uncertainty analysis and key category analysis
    
    This script computes the uncertainty following the guidelines 
    as in the 2019 IPCC Refinement, following two approaches:
        - approach 1: (simplified) uncertainty propagation;
        - approach 2: Monte Carlo simulations.
        
    Since very few informtion is given for approach 2, we try to apply
    as much as possible the recommendations from JCGM 2008, Supplement 1.
    
    Args:
        routine: integer coding for the method type, for greenhouse gases or pollutants.
            The main difference is that all greenhouse gases can be aggregated together,
            as long as they are all expressed in (tons of) CO2 equivalent,
            while pollutants cannot. This has consequences for the key category analysis.
        BY_string: string with the base year, format YYYY, i.e. "1990".
        RY_string: string with the reprting year, format YYYY.
        comp_total: list of names with the total compound.
        no_mc: number of Monte Carlo simulations to be performed.
            Use a small number for test purposes (e.g., 1000),
            use a large number for a real simulation.
            JCGM 2008 recommends at least one million.
            Check the memory of your computer first.
        plot_mode: to plot figures or not (do not plot figures to save time).
        dict_io_nomenc: dictionary containing information 
            where to load the nomenclature from.
        dict_io_em: dictionary containing information 
            where to load the emission values from.
        dict_io_u: dictionary containing information where 
            to load the uncertainties from.
        dict_io_out: dictionary containing information 
            where to export the results.
        use_fuel_used: applicable for pollutants only according to the CLRTAP. 
            Use "True" if your country is allowed to use "fuel used" for the compliance total.
            Use "False" otherwise: the total is then the 
            National Total according to the approach "fuel sold".
        root_path: path where the run files are saved.
            This may be needed on some old Python versions.
        
        
        
    Returns:
        WIP.
        Should return results required for the key category analysis.
        
    Raises:
        The procedure stops in case input values are not valid.
        
    """
        
    #++++++start of routine file++++++++++++++++++++++++
    
    
    check_file = open(dict_io_out["check_filename"], "w")    
    #--------------------------------------
    #Read input nomenclature for base year
    #--------------------------------------
    
    t0_read_input_main = time.time()
    
    
    #=============================================
    # DEFINE ROUTINE TYPE: ALL COMPOUNDS TOGETHER (GHG) OR EACH COMPOUND SEPARATELY (POLLUTANTS)
    #=============================================
    
    if routine == const.ROUTINE_IIR or routine == const.ROUTINE_IIR_WITHOUT_U:
        in_proc_agg_tree_sheetname = dict_io_nomenc["in_proc_agg_tree_nfr_sheetname"]
    elif routine == const.ROUTINE_NID:    
        in_proc_agg_tree_sheetname = dict_io_nomenc["in_proc_agg_tree_crt_sheetname"]

    
    #=============================================
    # READ INPUT NOMENCLATURE: NAMES FOR PROCESSES, COMPOUNDS, RESOURCES
    #=============================================
    
    #t0_read_input = time.time()
    
    #Read input nomenclature for process names
    df_proc = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"],
            sheetname = dict_io_nomenc["in_proc_sheetname"], 
            header = dict_io_nomenc["in_header_proc"], 
            skiprows = dict_io_nomenc["in_skiprows_proc"], 
            usecols = dict_io_nomenc["in_usecols_proc"], 
            names = dict_io_nomenc["in_col_names_proc"], 
            )
    #Read input nomenclature for compounds
    df_comp = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"],
            sheetname = dict_io_nomenc["in_comp_sheetname"], #Warning! for newer pandas version use sheet_name
            header = dict_io_nomenc["in_header_comp"], 
            skiprows = dict_io_nomenc["in_skiprows_comp"], 
            usecols = dict_io_nomenc["in_usecols_comp"], 
            names = dict_io_nomenc["in_col_names_comp"], 
            #engine = "openpyxl"
            )
    #Read input nomenclature for resources
    df_reso = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"],
            sheetname = dict_io_nomenc["in_reso_sheetname"], #Warning! for newer pandas version use sheet_name
            header = dict_io_nomenc["in_header_reso"],  
            skiprows = dict_io_nomenc["in_skiprows_reso"], 
            usecols = dict_io_nomenc["in_usecols_reso"], 
            names = dict_io_nomenc["in_col_names_reso"], 
            #engine = "openpyxl"
            )
    

    
    #=============================================
    # IMPORT AGGREGATION TREES
    #=============================================
    
    
    #=============================================
    # IMPORT AGGREGATION TREE FOR COMPOUND
    #=============================================
    
    df_agg_tree_comp = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"],  
            sheetname = dict_io_nomenc["in_comp_agg_tree_sheetname"],  #Warning! for newer pandas version use sheet_name
            header = dict_io_nomenc["in_header_agg_comp"],
            skiprows = dict_io_nomenc["in_skiprows_agg_comp"], 
            usecols = dict_io_nomenc["in_usecols_agg_comp"], 
            names = dict_io_nomenc["in_names_agg_comp"],
            dtype = dict_io_nomenc["in_dtype_agg_comp"],
            )
    
    #search for all valid compound_id as child in table of child_parent
    #if child not found, drop rows and write in check_file.
    df_agg_tree_comp = check_main(
            df = df_agg_tree_comp,
            df_main = df_comp,
            col_left = ["child_id_comp"],
            col_right = ["comp_id"],
            check_file = check_file,
            )
    df_agg_tree_comp = check_main(
            df = df_agg_tree_comp,
            df_main = df_comp,
            col_left = ["parent_id_comp"],
            col_right = ["comp_id"],
            check_file = check_file,
            )
    check_duplicate(
            df = df_agg_tree_comp,
            in_pathname = None,
            in_sheetname = None,
            df_str_name = "df_agg_tree_comp",
            in_col_unique = ["child_id_comp"],
            check_file = check_file,
            )
    
    #=============================================
    # IMPORT AGGREGATION TREE FOR RESOURCE
    #=============================================
    
    df_agg_tree_reso = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"], 
            sheetname = dict_io_nomenc["in_reso_agg_tree_sheetname"],#Warning! for newer pandas version use sheet_name
            header = dict_io_nomenc["in_header_agg_reso"], 
            skiprows = dict_io_nomenc["in_skiprows_agg_reso"], 
            usecols = dict_io_nomenc["in_usecols_agg_reso"], 
            names = dict_io_nomenc["in_names_agg_reso"],
            dtype = dict_io_nomenc["in_dtype_agg_reso"],
            )
    df_agg_tree_reso = check_main(
            df = df_agg_tree_reso,
            df_main = df_reso,
            col_left = ["child_id_reso"], 
            col_right = ["reso_id"],
            check_file = check_file,
            )
    df_agg_tree_reso = check_main(
            df = df_agg_tree_reso,
            df_main = df_reso,
            col_left = ["parent_id_reso"], 
            col_right = ["reso_id"],
            check_file = check_file,
            )
    check_duplicate(
            df = df_agg_tree_reso,
            in_pathname = None,
            in_sheetname = None,
            df_str_name = "df_agg_tree_reso",
            in_col_unique = ["child_id_reso"],
            check_file = check_file,
            )
    
    #=============================================
    # IMPORT AGGREGATION TREE FOR PROCESS NAMES
    #=============================================
    
    df_agg_tree_proc = pd.read_excel(
            io = dict_io_nomenc["in_nomenc_pathname"], 
            sheetname = in_proc_agg_tree_sheetname,  #Warning! for newer pandas version use sheet_name
            header = dict_io_nomenc["in_header_agg_proc"], 
            skiprows = dict_io_nomenc["in_skiprows_agg_proc"], 
            usecols = dict_io_nomenc["in_usecols_agg_proc"], 
            names = dict_io_nomenc["in_names_agg_proc"], #["child_id_proc", "parent_id_proc", "depth_id_proc"],
            dtype = dict_io_nomenc["in_dtype_agg_proc"], #{"child_id_proc": np.str, "parent_id_proc": np.str, "depth_id_proc": np.int}
            )
    #merge with proc_id for the child column
    df_agg_tree_proc = merge_with_proc(
            df = df_agg_tree_proc,
            df_proc = df_proc,
            col_from_main = dict_io_em["in_col_from_main_proc"], #columns to use from the main (primary) df
            col_merge_left_on = ["child_id_proc_class", "child_id_proc_code"], #cols to merge on from df
            col_merge_right_on = dict_io_nomenc["in_merge_with_proc_right"], #cols to merge on from primary df
            col_merge_drop_left = None, #["child_id_proc_class", "child_id_proc_code"],
            col_name_proc_id = "child_id_proc",
            check_file = check_file,
            )
    #merge with proc_id for the parent column
    df_agg_tree_proc = merge_with_proc(
            df = df_agg_tree_proc,
            df_proc = df_proc,
            col_from_main = dict_io_em["in_col_from_main_proc"], #columns to use from the main (primary) df
            col_merge_left_on = ["parent_id_proc_class", "parent_id_proc_code"], #cols to merge on from df
            col_merge_right_on = dict_io_nomenc["in_merge_with_proc_right"], #cols to merge on from primary df
            col_merge_drop_left = None, #["parent_id_proc_class", "parent_id_proc_code"],
            col_name_proc_id = "parent_id_proc",
            check_file = check_file,
            )
    
    check_duplicate(
            df = df_agg_tree_proc,
            in_pathname = None,
            in_sheetname = None,
            df_str_name = "df_agg_tree_proc",
            in_col_unique = ["child_id_proc"],
            check_file = check_file,
            )

    t1_read_input_main = time.time() - t0_read_input_main
    check_file.write("Run time for reading nomenclature inputs: " + str(t1_read_input_main) + " seconds\n")
    print("Run time for reading nomenclature inputs: " + str(t1_read_input_main) + " seconds")
    
    #TODO here start the loop over each compound
    for i_comp in range(len(dict_io_em["in_usecols_EM_RY_val"])):
        #For GHG, this loop is run once only
        #For pollutant, once for each pollutant.
        
        if i_comp == 0:
            df_EM_u, df_pr_out, df_pr_out_AD_EF, df_mc_out, df_mc_out_AD_EF = routine_u_kca_computations(               
                    routine,
                    BY_string,
                    RY_string,
                    comp_total,
                    no_mc,
                    plot_mode,
                    dict_io_nomenc,
                    dict_io_em,
                    dict_io_u,
                    dict_io_out,
                    i_comp,
                    df_proc,
                    df_comp,
                    df_reso,
                    df_agg_tree_proc,
                    df_agg_tree_comp,
                    df_agg_tree_reso,
                    use_fuel_used,
                    check_file,
                    )
            
        else:
            df_EM_u_i, df_pr_out_i, df_pr_out_AD_EF_i, df_mc_out_i, df_mc_out_AD_EF_i = routine_u_kca_computations(               
                    routine,
                    BY_string,
                    RY_string,
                    comp_total,
                    no_mc,
                    plot_mode,
                    dict_io_nomenc,
                    dict_io_em,
                    dict_io_u,
                    dict_io_out,
                    i_comp,
                    df_proc,
                    df_comp,
                    df_reso,
                    df_agg_tree_proc,
                    df_agg_tree_comp,
                    df_agg_tree_reso,
                    use_fuel_used,
                    check_file,
                    )
            
            #TODO Concatenat results to get all required values for the KCA.
            #df_EM_u = pd.concat([df_EM_u, df_EM_u_i], axis =0, ignore_index=True)
            


    #TODO Here would be the place to export the KCA results to excel.
    check_file.close()
    return None



def routine_u_kca_computations(
        routine,
        BY_string,
        RY_string,
        comp_total,
        no_mc,
        plot_mode,
        dict_io_nomenc,
        dict_io_em,
        dict_io_u,
        dict_io_out,
        i_comp,
        df_proc,
        df_comp,
        df_reso,
        df_agg_tree_proc,
        df_agg_tree_comp,
        df_agg_tree_reso,
        use_fuel_used,
        check_file,
        ):
    #XXXroutine comtaining the computations for uncertainties approach 1 and approach 2
    """Load numeric input values and compute uncertainty.
    
    Load values for input emissions and associated uncertainties for AD, EF or EM.
    Check that all source categories are valid according to the nomenclature.
    Compue uncertainty estimation according to uncertainty propagation (IPCC approach 1)
    and Monte Carlo somilations (IPCC approach 2).

    Args:
        routine: integer coding for the method type, for greenhouse gases or pollutants.
            The main difference is that all greenhouse gases can be aggregated together,
            as long as they are all expressed in (tons of) CO2 equivalent,
            while pollutants cannot. This has consequences for the key category analysis.
        BY_string: string with the base year, format YYYY, i.e. "1990".
        RY_string: string with the reprting year, format YYYY.
        comp_total: list of names with the total compound.
        no_mc: number of Monte Carlo simulations to be performed.
            Use a small number for test purposes (e.g., 1000),
            use a large number for a real simulation.
            JCGM 2008 recommends at least one million.
            Check the memory of your computer first.
        plot_mode: to plot figures or not (do not plot figures to save time).
        dict_io_nomenc: dictionary containing information 
            where to load the nomenclature from.
        dict_io_em: dictionary containing information 
            where to load the emission values from.
        dict_io_u: dictionary containing information where 
            to load the uncertainties from.
        dict_io_out: dictionary containing information 
            where to export the results.
        i_comp: loop index for the compound. This loop is called only once for greenhouse gases
            but once for each compound for the pollutants.
        df_proc: pandas DataFrame containing nomenclature for source category names.
        df_comp: pandas DataFrame containing nomenclature for compound names.
        df_reso: pandas DataFrame containing nomenclature for resource names (fuels and others).
        df_agg_tree_proc: pandas DataFrame containing the aggregation tree for source categories.
        df_agg_tree_comp: pandas DataFrame containing the aggregation tree for compounds.
        df_agg_tree_reso: pandas DataFrame containing the aggregation tree for resources.
        use_fuel_used: applicable for pollutants only according to the CLRTAP. 
            Use "True" if your country is allowed to use "fuel used" for the compliance total.
            Use "False" otherwise: the total is then the 
            National Total according to the approach "fuel sold".
        check_file: text file where results of automated quality checks are saved.

            
    Returns: results of the uncertainty estimations.

            
    """


    t0_read_input = time.time()
    
    if routine == const.ROUTINE_IIR:
        comp_string = dict_io_em["in_col_names_comp"][i_comp]
        unit_string = const.IIR_UNIT_STRING
        unit_string_plot = unit_string
        proc_id_total = const.IIR_PROC_ID_TOTAL #"NFR Total"
        reso_id_total = const.RESO_TOTAL #"Total"

        #columns for input emissions
        dict_io_em["in_usecols_EM_BY"] = dict_io_em["in_usecols_EM_BY_nomenc"] + [dict_io_em["in_usecols_EM_BY_val"][i_comp]]
        dict_io_em["in_usecols_EM_RY"] = dict_io_em["in_usecols_EM_RY_nomenc"] + [dict_io_em["in_usecols_EM_RY_val"][i_comp]]
        #columns for input uncertainties
        dict_io_u["in_usecols_u"] = dict_io_u["in_usecols_u_nomenc"] + dict_io_u["in_usecols_u_AD"] + dict_io_u["in_usecols_u_EF"][i_comp]
        
        #Output file names
        dict_io_out["filename_KCA_mc_out"] = dict_io_out["filename_out_KCA_root"] + comp_string + ".xlsx"
        dict_io_out["filename_out_u_input"] = dict_io_out["filename_out_u_input_root"] + comp_string + ".xlsx"
        dict_io_out["filename_out_u"] = dict_io_out["filename_out_u_root"] + comp_string + ".xlsx"
        dict_io_out["figname_out_mc_tornado"] = dict_io_out["figname_out_mc_tornado_root"] + comp_string #do not add extension yet!
        dict_io_out["figname_out_mc_distribution"] = dict_io_out["figname_out_mc_distribution_root"] + comp_string #do not add extension yet!
        
        
    elif routine == const.ROUTINE_NID:
        comp_string = None       
        unit_string = const.NID_UNIT_STRING
        unit_string_plot = const.NID_UNIT_STRING_LATEX 
        proc_id_total = const.NID_PROC_ID_TOTAL #"CRT Total incl. LULUCF"
        reso_id_total = const.RESO_TOTAL #"Total"
        
        #Output file names
        dict_io_out["filename_KCA_mc_out"] = dict_io_out["filename_out_KCA_root"] + ".xlsx"
        dict_io_out["filename_out_u_input"] = dict_io_out["filename_out_u_input_root"] + ".xlsx"
        dict_io_out["filename_out_u"] = dict_io_out["filename_out_u_root"] + ".xlsx"
        dict_io_out["figname_out_mc_tornado"] = dict_io_out["figname_out_mc_tornado_root"] #do not add extension yet!
        dict_io_out["figname_out_mc_distribution"] = dict_io_out["figname_out_mc_distribution_root"] #do not add extension yet!

    agg_proc = True
    use_col_agg_proc = ["parent_id_proc", "depth_id_proc"]
    use_col_agg_comp = ["parent_id_comp", "depth_id_comp"]
    use_col_agg_reso = ["parent_id_reso", "depth_id_reso"]
    use_cols_id = ["proc_id", "comp_id", "reso_id"]

    #==========================================
    #IMPORT LIST OF OUTPUT PROCESSES TO REPORT
    #==========================================
    
    df_proc_out = read_excel_nomenc_def(
            in_pathname = dict_io_out["out_nomenc_pathname"],
            in_sheetname = dict_io_out["out_nomenc_sheetname"],
            in_header = dict_io_out["header_out_nomenc"],
            in_skiprows = dict_io_out["skiprows_out_nomenc"],
            in_usecols = dict_io_out["usecols_out_nomenc"],
            in_col_names = dict_io_out["col_names_out_nomenc"],
            in_col_dtype = dict_io_out["col_dtype_out_nomenc"],
            #next are parameters from the main nomenclature definition
            in_col_unique = dict_io_em["in_col_unique_em"],
            col_from_main_proc = dict_io_em["in_col_from_main_proc"],
            col_merge_left_on_proc = dict_io_nomenc["in_merge_with_proc_left"],
            col_merge_right_on_proc = dict_io_nomenc["in_merge_with_proc_right"],
            df_proc = df_proc,
            col_check_left_on_comp = ["comp_id"], 
            col_check_right_on_comp = ["comp_id"], 
            df_comp = df_comp,
            col_check_left_on_reso = ["reso_id"],
            col_check_right_on_reso = ["reso_id"],
            df_reso = df_reso,
            comp_string = comp_string,
            use_fuel_used = use_fuel_used,
            check_file = check_file,
            )
    
    #=============================================
    # READ INPUT EMISSIONS
    #=============================================
    
    #Read Excel data for input emissions for the base year
    check_file.write("************************************************\n")
    check_file.write("Reading input emissions for the base year...\n")
    df_EM_BY = read_excel_nomenc_def(
            in_pathname = dict_io_em["in_pathname_EM_BY"],
            in_sheetname = dict_io_em["in_sheetname_EM_BY"],
            in_header = dict_io_em["in_header_EM_BY"],
            in_skiprows = dict_io_em["in_skiprows_EM_BY"],
            in_usecols = dict_io_em["in_usecols_EM_BY"],
            in_col_names = dict_io_em["in_col_names_EM_BY"],
            in_col_dtype = dict_io_em["in_col_dtype_EM_BY"],
            in_col_unique = dict_io_em["in_col_unique_em"],
            col_from_main_proc = dict_io_em["in_col_from_main_proc"],
            col_merge_left_on_proc = dict_io_nomenc["in_merge_with_proc_left"],
            col_merge_right_on_proc = dict_io_nomenc["in_merge_with_proc_right"],
            df_proc = df_proc,
            col_check_left_on_comp = ["comp_id"], 
            col_check_right_on_comp = ["comp_id"], 
            df_comp = df_comp,
            col_check_left_on_reso = ["reso_id"],
            col_check_right_on_reso = ["reso_id"],
            df_reso = df_reso,
            comp_string = comp_string,
            use_fuel_used = use_fuel_used,
            check_file = check_file,
            )
    
    df_EM_BY = input_em_data_check(df_EM_BY, "BY", check_file)
    
    #Read Excel data for input emissions for the reporting year
    check_file.write("************************************************\n")
    check_file.write("Reading input emissions for the reporting year...\n")
    df_EM_RY = read_excel_nomenc_def(
            in_pathname = dict_io_em["in_pathname_EM_RY"],
            in_sheetname = dict_io_em["in_sheetname_EM_RY"],
            in_header = dict_io_em["in_header_EM_RY"],
            in_skiprows = dict_io_em["in_skiprows_EM_RY"],
            in_usecols = dict_io_em["in_usecols_EM_RY"],
            in_col_names = dict_io_em["in_col_names_EM_RY"],
            in_col_dtype = dict_io_em["in_col_dtype_EM_RY"],
            in_col_unique = dict_io_em["in_col_unique_em"],
            col_from_main_proc = dict_io_em["in_col_from_main_proc"],
            col_merge_left_on_proc = dict_io_nomenc["in_merge_with_proc_left"],
            col_merge_right_on_proc = dict_io_nomenc["in_merge_with_proc_right"],
            df_proc = df_proc,
            col_check_left_on_comp = ["comp_id"], 
            col_check_right_on_comp = ["comp_id"], 
            df_comp = df_comp,
            col_check_left_on_reso = ["reso_id"],
            col_check_right_on_reso = ["reso_id"],
            df_reso = df_reso,
            comp_string = comp_string,
            use_fuel_used = use_fuel_used,
            check_file = check_file,
            )

    df_EM_RY = input_em_data_check(df_EM_RY, "RY", check_file)
    
    #Merge BY and RY: one row contains emissions for BY and RY (each in one column).
    df_EM_BY_RY = pd.merge(
            df_EM_BY, 
            df_EM_RY, 
            left_on = dict_io_em["in_col_unique_em"], 
            right_on = dict_io_em["in_col_unique_em"], 
            how="outer", 
            indicator="exists_BY_RY", 
            suffixes = ["_BY", "_RY"],
            copy = False
            )
    
    #Check for missing input for BY or for RY.
    
    df_EM_BY_RY["unit_trend_normed"] = "%"
    df_EM_BY_RY["EM_status_trend_normed"] = "ES"
    
    count_missing_data = 0
    for i in range(len(df_EM_BY_RY)):
        if not df_EM_BY_RY["EM_is_num_BY"].iloc[i]:
            check_file.write("Code <{}>: missing input for BY.\n".format(df_EM_BY_RY["proc_id"].iloc[i]))
        if not df_EM_BY_RY["EM_is_num_RY"].iloc[i]:
            check_file.write("Code <{}>: missing input for RY.\n".format(df_EM_BY_RY["proc_id"].iloc[i]))
        if df_EM_BY_RY["exists_BY_RY"].iloc[i] == "left_only":
            check_file.write("Code <{}>: missing input for RY.\n".format(df_EM_BY_RY["proc_id"].iloc[i]))
            count_missing_data += 1
        if df_EM_BY_RY["exists_BY_RY"].iloc[i] == "right_only":
            check_file.write("Code <{}>: missing input for BY.\n".format(df_EM_BY_RY["proc_id"].iloc[i]))
            count_missing_data += 1
            
        #Done  20230216 Derive status and is_num from emissions
        if df_EM_BY_RY["EM_status_BY"].iloc[i] == df_EM_BY_RY["EM_status_RY"].iloc[i]:
            df_EM_BY_RY["EM_status_trend_normed"].iloc[i] = df_EM_BY_RY["EM_status_RY"].iloc[i]
        elif df_EM_BY_RY["EM_status_BY"].iloc[i] == "ES" or df_EM_BY_RY["EM_status_RY"].iloc[i] == "ES":
            df_EM_BY_RY["EM_status_trend_normed"].iloc[i] = "ES"
    
    if count_missing_data > 0:
        check_file.write("There were unmatched input for emissions between base year and reporting year. Please check.")
        check_file.close()
        raise ValueError("There were unmatched input for emissions between base year and reporting year. Please check.")
    #Then drop check column
    df_EM_BY_RY.drop(["exists_BY_RY"], axis=1, inplace=True) #use axis=1 to drop columns, axis=0 to drop rows.
    
    #Compute inventory data
    EM_BY_inventory = np.nansum(df_EM_BY_RY['EM_BY']) #aggregated emissions
    EM_RY_inventory = np.nansum(df_EM_BY_RY['EM_RY']) #aggregated emissions
    
    #Compute, for each source category, the contribution to the inventory trend
    df_EM_BY_RY["EM_trend_normed"] = np.float(0.0)
    if EM_BY_inventory != np.float(0.0):
        df_EM_BY_RY["EM_trend_normed"] = (df_EM_BY_RY["EM_RY"] - df_EM_BY_RY["EM_BY"]) / EM_BY_inventory * np.float(100)
    
    
    #=============================================
    # READ INPUT UNCERTAINTIES
    #=============================================
    
    #Read Excel data for input uncertainties
    check_file.write("************************************************\n")
    check_file.write("Reading input uncertainties for the reporting year...\n")
    df_u_RY = read_excel_nomenc_def(
            in_pathname = dict_io_u["in_U_RY_pathname"], 
            in_sheetname = dict_io_u["in_U_RY_sheetname"], 
            in_header = dict_io_u["in_header_u"],
            in_skiprows = dict_io_u["in_skiprows_u"],
            in_usecols = dict_io_u["in_usecols_u"],
            in_col_names = dict_io_u["in_col_names_u"],
            in_col_dtype = dict_io_u["in_col_dtype_u"],
            in_col_unique = dict_io_em["in_col_unique_em"],
            col_from_main_proc = dict_io_em["in_col_from_main_proc"],
            col_merge_left_on_proc = dict_io_nomenc["in_merge_with_proc_left"],
            col_merge_right_on_proc = dict_io_nomenc["in_merge_with_proc_right"],
            df_proc = df_proc,
            col_check_left_on_comp = ["comp_id"], 
            col_check_right_on_comp = ["comp_id"], 
            df_comp = df_comp,
            col_check_left_on_reso = ["reso_id"],
            col_check_right_on_reso = ["reso_id"],
            df_reso = df_reso,
            comp_string = comp_string,
            use_fuel_used = use_fuel_used,
            check_file = check_file,
            )


    
    df_u_RY = input_u_data_preparation(
            df = df_u_RY, 
            input_type = "AD", 
            input_year = "RY",
            check_file = check_file,
            )
    
    df_u_RY = input_u_data_preparation(
            df = df_u_RY, 
            input_type = "EF", 
            input_year = "RY",
            check_file = check_file,
            )
    
    if "uEM_dist" in dict_io_u["in_col_names_u"]:
        df_u_RY = input_u_data_preparation(
                df = df_u_RY, 
                input_type = "EM", 
                input_year = "RY",
                check_file = check_file,
                )
    else:
        df_u_RY["uEM_is_num" ] = False
    
    #Check completeness of input data for AD, EF, EM
    df_u_RY = input_u_data_check_completeness_per_year(df_u_RY, "RY", check_file)
    
    if dict_io_u["in_U_BY_sheetname"] is None:
        df_u_BY = df_u_RY.copy()
    
    else:
        check_file.write("************************************************\n")
        check_file.write("Reading input uncertainties for the base year...\n")
    
        df_u_BY = read_excel_nomenc_def(
                in_pathname = dict_io_u["in_U_BY_pathname"], 
                in_sheetname = dict_io_u["in_U_BY_sheetname"], 
                in_header = dict_io_u["in_header_u"],
                in_skiprows = dict_io_u["in_skiprows_u"],
                in_usecols = dict_io_u["in_usecols_u"],
                in_col_names = dict_io_u["in_col_names_u"],
                in_col_dtype = dict_io_u["in_col_dtype_u"],
                in_col_unique = dict_io_em["in_col_unique_em"],
                col_from_main_proc = dict_io_em["in_col_from_main_proc"],
                col_merge_left_on_proc = dict_io_nomenc["in_merge_with_proc_left"],
                col_merge_right_on_proc = dict_io_nomenc["in_merge_with_proc_right"],
                df_proc = df_proc,
                col_check_left_on_comp = ["comp_id"], 
                col_check_right_on_comp = ["comp_id"], 
                df_comp = df_comp,
                col_check_left_on_reso = ["reso_id"],
                col_check_right_on_reso = ["reso_id"],
                df_reso = df_reso,
                comp_string = comp_string,
                use_fuel_used = use_fuel_used,
                check_file = check_file,
                )
    
        df_u_BY = input_u_data_preparation(
                df = df_u_BY, 
                input_type = "AD", 
                input_year = "BY",
                check_file = check_file,
                )
        
        df_u_BY = input_u_data_preparation(
                df = df_u_BY, 
                input_type = "EF", 
                input_year = "BY",
                check_file = check_file,
                )
    
        if "uEM_dist" in dict_io_u["in_col_names_u"]:
            df_u_BY = input_u_data_preparation(
                    df = df_u_BY, 
                    input_type = "EM", 
                    input_year = "BY",
                    check_file = check_file,
                    )
        else:
            df_u_BY["uEM_is_num" ] = False
        
        #if check_completeness_BY:
        #If missing data for U BY: take value from RY.    
        #(If RY also has a missing data, that's ok)
        for i in range(len(df_u_BY)):
            i_RY = df_u_RY.index[(df_u_RY["proc_id"] == df_u_BY["proc_id"].iloc[i]) &
                                 (df_u_RY["comp_id"] == df_u_BY["comp_id"].iloc[i]) & 
                                 (df_u_RY["reso_id"] == df_u_BY["reso_id"].iloc[i])
                                 ].tolist()
            if len(i_RY) == 0:
                check_file.write("Code <{}>: missing input for u, RY.\n".format(df_u_BY["proc_id"].iloc[i]))
            else:
                i_RY = i_RY[0]
                for col in df_u_BY.columns.values.tolist():
                    if col in df_u_RY:
                        if col in ["uAD_dist", "uEF_dist", "uEM_dist"]:
                            #if there is no input distribution type for BY: take value from RY
                            if df_u_BY[col].iloc[i] == -1 and df_u_RY[col].iloc[i_RY] != -1:
                                df_u_BY[col].iloc[i] = df_u_RY[col].iloc[i_RY]
                        else:
                            if (df_u_BY[col].iloc[i] == np.float(0.0) and df_u_RY[col].iloc[i_RY] > np.float(0.0))\
                            or df_u_BY[col].iloc[i] == "MI"\
                            or pd.isnull(df_u_BY[col].iloc[i]):
                                df_u_BY[col].iloc[i] = df_u_RY[col].iloc[i_RY]
    
        df_u_BY = input_u_data_check_completeness_per_year(df_u_BY, "BY", check_file)
    
    df_u_BY.drop(["uAD_corr"], axis=1, inplace=True)
    df_u_BY.drop(["uEF_corr"], axis=1, inplace=True)
    if "uEM_dist" in dict_io_u["in_col_names_u"]:
        df_u_BY.drop(["uEM_corr"], axis=1, inplace=True)
    
    
    #Then merge the input u for BY and RY
    df_u = pd.merge(
            df_u_BY, 
            df_u_RY, 
            left_on = dict_io_em["in_col_unique_em"], 
            right_on = dict_io_em["in_col_unique_em"], 
            how="outer", 
            indicator="exists_u_BY_RY", 
            suffixes = ["_BY", "_RY"],
            copy = False
            )
    
    count_missing_data = 0
    for i in range(len(df_u["exists_u_BY_RY"])):
        if df_u["exists_u_BY_RY"].iloc[i] == "left_only":
            check_file.write("Code <{}>: missing input for u, RY.\n".format(df_u["proc_id"].iloc[i]))
            count_missing_data += 1
        elif df_u["exists_u_BY_RY"].iloc[i] == "right_only":
            check_file.write("Code <{}>: missing input for u, BY.\n".format(df_u["proc_id"].iloc[i]))
            count_missing_data += 1
    
    if count_missing_data > 0:
        check_file.write("There were unmatched input for uncertainties between base year and reporting year. Please check.")
        check_file.close()
        raise ValueError("There were unmatched input for uncertainties between base year and reporting year. Please check.")
    
    df_u.drop(["exists_u_BY_RY"], axis=1, inplace=True)
    
                
    df_u["u_is_num"] = True
    
    #If input u for BY and RY are correlated, input dist and values must be exactly the same.
    df_u = input_u_data_check_correlation(df_u, check_file)
    
    
         
    #=============================================
    # MERGE INPUT EMISSIONS AND UNCERTAINTIES
    #=============================================
    
    df_EM_u = pd.merge(
            df_EM_BY_RY,
            df_u,
            left_on = dict_io_em["in_col_unique_em"],  
            right_on = dict_io_em["in_col_unique_em"], 
            how="outer", 
            indicator="exists_u_BY_RY", 
            suffixes = ["_EM", "_u"], #no suffixes will be applied because not needed, all columns from left or right have different names
            copy = False
            ) 
    
    
    #Check for missing data for base year or reporting year
    count_missing_data = 0
    for i in range(len(df_EM_u["exists_u_BY_RY"])):
         if df_EM_u["exists_u_BY_RY"].iloc[i] == "left_only":
             count_missing_data += 1
             check_file.write("Code <{}>, compound <{}>, resource <{}>: input provided for emission but missing for uncertainty.\n".format(df_EM_u["proc_id"].iloc[i], df_EM_u["comp_id"].iloc[i], df_EM_u["reso_id"].iloc[i]))
         elif df_EM_u["exists_u_BY_RY"].iloc[i] == "right_only":
             count_missing_data += 1
             check_file.write("Code <{}>, compound <{}>, resource <{}>: input provided for uncertainty but missing for emission.\n".format(df_EM_u["proc_id"].iloc[i], df_EM_u["comp_id"].iloc[i], df_EM_u["reso_id"].iloc[i]))
    
    df_EM_u["exists_u_BY_RY"] = np.where(df_EM_u["exists_u_BY_RY"] == "both", True, False)
    check_file.write("Found {} valid input for EM and u, for BY and RY.\n".format(sum([1 if val else 0 for val in df_EM_u["exists_u_BY_RY"]])))
    
    if count_missing_data > 0:
        check_file.write("There were unmatched input between uncertainties and emissions. Please check.")
        check_file.close()
        raise ValueError("There were unmatched input between uncertainties and emissions. Please check.")
        
    df_EM_u.drop(["exists_u_BY_RY"], axis=1, inplace=True)
    
    
    
    #Before doing any aggregation: create information that the contained rows are all input (not aggregated).
    df_EM_u["import"] = True
    
    
    
    
    #Check that all or none of the compounds can be aggregated together
    comp_list = pd.unique(df_EM_u["comp_id"])
    count_comp_in_agg_tree = sum([sum(df_agg_tree_comp["child_id_comp"].isin([comp])) for comp in comp_list])
    
    if count_comp_in_agg_tree == len(comp_list):
        #routine = const.ROUTINE_NID
        agg_comp = True
        #in_proc_agg_tree_sheetname = dict_io_nomenc["in_proc_agg_tree_crt_sheetname"]
        comp_id_total = "Total"
    elif count_comp_in_agg_tree == 0:
        #routine = const.ROUTINE_IIR
        agg_comp = False
        #in_proc_agg_tree_sheetname = dict_io_nomenc["in_proc_agg_tree_nfr_sheetname"]
        comp_id_total = df_EM_u["comp_id"].iloc[0]
    else:
        check_file.write("Check your compound names and your aggregation tree for compounds. Some can be aggregated but not all.")
        check_file.close()
        raise ValueError("Check your compound names and your aggregation tree for compounds. Some can be aggregated but not all.")
    
       
        
    #define if aggregation according to resource should occur or not
    reso_list = pd.unique(df_EM_u["reso_id"])
    reso_total_name = df_agg_tree_reso["parent_id_reso"].loc[df_agg_tree_reso["depth_id_reso"] == 1][0] #take the first occurence
    count_reso_total = sum([reso == reso_total_name for reso in reso_list])
    
    if count_reso_total == len(reso_list):
        agg_reso = False
    elif count_reso_total == 0:
        agg_reso = True
    else:
        check_file.write("Check your names for resource and your aggregation tree for resources. Some input resources have the name of the total resource, this is not allowed.")
        check_file.close()
        raise ValueError("Check your names for resource and your aggregation tree for resources. Some input resources have the name of the total resource, this is not allowed.")
    
        
    
    t1_read_input = time.time() - t0_read_input
    check_file.write("Run time for reading emissions and uncertainties inputs: " + str(t1_read_input) + " seconds\n")
    print("Run time for reading emissions and uncertainties inputs: " + str(t1_read_input) + " seconds")
    
    
    #=============================================
    # PREPARE AGGREGATION TREES
    #=============================================
    #To save memory space, do aggregation of each df separately: 
    #one for BY, one for RY, one for trend.
    
    
    use_col_agg_proc = []
    use_col_agg_comp = []
    use_col_agg_reso = []
    
    if agg_proc:
         
        #For each process in EM, find parent process to aggregate to.
        #In practice, merge EM data with aggregation tree.
        df_EM_u = pd.merge(
                df_EM_u, 
                df_agg_tree_proc, 
                left_on=["proc_id"], 
                right_on = ["child_id_proc"], 
                how="left", 
                indicator="exists_agg") #, validate = 'one_to_one'
        df_EM_u["exists_agg"] = np.where(df_EM_u["exists_agg"] == "both", True, False)
        for i in range(len(df_EM_u["exists_agg"])):
            if df_EM_u["exists_agg"].iloc[i] == False:
                check_file.write("Input process name {} was not found in aggregation tree for processes.\n".format(df_EM_u["proc_id"].iloc[i]))
        df_EM_u.drop(["child_id_proc", "exists_agg"], axis=1, inplace=True)
        use_col_agg_proc = ["parent_id_proc", "depth_id_proc"]
        
    
    if agg_comp: 
        #For each process in EM, find parent process to aggregate to.
        #In practice, merge EM data with aggregation tree.
        df_EM_u = pd.merge(
                df_EM_u, 
                df_agg_tree_comp, 
                left_on=["comp_id"], 
                right_on = ["child_id_comp"], 
                how="left", 
                indicator="exists_agg") #, validate = 'one_to_one'
        df_EM_u["exists_agg"] = np.where(df_EM_u["exists_agg"] == "both", True, False)
        for i in range(len(df_EM_u["exists_agg"])):
            if df_EM_u["exists_agg"].iloc[i] == False:
                check_file.write("Input compound name {} was not found in aggregation tree for compounds.\n".format(df_EM_u["comp_id"].iloc[i]))
        df_EM_u.drop(["child_id_comp", "exists_agg"], axis=1, inplace=True)
        use_col_agg_comp = ["parent_id_comp", "depth_id_comp"]
        
    
    
    if agg_reso:    
        #For each process in EM, find parent process to aggregate to.
        #In practice, merge EM data with aggregation tree.
        df_EM_u = pd.merge(
                df_EM_u, 
                df_agg_tree_reso, 
                left_on=["reso_id"], 
                right_on = ["child_id_reso"], 
                how="left", 
                indicator="exists_agg") #, validate = 'one_to_one'
        df_EM_u["exists_agg"] = np.where(df_EM_u["exists_agg"] == "both", True, False)
        for i in range(len(df_EM_u["exists_agg"])):
            if df_EM_u["exists_agg"].iloc[i] == False:
                check_file.write("Input resource name {} was not found in aggregation tree for resources.\n".format(df_EM_u["reso_id"].iloc[i]))
        df_EM_u.drop(["child_id_reso", "exists_agg"], axis=1, inplace=True)
        use_col_agg_reso = ["parent_id_reso", "depth_id_reso"]
    
    

    #============================================================================
    # COMPUTE UNCERTAINTY PROPAGATION (APPROACH 1)
    #============================================================================ 
    #TODO  20230215: use results from approach 1 as approximate results
    #to guess partition values for simulated values for Monte Carlo,
    #in order to reduce computation time.
    
    df_pr_out_AD_EF = compute_U_propagation_em_pd(df_EM_u)
    
    #Compute uncertainty propagation for the trend
    df_pr_out_AD_EF = compute_U_propagation_trend_pd(df_EM_u, df_pr_out_AD_EF, EM_BY_inventory, EM_RY_inventory)
    
    
    #Aggregate source categories for uncertainty propagation
    #use aggregation function!
    
    #group by process
    for i_y in range(3):
        if i_y == 0:
            y_string = "BY"        
            
        elif i_y == 1:
            y_string = "RY"        
            
        elif i_y == 2:
            y_string = "trend_normed"
    
        col_EM_status = "EM_status_{}".format(y_string)
        col_EM_is_num = "EM_is_num_{}".format(y_string)
        use_cols_main = [col_EM_status, "EM_{}".format(y_string)]
        use_cols_extra = ["EM_{}_pr_contrib_var_lower".format(y_string), "EM_{}_pr_contrib_var_upper".format(y_string)]
        use_cols_for_agg = use_cols_id + use_cols_main + use_col_agg_proc + use_col_agg_comp + use_col_agg_reso
        df_pr_agg = pd.concat([df_EM_u[use_cols_for_agg], df_pr_out_AD_EF[use_cols_extra]], axis = 1)
    
        if agg_proc:
            df_pr_agg = groupby_one_attribute_pd(
                    df = df_pr_agg,
                    df_agg_tree = df_agg_tree_proc,
                    agg_str = "_proc",
                    child_id_left = "proc_id",
                    col_unique_groupby_extra = ["reso_id", "comp_id"],
                    col_EM_status = col_EM_status,
                    )
    
        if agg_comp:
            df_pr_agg = groupby_one_attribute_pd(
                    df = df_pr_agg,
                    df_agg_tree = df_agg_tree_comp,
                    agg_str = "_comp",
                    child_id_left = "comp_id",
                    col_unique_groupby_extra = ["reso_id", "proc_id"],
                    col_EM_status = col_EM_status,
                    )
    
        if agg_reso:
            df_pr_agg = groupby_one_attribute_pd(
                    df = df_pr_agg,
                    df_agg_tree = df_agg_tree_reso,
                    agg_str = "_reso",
                    child_id_left = "reso_id",
                    col_unique_groupby_extra = ["comp_id", "proc_id"],
                    col_EM_status = col_EM_status,
                    )
            
        if i_y == 0:
            #df_pr_out is still completely empty.
            #df_pr_out_len = len(df_pr_agg)
            df_pr_out = pd.DataFrame(
                    np.float(0.0),
                    columns=[
                            #use_cols_id
                            #"proc_id", 
                            #"comp_id", 
                            #"reso_id",
                            
                            #"import",
            
                            #use_cols_main
                            #"EM_BY",
                            #"EM_status_BY",
                            #"EM_is_num_BY",
                            #"unit_BY",
                            #"EM_RY",
                            #"EM_status_RY",
                            #"EM_is_num_RY",
                            #"unit_RY",
                            #"EM_trend_normed",
                            #"EM_status_trend_normed",
                            #"EM_is_num_trend_normed",
                            #"unit_trend_normed",
            
                            #"report", #do not create here otherwise raise ValueError: Cannot use name of an existing column for indicator column
            
                            "EM_BY_pr_U_lower_p",
                            "EM_BY_pr_U_upper_p",
                            "EM_BY_pr_U_mean_p",
                            "EM_RY_pr_U_lower_p",
                            "EM_RY_pr_U_upper_p",
                            "EM_RY_pr_U_mean_p",
                            "EM_trend_normed_pr_U_lower_p",
                            "EM_trend_normed_pr_U_upper_p",
                            "EM_trend_normed_pr_U_mean_p",
    
                            "EM_BY_pr_var_normed",
                            "EM_RY_pr_var_normed",
                            "EM_trend_normed_pr_var_normed",
    
                            ],
                            index=range(len(df_pr_agg)))
    
    
            df_pr_out[use_cols_id] = df_pr_agg[use_cols_id].copy() #cols are: ["proc_id", "comp_id", "reso_id"]
            df_pr_out["import"] = df_EM_u["import"].copy()
            df_pr_out["import"].loc[pd.isnull(df_pr_out["import"])] = False
            
        
        df_pr_out[use_cols_main] = df_pr_agg[use_cols_main].copy()
        df_pr_out[use_cols_extra] = df_pr_agg[use_cols_extra].copy()    
        df_pr_out[col_EM_is_num] = False
        df_pr_out[col_EM_is_num].loc[df_pr_out[col_EM_status] == "ES"] = True
        
        
    
        del df_pr_agg
    
    
    #======================================
    #FIND PROCESSES TO REPORT
    #====================================== 
        
    df_pr_out = pd.merge(
            df_pr_out,
            df_proc_out,
            left_on = dict_io_em["in_col_unique_em"],
            right_on = dict_io_em["in_col_unique_em"],
            how="left", 
            indicator="report",
            #suffixes = ["_agg", "_tree"] 
            )
    
    df_pr_out["report"] = np.where(df_pr_out["report"] == "both", True, False)
    index_input = df_pr_out.index[df_pr_out["import"] == True].tolist()  
    index_output = df_pr_out.index[df_pr_out["report"] == True].tolist()
    if len(index_output) == 0:
        check_file.write("There were no recognised output indexes.")
        check_file.close()
        raise ValueError("There were no recognised output indexes.")
    
    
    #merge with compound nomenclature
    df_pr_out = merge_with_main(
            df = df_pr_out,
            df_main = df_comp,
            merge_with_main_left = ["comp_id"],
            merge_with_main_right = ["comp_id"],
            check_file = check_file,
            )
    #merge with resource nomenclature
    df_pr_out = merge_with_main(
            df = df_pr_out,
            df_main = df_reso,
            merge_with_main_left = ["reso_id"],
            merge_with_main_right = ["reso_id"],
            check_file = check_file,
            )
    #merge with all columns of the process nomenclature
    df_pr_out = pd.merge(
            df_pr_out,
            df_proc,
            left_on = ["proc_id"],
            right_on = ["proc_id"],
            how = "left",
            indicator = "exists_proc"
            )
    
    df_pr_out.sort_values(
            by = ["proc_rank", "proc_name", "reso_rank", "comp_rank"],
            axis = 0, #use axis = 0 to sort rows, use axis =1 to sort columns
            inplace = True,
            #ignore_index = True, #set True to relabel index axis
            )
    df_pr_out.reset_index(inplace = True, drop = True)
    
    #find index for the inventory total, for pr results (uncertainty propagation)
    index_pr_total = find_index_inventory_total(df_pr_out, proc_id_total, comp_id_total, reso_id_total, "pr", check_file)

    #finish uncertainty computations for approach 1, uncertainty propagation: normalisation by inventory total emissions
    for i_y in range(3):
        if i_y == 0:
            y_string = "BY"        
            
        elif i_y == 1:
            y_string = "RY"        
            
        elif i_y == 2:
            y_string = "trend_normed"
        
        df_pr_out = compute_U_propagation_normalisation_pd(df_pr_out, y_string, index_pr_total)    
    
    
    
    
    #============================================================================
    # PREPARE FOR MONTE CARLO SIMULATIONS
    #============================================================================   
    no_nomenc_in = len(df_EM_u)
       
    
    #generate utilitarian values for AD and EF 
    #(they can be considered as computation tools, values in themselves have no meaning,
    #but are used as input in computation steps).
    #This is done so because with the available information so far,
    #uncertainties values for AD and EF are not estimated at the same aggregation level
    #than AD and EF values themselves.
    #Also, because AD and EF are multiplied, and since we know the resulting quantity EM,
    #we can set fake vales for AD and EF, as long as their product equals EM.
    
    #implicitely, all EF are set to a value of one (1).
    
    df_EM_u["uAD_lower_BY"] = df_EM_u["uAD_lower_f_BY"] * df_EM_u["EM_BY"]
    df_EM_u["uAD_upper_BY"] = df_EM_u["uAD_upper_f_BY"] * df_EM_u["EM_BY"] 
    df_EM_u["uAD_lower_RY"] = df_EM_u["uAD_lower_f_RY"] * df_EM_u["EM_RY"]
    df_EM_u["uAD_upper_RY"] = df_EM_u["uAD_upper_f_RY"] * df_EM_u["EM_RY"]
    
    if "uEM_dist" in dict_io_u["in_col_names_u"]:
        df_EM_u["uEM_lower_BY"] = df_EM_u["uEM_lower_f_BY"] * df_EM_u["EM_BY"]
        df_EM_u["uEM_upper_BY"] = df_EM_u["uEM_upper_f_BY"] * df_EM_u["EM_BY"]
        df_EM_u["uEM_lower_RY"] = df_EM_u["uEM_lower_f_RY"] * df_EM_u["EM_RY"]
        df_EM_u["uEM_upper_RY"] = df_EM_u["uEM_upper_f_RY"] * df_EM_u["EM_RY"]
        
    
    #All input uncertainties are now given in absolute values, 
    #not in percent and not in fraction of the mean,
    #and with a coverage factor of one,
    #except for the triangular distribution where this is the edge.
    
    #trend_EM_mc is the trend for a given process, normalised by BY EM from that process.
    #these values cannot be summed up because each is normalised by a specific BY_EM.
    
    #trend_normed_mc is (RY_EM(process) - BY_EM(process)) / BY_EM(inventory),
    #so it is normalised by the sum of BY_EM of the entire inventory.
    #So these values can be summed up because they are nomalised by the same quantity.
        
    
    #***Deal with data correlated between BY and RY********************************
    
    #RY = BY * a + b
    #method 2: uncertainty stays the same in percentage value.
    #use a ratio.
    #advantage: no shift, just scaling, so
    #no risk of creating e.g. negative data that would be impossible for e.g. EF
    EM_BY_isnotzero = df_EM_u["EM_BY"] != np.float64(0.0)
    
    AD_RY_BY_ratio = np.where(EM_BY_isnotzero, df_EM_u["EM_RY"] / df_EM_u["EM_BY"], np.nan) #RY_AD_interm/BY_AD_interm
    #implicitely, EF_RY_BY_ratio is one.
    
    dEM_RY_BY_ratio = np.where((df_EM_u['uEM_is_num_BY'] & EM_BY_isnotzero), df_EM_u['EM_RY']/df_EM_u['EM_BY'], np.nan)
    
    AD_corr_a = AD_RY_BY_ratio
    AD_corr_b = [float(0.0)]*no_nomenc_in
    
    EF_corr_a = [float(1.0)]*no_nomenc_in
    EF_corr_b = [float(0.0)]*no_nomenc_in
    
    EM_corr_a = dEM_RY_BY_ratio
    EM_corr_b = [float(0.0)]*no_nomenc_in
    
    #***End of Deal with data correlated between BY and RY*************************
    
    #https://www.statology.org/pandas-create-dataframe-with-column-names/
    df_mc_out_AD_EF = pd.DataFrame(
            np.float(0.0), #fill all cells with zeros, this is the default result (not nan!)
            columns=[
            "AD_BY_mc_edge_min",
            "AD_BY_mc_edge_max",
            "AD_BY_mc_mean",
            "EF_BY_mc_edge_min",
            "EF_BY_mc_edge_max",
            "EF_BY_mc_mean",
            "AD_RY_mc_edge_min",
            "AD_RY_mc_edge_max",
            "AD_RY_mc_mean",
            "EF_RY_mc_edge_min",
            "EF_RY_mc_edge_max",
            "EF_RY_mc_mean",
            "AD_BY_mc_U_mean_p",
            "AD_BY_mc_U_lower_p",
            "AD_BY_mc_U_upper_p",
            "AD_RY_mc_U_mean_p",
            "AD_RY_mc_U_lower_p",
            "AD_RY_mc_U_upper_p",
            "EF_BY_mc_U_mean_p",
            "EF_BY_mc_U_lower_p",
            "EF_BY_mc_U_upper_p",
            "EF_RY_mc_U_mean_p",
            "EF_RY_mc_U_lower_p",
            "EF_RY_mc_U_upper_p",        
            ],
            index=range(no_nomenc_in))
    
    #============================================================================
    # START MONTE CARLO SIMULATIONS
    #============================================================================    
    print("**********************************************************")
    print("Starting Monte Carlo simulations...")
    
    t0_mc = time.time()  
    
    no_interv = int(np.ceil(const.P_DIST*no_mc)) #number of points that should be part of the confidence interval to get p_dist
    
    #creatre empty variable to store results from mc simulations
    #for sensitivity analysis, we need all generated emission values 
    #for each category (nomenclature code)
    #even if it takes memory to store
    EM_BY_mc = np.zeros((no_nomenc_in, no_mc), dtype = float)
    EM_RY_mc = np.zeros((no_nomenc_in, no_mc), dtype = float)
    
    
    #***Generate random numbers with specific distribution***            
    
    for i_code in range(no_nomenc_in):        
    
        # 20230210 We do not do sensitivity analysis
        #between neither AD and inventory EM
        #nor between EF and inventory EM
        #so we need to store mc results for AD and EF only to compute EM, for each process
        AD_BY_mc = np.zeros((no_mc), dtype = float)
        EF_BY_mc = np.zeros((no_mc), dtype = float)
        AD_RY_mc = np.zeros((no_mc), dtype = float)
        EF_RY_mc = np.zeros((no_mc), dtype = float)
        
    
        #----------------------------------------------------------------------
        #***BASE YEAR EMISSION IS NOT ZERO***
        #----------------------------------------------------------------------
        if df_EM_u['EM_BY'][i_code] != float(0.0):
    
            #***BASE YEAR: UNCERTAINTY GIVEN FOR AD AND EF***        
            if not df_EM_u['uEM_is_num_BY'][i_code]:
            
                #Base year, activity data AD
                AD_BY_mc[:] = generate_random_value(
                        df_EM_u['uAD_dist_BY'][i_code],
                        df_EM_u['EM_BY'][i_code], 
                        df_EM_u["uAD_lower_BY"][i_code], 
                        df_EM_u["uAD_upper_BY"][i_code],
                        no_mc)
    
                #base year, emission factor EF
                EF_BY_mc[:] = generate_random_value(
                        df_EM_u['uEF_dist_BY'][i_code],
                        np.float64(1.0), #BY_EF_interm[i_code],
                        df_EM_u["uEF_lower_f_BY"][i_code],
                        df_EM_u["uEF_upper_f_BY"][i_code],
                        no_mc)
    
                #compute confidence intervals for AD and EF
                df_mc_out_AD_EF["AD_BY_mc_edge_min"].iloc[i_code], df_mc_out_AD_EF["AD_BY_mc_edge_max"].iloc[i_code] = find_interval_np(AD_BY_mc, const.P_DIST)#const.P_DIST) #no_mc, no_interv)
                df_mc_out_AD_EF["EF_BY_mc_edge_min"].iloc[i_code], df_mc_out_AD_EF["EF_BY_mc_edge_max"].iloc[i_code] = find_interval_np(EF_BY_mc, const.P_DIST)#const.P_DIST) #no_mc, no_interv)
                #Store mean value for AD and EF
                df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[i_code] = np.nanmean(AD_BY_mc)
                df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[i_code] = np.nanmean(EF_BY_mc)
            
                EM_BY_mc[i_code, :] = AD_BY_mc * EF_BY_mc
        
            #***BASE YEAR: UNCERTAINTY GIVEN FOR DIRECT EMISSION***        
            else:                             
                EM_BY_mc[i_code, :] = generate_random_value(
                        df_EM_u['uEM_dist_BY'][i_code],
                        df_EM_u['EM_BY'][i_code],
                        df_EM_u["uEM_lower_BY"][i_code],
                        df_EM_u["uEM_upper_BY"][i_code],
                        no_mc)
                
                
        #----------------------------------------------------------------------
        #***REPORTING YEAR EMISSION IS NOT ZERO***
        #----------------------------------------------------------------------
        if df_EM_u['EM_RY'][i_code] != float(0.0): #either no correlation or RY cannot be computed from BY if BY is zero but RY is not zero                                   
    
            #***REPORTING YEAR: UNCERTAINTY GIVEN FOR AD AND EF***        
            if not df_EM_u['uEM_is_num_RY'][i_code]:                    
                #Reporting year, AD
                if df_EM_u['uAD_corr'][i_code] and df_EM_u['EM_BY'][i_code] != float(0.0): #full correlation with AD_BY and AD_BY != 0
                    AD_RY_mc = AD_BY_mc * AD_corr_a[i_code] + AD_corr_b[i_code]                                               
                else:
                    AD_RY_mc[:] = generate_random_value(
                            df_EM_u['uAD_dist_RY'][i_code],
                            df_EM_u['EM_RY'][i_code],
                            df_EM_u["uAD_lower_RY"][i_code],
                            df_EM_u["uAD_upper_RY"][i_code],
                            no_mc)
                                            
                #Reporting year, EF
                if df_EM_u['uEF_corr'][i_code] and df_EM_u['EM_BY'][i_code] != float(0.0): #full correlation with BY
                    #it could be that values are fully correlated but that process started later than BY, for example
                    EF_RY_mc = EF_BY_mc * EF_corr_a[i_code] + EF_corr_b[i_code]    
                else:
                    EF_RY_mc[:] = generate_random_value(
                            df_EM_u['uEF_dist_RY'][i_code],
                            np.float64(1.0), #RY_EF_interm[i_code],
                            df_EM_u["uEF_lower_f_RY"][i_code],
                            df_EM_u["uEF_upper_f_RY"][i_code],
                            no_mc)
    
                #compute confidence intervals for AD and EF
                df_mc_out_AD_EF["AD_RY_mc_edge_min"].iloc[i_code], df_mc_out_AD_EF["AD_RY_mc_edge_max"].iloc[i_code] = find_interval_np(AD_RY_mc, const.P_DIST) #const.P_DIST) #no_mc, no_interv) 
                df_mc_out_AD_EF["EF_RY_mc_edge_min"].iloc[i_code], df_mc_out_AD_EF["EF_RY_mc_edge_max"].iloc[i_code] = find_interval_np(EF_RY_mc, const.P_DIST) #const.P_DIST) #no_mc, no_interv)
                #Store mean value for AD and EF
                df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[i_code] = np.nanmean(AD_RY_mc)
                df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[i_code] = np.nanmean(EF_RY_mc)
    
                EM_RY_mc[i_code, :] = AD_RY_mc * EF_RY_mc
    
            #***REPORTING YEAR: UNCERTAINTY GIVEN FOR DIRECT EMISSION***                                              
            else:
                if df_EM_u['uEM_corr'][i_code] and df_EM_u['EM_BY'][i_code] != float(0.0): #full correlation with BY
                    EM_RY_mc[i_code, :] = EM_BY_mc[i_code, :]* EM_corr_a[i_code] + EM_corr_b[i_code]    
                else:
                    EM_RY_mc[i_code, :] = generate_random_value(
                            df_EM_u['uEM_dist_RY'][i_code],
                            df_EM_u['EM_RY'][i_code],
                            df_EM_u["uEM_lower_RY"][i_code],
                            df_EM_u["uEM_upper_RY"][i_code],
                            no_mc)
    
        #implicitely, else are emissions zero.
        #Do not assign nan to emissions otherwise 
        #contribution to inventory trend cannot be computed.
    
    #delete a few unecessary variables to save some memory space
    del AD_BY_mc
    del AD_RY_mc
    del EF_BY_mc
    del EF_RY_mc
            
    
    print("Monte Carlo simulations completed.")
    check_file.write("Run time for Monte Carlo simulations: " + str(time.time() - t0_mc) + " seconds\n")   
    print("Run time for Monte Carlo simulations: " + str(time.time() - t0_mc) + " seconds")   
    
    #t0_compute_results_mc = time.time()            
    #***Compute results***
    
    #Finish all computations for AD and EF
    
    #Compute uncertainty in percent for AD and EF
    #for the mean uncertainty, use the interval between min and max
    indexes_nonzero = df_mc_out_AD_EF.index[df_mc_out_AD_EF["AD_BY_mc_mean"]!=0].tolist()
    df_mc_out_AD_EF["AD_BY_mc_U_mean_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_BY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_BY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0) / np.float(2.0)
    df_mc_out_AD_EF["AD_BY_mc_U_lower_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_BY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    df_mc_out_AD_EF["AD_BY_mc_U_upper_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_BY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    
    indexes_nonzero = df_mc_out_AD_EF.index[df_mc_out_AD_EF["AD_RY_mc_mean"]!=0].tolist()
    df_mc_out_AD_EF["AD_RY_mc_U_mean_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_RY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_RY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0) / np.float(2.0)
    df_mc_out_AD_EF["AD_RY_mc_U_lower_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_RY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    df_mc_out_AD_EF["AD_RY_mc_U_upper_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["AD_RY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["AD_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    
    indexes_nonzero = df_mc_out_AD_EF.index[df_mc_out_AD_EF["EF_BY_mc_mean"]!=0].tolist()
    df_mc_out_AD_EF["EF_BY_mc_U_mean_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_BY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_BY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0) / np.float(2.0)
    df_mc_out_AD_EF["EF_BY_mc_U_lower_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_BY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    df_mc_out_AD_EF["EF_BY_mc_U_upper_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_BY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_BY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    
    indexes_nonzero = df_mc_out_AD_EF.index[df_mc_out_AD_EF["EF_RY_mc_mean"]!=0].tolist()
    df_mc_out_AD_EF["EF_RY_mc_U_mean_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_RY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_RY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0) / np.float(2.0)
    df_mc_out_AD_EF["EF_RY_mc_U_lower_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_RY_mc_edge_min"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    df_mc_out_AD_EF["EF_RY_mc_U_upper_p"].iloc[indexes_nonzero] = abs((df_mc_out_AD_EF["EF_RY_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[indexes_nonzero]) / df_mc_out_AD_EF["EF_RY_mc_mean"].iloc[indexes_nonzero]) * np.float(100.0)
    
                    
    #numpy data structure used
    np_axis_mc = 1
    np_axis_process = 0
    
    #=============================================================
    # PLOT DISTRIBUTION OF DATA FOR INVENTORY: BY, RY, TREND
    #=============================================================
    
    #Compute sum of emissions 
    #(aggregation over all {code, compound, resource})
    #Sum of emissions for the inventory, over all input rows, for each mc simulation
    #implicitely, all the input rows together makes the sum of the inventory.
    EM_BY_mc_inventory = np.nansum(EM_BY_mc, axis = np_axis_process) #has 1 dimension and lenght of np_axis_mc
    EM_RY_mc_inventory = np.nansum(EM_RY_mc, axis = np_axis_process) #has 1 dimension and lenght of np_axis_mc
    EM_BY_mc_inventory_mean = np.nanmean(EM_BY_mc_inventory)
    EM_RY_mc_inventory_mean = np.nanmean(EM_RY_mc_inventory)
    EM_BY_mc_inventory_stddev = np.nanstd(EM_BY_mc_inventory)
    EM_RY_mc_inventory_stddev = np.nanstd(EM_RY_mc_inventory)
    
    
    #************************trend**************************************
    
    trend_normed_mc = np.empty((no_nomenc_in, no_mc), dtype = float)
    #Compute trend for each row, normalised by simulations of inventory sum for BY
    #The sum of the rows from the normalised trend gives the trend of the inventory sum!
    for i_code in range(no_nomenc_in):
        trend_normed_mc[i_code, :] = np.where(
                EM_BY_mc_inventory != np.float64(0.0), 
                (EM_RY_mc[i_code, :]-EM_BY_mc[i_code, :])/EM_BY_mc_inventory*np.float64(100.0), 
                np.nan)
        
    #trend for the inventory, for each mc simulation
    EM_trend_mc_inventory = np.where(EM_BY_mc_inventory!= float(0), (EM_RY_mc_inventory-EM_BY_mc_inventory)/EM_BY_mc_inventory * float(100.0), np.nan)
    EM_trend_mc_inventory_mean = np.nanmean(EM_trend_mc_inventory)
    EM_trend_mc_inventory_stddev = np.nanstd(EM_trend_mc_inventory)
    
    
    t0_plot_dist = time.time()   
    if plot_mode:
        if routine == const.ROUTINE_IIR:
            gas_label = df_EM_RY["comp_id"].iloc[0]
            gas_label_latex = df_comp["comp_name_latex"].loc[df_comp["comp_id"] == gas_label].iloc[0]
            unit_string_plot = const.IIR_UNIT_STRING
            
        else:
            gas_label = "GHGs"
            gas_label_latex = "GHGs"
            unit_string_plot = const.NID_UNIT_STRING
            
        plot_distributions_EM_trend(
                EM_BY_mc_inventory_mean, 
                EM_BY_mc_inventory_stddev, 
                EM_BY_mc_inventory,
                EM_RY_mc_inventory_mean, 
                EM_RY_mc_inventory_stddev, 
                EM_RY_mc_inventory,
                EM_trend_mc_inventory_mean,
                EM_trend_mc_inventory_stddev,
                EM_trend_mc_inventory,
                gas_label,
                gas_label_latex,
                BY_string,
                RY_string,
                unit_string_plot,
                dict_io_out["figname_out_mc_distribution"],#dict_io_out["output_foldername"]
                )
    
    t1_plot_dist = time.time() - t0_plot_dist
    check_file.write("Run time for plotting distributions: " + str(t1_plot_dist) + " seconds\n")  
    print("Run time for plotting distributions: " + str(t1_plot_dist) + " seconds")  
    
    
    
    #=============================================
    # AGGREGATE MC-SIMULATED EMISSIONS ACCORDING TO PROCESSES
    #=============================================
    #To save memory space, do aggregation of each df separately: 
    #one for BY, one for RY, one for trend.
    
    
    t_compute_interval = float(0.0)
    t_agg = 0
    
    for i_y in range(3):
        if i_y == 0:
            y_string = "BY"
            sensitivity_ref = EM_BY_mc_inventory #reference variable to compute sensitivity
            col_EM_status = "EM_status_{}".format(y_string)
            col_EM_is_num = "EM_is_num_{}".format(y_string)
            use_cols_y = [col_EM_status, "EM_{}".format(y_string)]
            use_cols_for_agg = use_cols_id + use_cols_y + use_col_agg_proc + use_col_agg_comp + use_col_agg_reso
            df_EM_u_mc = pd.concat([df_EM_u[use_cols_for_agg], pd.DataFrame(data = EM_BY_mc)], axis = 1)
            
        elif i_y == 1:
            y_string = "RY"
            sensitivity_ref = EM_RY_mc_inventory
            col_EM_status = "EM_status_{}".format(y_string)
            col_EM_is_num = "EM_is_num_{}".format(y_string)
            use_cols_y = [col_EM_status, "EM_{}".format(y_string)]
            use_cols_for_agg = use_cols_id + use_cols_y + use_col_agg_proc + use_col_agg_comp + use_col_agg_reso
            df_EM_u_mc = pd.concat([df_EM_u[use_cols_for_agg], pd.DataFrame(data = EM_RY_mc)], axis = 1)
            
        elif i_y == 2:
            y_string = "trend_normed"
            sensitivity_ref = EM_trend_mc_inventory
            col_EM_status = "EM_status_{}".format(y_string)
            col_EM_is_num = "EM_is_num_{}".format(y_string)
            use_cols_y = [col_EM_status, "EM_{}".format(y_string)]
            use_cols_for_agg = use_cols_id + use_cols_y + use_col_agg_proc + use_col_agg_comp + use_col_agg_reso
            df_EM_u_mc = pd.concat([df_EM_u[use_cols_for_agg], pd.DataFrame(data = trend_normed_mc)], axis = 1)
    
        start_column_mc = len(use_cols_for_agg)    
        stop_column_mc = df_EM_u_mc.shape[1]
        
        #DOES NOT work:
        #compute confidence intervals here? make sense only if intermediate agg can be trown away, which is not the case so far.
    
    
        t0_agg = time.time()
        
        for i_agg_type in range(3):
            if i_agg_type == 0:
                agg_type = agg_proc
                agg_str = "_proc"
                agg_str_long = "process"
                child_id_left = "proc_id"
                col_unique_groupby_extra = ["reso_id", "comp_id"]
                      
            elif i_agg_type == 1:
                agg_type = agg_comp
                agg_str = "_comp"
                agg_str_long = "compound"
                child_id_left = "comp_id"
                col_unique_groupby_extra = ["proc_id", "reso_id"]
                
            elif i_agg_type == 2:
                agg_type = agg_reso
                agg_str = "_reso"
                agg_str_long = "resource"
                child_id_left = "reso_id"
                col_unique_groupby_extra = ["proc_id", "comp_id"]
                
            if agg_type:
                print("Starting aggregation by {}.".format(agg_str_long))
        
                depth_id = "depth_id{}".format(agg_str)
                parent_id = "parent_id{}".format(agg_str)
                child_id = "child_id{}".format(agg_str)
                parent_id_tree = "parent_id{}_tree".format(agg_str)
                child_id_tree = "child_id{}_tree".format(agg_str)
                parent_id_agg = "parent_id{}_agg".format(agg_str)
                
                if i_agg_type == 0:
                    df_agg_tree = df_agg_tree_proc
                elif i_agg_type == 1:
                    df_agg_tree = df_agg_tree_comp
                elif i_agg_type == 2:
                    df_agg_tree = df_agg_tree_reso
        
        
                #this is working
                df_test = pd.merge(
                        df_EM_u_mc[[child_id_left]],
                        df_agg_tree,
                        left_on=[child_id_left], 
                        right_on = [child_id], 
                        how="left", 
                        indicator="exists_agg")
                        
                #https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html#merging-together-values-within-series-or-dataframe-columns
                df_EM_u_mc[depth_id] = df_test[depth_id].copy()
                df_EM_u_mc[parent_id] = df_test[parent_id].copy()        
    
                agg_max_depth = np.int(np.max(df_EM_u_mc[depth_id]))
                print(y_string + " group by: " + str([parent_id] + col_unique_groupby_extra + [depth_id]))
                    
                for i_depth in range(agg_max_depth, 0, -1):
                    #aggregate only to one level above
                    print("mc, i_depth: " + str(i_depth))
                    
            
                    df_agg_mc = df_EM_u_mc.loc[df_EM_u_mc[depth_id] == i_depth].groupby(
                            by = [parent_id] + col_unique_groupby_extra + [depth_id]).sum().reset_index()
    
                    
                    #TODO  20230216 The next loop is very slow. 
                    #Find a better way using .agg
                    df_agg_mc[col_EM_status] = "ES"
                    #df_agg_mc["EM_is_num_BY"] = True
                    for i in range(len(df_agg_mc)):
                        status_list = pd.unique(df_EM_u_mc[col_EM_status].loc[
                                (df_EM_u_mc[col_unique_groupby_extra[0]] == df_agg_mc[col_unique_groupby_extra[0]].iloc[i])
                                & (df_EM_u_mc[col_unique_groupby_extra[1]] == df_agg_mc[col_unique_groupby_extra[1]].iloc[i])
                                & (df_EM_u_mc[parent_id] == df_agg_mc[parent_id].iloc[i])
                                ]).tolist()
                        if len(status_list) == 1:
                            df_agg_mc[col_EM_status].iloc[i] = status_list[0]
    
                    #Update depth_id of resulting rows: one level up.
                    df_agg_mc[depth_id] -= 1
                    df_agg_mc[child_id_left] = df_agg_mc[parent_id].copy()
                    #df_agg_mc["import"] = False
                                
                    df_agg_mc = pd.merge(
                            df_agg_mc, 
                            df_agg_tree, 
                            left_on=[parent_id, depth_id], 
                            right_on = [child_id, depth_id], 
                            how="left", 
                            indicator="exists_agg",
                            suffixes = ["_agg", "_tree"] #suffixes = ['_agg', None] #does not work!!!
                            ).rename(columns = {parent_id_tree: parent_id, child_id_tree: child_id}) #suffixes = [None, "_tree"]
                    df_agg_mc["exists_agg"] = np.where(df_agg_mc["exists_agg"] == "both", True, False)
                    #drop redundant columns
                    df_agg_mc.drop([parent_id_agg, child_id], axis=1, inplace=True) #, "exists_agg"
                
                    #Technical aspect: drop this column resulting from the merge
                    #because it will be added with the next merge with the aggregation tree
                    df_agg_mc.drop(["exists_agg"], axis=1, inplace=True) #,     
                    
                    
                    #Concatenate the aggregated rows with the original DataFrame, to get all results into one DataFrame
                    #TODO  20230217: think abut a less memory-intensive method.
                    #The problem is, such intermediate results are needed for subsequent aggregations.
                    df_EM_u_mc = pd.concat([df_EM_u_mc, df_agg_mc], axis =0, ignore_index=True)
    
    
                print("Aggregation by {} completed.".format(agg_str_long))
                t_agg = t_agg + time.time() - t0_agg
            
        del df_agg_mc
        
        if i_y == 0:
            #df_mc_out is still completely empty.
            df_mc_out_len = len(df_EM_u_mc)
            df_mc_out = pd.DataFrame(
                    np.float(0.0),
                    columns=[
                            #use_cols_id
                            #"proc_id", 
                            #"comp_id", 
                            #"reso_id",
                            
                            #"import",
            
                            #use_cols_y
                            #"EM_BY",
                            #"EM_status_BY",
                            #"EM_is_num_BY",
                            #"unit_BY",
                            #"EM_RY",
                            #"EM_status_RY",
                            #"EM_is_num_RY",
                            #"unit_RY",
                            #"EM_trend_normed",
                            #"EM_status_trend_normed",
                            #"EM_is_num_trend_normed",
                            #"unit_trend_normed",
            
                            #"report", #do not create here otherwise raise ValueError: Cannot use name of an existing column for indicator column
            
                            "EM_BY_mc_edge_min",
                            "EM_BY_mc_edge_max",
                            "EM_BY_mc_mean",
                            "EM_RY_mc_edge_min",
                            "EM_RY_mc_edge_max",
                            "EM_RY_mc_mean",
                            "EM_trend_normed_mc_edge_min",
                            "EM_trend_normed_mc_edge_max",
                            "EM_trend_normed_mc_mean",                
            
                            "EM_BY_mc_U_lower_p",
                            "EM_BY_mc_U_upper_p",
                            "EM_BY_mc_U_mean_p",
                            "EM_RY_mc_U_lower_p",
                            "EM_RY_mc_U_upper_p",
                            "EM_RY_mc_U_mean_p",
                            "EM_trend_normed_mc_U_lower_p",
                            "EM_trend_normed_mc_U_upper_p",
                            "EM_trend_normed_mc_U_mean_p",
            
                            "EM_BY_mc_2stddev_p",
                            "EM_RY_mc_2stddev_p",
                            "EM_trend_normed_mc_2stddev_p",
                            
                            "EM_BY_mc_sensitivity", #sensitivity of source category emission to inventory emission for BY
                            "EM_RY_mc_sensitivity", #sensitivity of source category emission to inventory emission for RY
                            "EM_trend_normed_mc_sensitivity", #sensitivity of source category normalised trend to inventory trend
                            #"EM_BY_RY_mc_sensitivity", #sensitivity of RY emission to BY emission: cannot be computed in this version.    
                            "EM_BY_mc_var",
                            "EM_RY_mc_var",
                            "EM_trend_normed_mc_var",
                            "EM_BY_mc_var_normed",     
                            "EM_RY_mc_var_normed",
                            "EM_trend_normed_mc_var_normed",             
                            ],
                            index=range(len(df_EM_u_mc)))
    
    
            df_mc_out[use_cols_id] = df_EM_u_mc[use_cols_id].copy()
            df_mc_out["import"] = df_EM_u["import"].copy()
            df_mc_out["import"].loc[pd.isnull(df_mc_out["import"])] = False
            
        
        df_mc_out[use_cols_y] = df_EM_u_mc[use_cols_y].copy()    
        df_mc_out[col_EM_is_num] = False
        df_mc_out[col_EM_is_num].loc[df_mc_out[col_EM_status] == "ES"] = True
    
        df_mc_out["EM_{}_mc_mean".format(y_string)] = np.nanmean(df_EM_u_mc.iloc[:, start_column_mc:stop_column_mc], axis = np_axis_mc)
        df_mc_out["EM_{}_mc_var".format(y_string)] = np.nanvar(df_EM_u_mc.iloc[:, start_column_mc:stop_column_mc], axis = np_axis_mc)
        df_mc_out["EM_{}_mc_2stddev_p".format(y_string)] = np.sqrt(df_mc_out["EM_{}_mc_var".format(y_string)])/df_mc_out["EM_{}_mc_mean".format(y_string)] * np.float(200.0) #2 times the standard deviation, needed to use as input for next mc simulation for indirect emissions.
    
    
        print("Now computing confidence intervals for {}.".format(y_string))
    
        #---------------------------------------------------------------------
        # FIND NARROWEST INTERVAL CONTAINING CHOSEN INTERVAL E.G. 95%
        #---------------------------------------------------------------------    
        
        t0_compute_interval = time.time()
        
        for i in range(df_mc_out_len):
            if df_EM_u_mc["EM_{}".format(y_string)].iloc[i] != np.float(0.0):
                df_slice = df_EM_u_mc.iloc[i, start_column_mc:stop_column_mc].copy().values
                np_slice = np.array([val for val in df_slice])
                
        
                #TODO  20230113 the line above is absolutely not optimal but I could not find a better way so far.
                #other options require a more up-to-date version of pandas.
                #df_slice = df_slice.to_numpy() #only for pandas >= 0.24.1        
                #print(np_slice.dtype)       
                #df_slice = np.array(df_slice) #does not work        
                #print(df_slice.dtype)        
                #pd.isnull(df_slice)
                #np.isnan(np_slice)
                
                df_mc_out["EM_{}_mc_edge_min".format(y_string)].iloc[i], df_mc_out["EM_{}_mc_edge_max".format(y_string)].iloc[i] = find_interval_np(np_slice, const.P_DIST)       
    
    
                #===========================================================================
                # MC: SENSITIVITY ANALYSIS
                #===========================================================================
                #what equation?
                #in Table 3.3 Chap 3 IPCC, Column H is "contribution to variance"
                #Report the ‘contribution to uncertainty’. It is estimated dividing the variance of each category by
                #the total variance of the inventory (var(x)/sum(var(x[i]))).
                #but is this really an appropriate and suitable method?
                #yes because a sum is a linear process so uncertainty propagation is ok.
                   
                
                #*************************    
                #Other method: covariance between each input source and the sum.
                #sensitivity = cov(x,y)/sqrt(var(x)*var(y)) #note: this is np.corrcoef
                #but for that we need to keep all generated input values in memory, from each source
                
                #Use this sensitivity for tornado plot.
                df_mc_out["EM_{}_mc_sensitivity".format(y_string)].iloc[i] = np.corrcoef(np_slice, sensitivity_ref)[0,1]
            
                #Alternative pandas method
                #pd_series_slice = df_EM_u_BY_mc.iloc[i, start_column_mc:stop_column_mc].squeeze()    
                #df_mc_out["EM_BY_mc_edge_min"].iloc[i], df_mc_out["EM_BY_mc_edge_max"].iloc[i] = find_interval_pd(pd_series_slice, const.P_DIST)       
                #df_mc_out["EM_BY_mc_sensitivity"].iloc[i] = pd_series_slice.corrwith(other = pd.Series(EM_BY_mc_inventory), method = 'pearson')
        
            #compute sensitivity between base year and reporting year
            #TODO This would be nice to have but cannot be compute since the mc simulations are deleted after each loop, to save memory
            #if df_EM_u_BY_mc['EM_BY'].iloc[i] != np.float(0.0) and df_EM_u_RY_mc['EM_RY'].iloc[i] != np.float(0.0):           
            #    df_mc_out["EM_BY_RY_mc_sensitivity"].iloc[i] = np.corrcoef(np_slice_BY, np_slice_RY)[0,1]
    
        t_compute_interval = t_compute_interval + time.time() - t0_compute_interval
    
        indexes_nonzero = df_mc_out.index[((df_mc_out["EM_{}_mc_mean".format(y_string)]!=0) & (pd.isnull(df_mc_out["EM_{}_mc_mean".format(y_string)]) == False))].tolist()
        if i_y == 0 or i_y == 1:
            #Computation for BY and RY
            #For the mean uncertainty, do not foget to divide by 2!
            df_mc_out["EM_{}_mc_U_mean_p".format(y_string)].iloc[indexes_nonzero] = abs((df_mc_out["EM_{}_mc_edge_max".format(y_string)].iloc[indexes_nonzero] - df_mc_out["EM_{}_mc_edge_min".format(y_string)].iloc[indexes_nonzero]) / np.float(2.0) / df_mc_out["EM_{}_mc_mean".format(y_string)].iloc[indexes_nonzero]) * np.float(100.0)
            df_mc_out["EM_{}_mc_U_lower_p".format(y_string)].iloc[indexes_nonzero] = abs((df_mc_out["EM_{}_mc_mean".format(y_string)].iloc[indexes_nonzero] - df_mc_out["EM_{}_mc_edge_min".format(y_string)].iloc[indexes_nonzero]) / df_mc_out["EM_{}_mc_mean".format(y_string)].iloc[indexes_nonzero]) * np.float(100.0)
            df_mc_out["EM_{}_mc_U_upper_p".format(y_string)].iloc[indexes_nonzero] = abs((df_mc_out["EM_{}_mc_edge_max".format(y_string)].iloc[indexes_nonzero] - df_mc_out["EM_{}_mc_mean".format(y_string)].iloc[indexes_nonzero]) / df_mc_out["EM_{}_mc_mean".format(y_string)].iloc[indexes_nonzero]) * np.float(100.0)
        elif i_y == 2:
            #special computation for the trend! 
            #Do not divide by trend_normed_mc_mean and do not multiply by 100!
            #For the mean uncertainty, do not forget to divide by 2!
            df_mc_out["EM_trend_normed_mc_U_mean_p"].iloc[indexes_nonzero]  = abs(df_mc_out["EM_trend_normed_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out["EM_trend_normed_mc_edge_min"].iloc[indexes_nonzero]) / np.float(2.0)
            df_mc_out["EM_trend_normed_mc_U_lower_p"].iloc[indexes_nonzero] = abs(df_mc_out["EM_trend_normed_mc_mean"].iloc[indexes_nonzero] - df_mc_out["EM_trend_normed_mc_edge_min"].iloc[indexes_nonzero])
            df_mc_out["EM_trend_normed_mc_U_upper_p"].iloc[indexes_nonzero] = abs(df_mc_out["EM_trend_normed_mc_edge_max"].iloc[indexes_nonzero] - df_mc_out["EM_trend_normed_mc_mean"].iloc[indexes_nonzero])
              
            
        #Delete variables to save memory space
        del df_EM_u_mc
        del df_slice
        del np_slice
        if i_y == 0:
            del EM_BY_mc
            del sensitivity_ref
            del EM_BY_mc_inventory
        elif i_y == 1:
            del EM_RY_mc
            del sensitivity_ref
            del EM_RY_mc_inventory
        elif i_y == 2:
            del trend_normed_mc
            del sensitivity_ref
            del EM_trend_mc_inventory
    
    
    check_file.write("Run time for aggregations: " + str(t_agg) + " seconds\n")  
    print("Run time for aggregations: " + str(t_agg) + " seconds")  
    
    
    
    check_file.write("Run time for computing confidence interval: " + str(t_compute_interval) + " seconds\n")  
    print("Run time for computing confidence interval: " + str(t_compute_interval) + " seconds")  
    
    
    
    #=============================================================================
    # quality control: compare input mean and mc mean for each process
    #=============================================================================
    indexes = df_mc_out.index[(df_mc_out["EM_BY"] != np.float(0.0)) & df_mc_out["import"]].tolist()
    BY_EM_mean_offset = np.nanstd((df_mc_out["EM_BY_mc_mean"].iloc[indexes] - df_mc_out['EM_BY'].iloc[indexes])/df_mc_out['EM_BY'].iloc[indexes]*float(100.0))
    RY_EM_mean_offset = np.nanstd((df_mc_out["EM_RY_mc_mean"].iloc[indexes] - df_mc_out['EM_RY'].iloc[indexes])/df_mc_out['EM_RY'].iloc[indexes]*float(100.0))
    
    check_file.write("Mean offset in percent between BY mean and Monte Carlo simulated mean: {}.\n".format(BY_EM_mean_offset))
    check_file.write("Mean offset in percent between RY mean and Monte Carlo simulated mean: {}.\n".format(RY_EM_mean_offset))
    #=============================================================================
    
    
    #======================================
    #FIND PROCESSES TO REPORT
    #====================================== 
        
    df_mc_out = pd.merge(
            df_mc_out,
            df_proc_out,
            left_on = dict_io_em["in_col_unique_em"],
            right_on = dict_io_em["in_col_unique_em"],
            how="left", 
            indicator="report",
            #suffixes = ["_agg", "_tree"] 
            )
    
    df_mc_out["report"] = np.where(df_mc_out["report"] == "both", True, False)
    index_input = df_mc_out.index[df_mc_out["import"] == True].tolist()  
    index_output = df_mc_out.index[df_mc_out["report"] == True].tolist()
    if len(index_output) == 0:
        check_file.write("There were no recognised output indexes.")
        check_file.close()
        raise ValueError("There were no recognised output indexes.")
    
    
    #merge with compound nomenclature
    df_mc_out = merge_with_main(
            df = df_mc_out,
            df_main = df_comp,
            merge_with_main_left = ["comp_id"],
            merge_with_main_right = ["comp_id"],
            check_file = check_file,
            )
    #merge with resource nomenclature
    df_mc_out = merge_with_main(
            df = df_mc_out,
            df_main = df_reso,
            merge_with_main_left = ["reso_id"],
            merge_with_main_right = ["reso_id"],
            check_file = check_file,
            )
    #merge with all columns of the process nomenclature
    df_mc_out = pd.merge(
            df_mc_out,
            df_proc,
            left_on = ["proc_id"],
            right_on = ["proc_id"],
            how = "left",
            indicator = "exists_proc"
            )
    
    #get normalised values so that sum of reported values is one
    #Emission contribution to variance, reporting column H
    df_mc_out["EM_BY_mc_var_normed"].iloc[index_output] = df_mc_out["EM_BY_mc_var"].iloc[index_output]/ np.nansum(df_mc_out["EM_BY_mc_var"].iloc[index_output])
    df_mc_out["EM_RY_mc_var_normed"].iloc[index_output] = df_mc_out["EM_RY_mc_var"].iloc[index_output]/ np.nansum(df_mc_out["EM_RY_mc_var"].iloc[index_output])
    df_mc_out["EM_trend_normed_mc_var_normed"].iloc[index_output] = df_mc_out["EM_trend_normed_mc_var"].iloc[index_output]/ np.nansum(df_mc_out["EM_trend_normed_mc_var"].iloc[index_output])
    
    
    #======================================================================
    # PLOT TORNADO PLOT FOR SELECTED OUTPUT PROCESSES, COMPOUNDS, RESOURCES
    #======================================================================    
    t0_tornado_plots = time.time()
    
    if plot_mode:
        if routine == const.ROUTINE_IIR:      
            gas_label_latex_tornado = df_comp["comp_name_latex"].loc[df_comp["comp_id"] == gas_label].iloc[0]
            nomenc_code_tornado = df_mc_out["proc_code"]            
            
        else:      
            gas_label_latex_tornado = None
            nomenc_code_tornado = [
                    df_mc_out['proc_code'].iloc[i] + "; " + df_mc_out['comp_name_latex'].iloc[i]
                    if (df_mc_out['reso_id'].iloc[i] == "Total" or df_mc_out['reso_id'].iloc[i] == "All resources")
                    else df_mc_out['proc_code'].iloc[i] + "; " + df_mc_out['reso_id'].iloc[i] + "; " + df_mc_out['comp_name_latex'].iloc[i]
                    for i in range(df_mc_out_len)]            
    
        tornado_plot_EM_BY_RY(
                [nomenc_code_tornado[index] for index in index_input],
                np.array([val for val in df_mc_out["EM_BY_mc_sensitivity"].iloc[index_input]]),
                np.array([val for val in df_mc_out["EM_RY_mc_sensitivity"].iloc[index_input]]),
                BY_string, 
                RY_string, 
                gas_label_latex_tornado, 
                dict_io_out["figname_out_mc_tornado"] + "_input_index.png")
    
        tornado_plot_EM_BY_RY(
                [nomenc_code_tornado[index] for index in index_output],
                np.array([val for val in df_mc_out["EM_BY_mc_sensitivity"].iloc[index_output]]), #sensitivity_EM_BY_nomenc_code, 
                np.array([val for val in df_mc_out["EM_RY_mc_sensitivity"].iloc[index_output]]), #sensitivity_EM_RY_nomenc_code, 
                BY_string, 
                RY_string, 
                gas_label_latex_tornado, 
                dict_io_out["figname_out_mc_tornado"] + "_output_index.png")
    
    t1_tornado_plots = time.time() - t0_tornado_plots
    check_file.write("Run time for tornado plots: " + str(t1_tornado_plots) + " seconds\n")  
    
    #======================================================================
    # TODO: WRITE OUTPUT FILE WITH INPUT PROCESSES FOR QA/QC
    #======================================================================
    
    
    #======================================================================
    # WRITE OUTPUT FILE WITH OUTPUT PROCESSES FOR REPORTING
    #======================================================================
    
    df_mc_out.sort_values(
            by = ["proc_rank", "proc_name", "reso_rank", "comp_rank"],
            axis = 0, #use axis = 0 to sort rows, use axis =1 to sort columns
            inplace = True,
            #ignore_index = True, #set True to relabel index axis
            )
    df_mc_out.reset_index(inplace = True, drop = True)
    #df_mc_out.reset_index(drop = True) #does nothing!
    
    
    #find index for the inventory total, for mc results (Monte Carlo simulations)
    index_mc_total = find_index_inventory_total(df_mc_out, proc_id_total, comp_id_total, reso_id_total, "mc", check_file)
    


    
    
    #find indexes for the sums for each sector
    index_mc_proc_sector_total = df_mc_out.index[((df_mc_out["proc_code"].isin(const.PROC_CODE_SECTOR_TOTAL)) & (df_mc_out["comp_id"] == comp_id_total) & (df_mc_out["reso_id"] == reso_id_total) )].tolist()
    if len(index_mc_proc_sector_total) == 0:
        check_file.write("Could not find the sectorial totals in mc results!")
        check_file.close()
        raise ValueError("Could not find the sectorial totals in mc results!")
    
    index_pr_proc_sector_total = df_pr_out.index[((df_pr_out["proc_code"].isin(const.PROC_CODE_SECTOR_TOTAL)) & (df_pr_out["comp_id"] == comp_id_total) & (df_pr_out["reso_id"] == reso_id_total) )].tolist()
    if len(index_pr_proc_sector_total) == 0:
        check_file.write("Could not find the sectorial totals in pr results!")
        check_file.close()
        raise ValueError("Could not find the sectorial totals in pr results!")
       
    #compute variance for each category/compound, normalised by sum of input variances
    df_mc_out["EM_BY_mc_var_normed"].iloc[index_mc_proc_sector_total] = df_mc_out["EM_BY_mc_var"].iloc[index_mc_proc_sector_total]/ np.nansum(df_mc_out["EM_BY_mc_var"].iloc[index_mc_proc_sector_total])
    df_mc_out["EM_RY_mc_var_normed"].iloc[index_mc_proc_sector_total] = df_mc_out["EM_RY_mc_var"].iloc[index_mc_proc_sector_total]/ np.nansum(df_mc_out["EM_RY_mc_var"].iloc[index_mc_proc_sector_total])
    df_mc_out["EM_trend_normed_mc_var_normed"].iloc[index_mc_proc_sector_total] = df_mc_out["EM_trend_normed_mc_var"].iloc[index_mc_proc_sector_total]/ np.nansum(df_mc_out["EM_trend_normed_mc_var"].iloc[index_mc_proc_sector_total])
    
    df_pr_out["EM_BY_pr_var_normed"].iloc[index_pr_proc_sector_total] = df_pr_out["EM_BY_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total]/ np.nansum(df_pr_out["EM_BY_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total])
    df_pr_out["EM_RY_pr_var_normed"].iloc[index_pr_proc_sector_total] = df_pr_out["EM_RY_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total]/ np.nansum(df_pr_out["EM_RY_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total])
    df_pr_out["EM_trend_normed_pr_var_normed"].iloc[index_pr_proc_sector_total] = df_pr_out["EM_trend_normed_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total]/ np.nansum(df_pr_out["EM_trend_normed_pr_contrib_var_mean"].iloc[index_pr_proc_sector_total])
    
    
    if routine == const.ROUTINE_NID:
    
        #**************For mc results*******************************
        #find indexes for the sums for each compound
        index_mc_comp_total = df_mc_out.index[((df_mc_out["proc_id"] == proc_id_total) & (df_mc_out["comp_id"].isin(comp_total)) & (df_mc_out["reso_id"] == reso_id_total) )].tolist() 
        if len(index_mc_comp_total) == 0:
            check_file.write("Could not find the total per compound in mc results!")
            check_file.close()
            raise ValueError("Could not find the total per compound in mc results!")
        #compute variance for each category/compound, normalised by sum of input variances
        df_mc_out["EM_BY_mc_var_normed"].iloc[index_mc_comp_total] = df_mc_out["EM_BY_mc_var"].iloc[index_mc_comp_total]/ np.nansum(df_mc_out["EM_BY_mc_var"].iloc[index_mc_comp_total])
        df_mc_out["EM_RY_mc_var_normed"].iloc[index_mc_comp_total] = df_mc_out["EM_RY_mc_var"].iloc[index_mc_comp_total]/ np.nansum(df_mc_out["EM_RY_mc_var"].iloc[index_mc_comp_total])
        df_mc_out["EM_trend_normed_mc_var_normed"].iloc[index_mc_comp_total] = df_mc_out["EM_trend_normed_mc_var"].iloc[index_mc_comp_total]/ np.nansum(df_mc_out["EM_trend_normed_mc_var"].iloc[index_mc_comp_total])
    
        #Find indexes for the inventory total with and without LULUCF
        index_mc_inv_with_without_lulucf = df_mc_out.index[((df_mc_out["proc_code"].isin(const.PROC_CODE_INVENTORY_WITH_WITHOUT_LULUCF)) & (df_mc_out["comp_id"] == comp_id_total) & (df_mc_out["reso_id"] == reso_id_total) )].tolist() 
        if len(index_mc_inv_with_without_lulucf) == 0:
            check_file.write("Could not find the total with and without LULUCF in mc results!")
            check_file.close()
            raise ValueError("Could not find the total with and without LULUCF in mc results!")
    
        #**************For pr results*******************************
        #find indexes for the sums for each compound
        index_pr_comp_total = df_pr_out.index[((df_pr_out["proc_id"] == proc_id_total) & (df_pr_out["comp_id"].isin(comp_total)) & (df_pr_out["reso_id"] == reso_id_total) )].tolist() 
        if len(index_pr_comp_total) == 0:
            check_file.write("Could not find the total per compound in pr results!")
            check_file.close()
            raise ValueError("Could not find the total per compound in pr results!")
        #compute variance for each category/compound, normalised by sum of input variances
        df_pr_out["EM_BY_pr_var_normed"].iloc[index_pr_comp_total] = df_pr_out["EM_BY_pr_contrib_var_mean"].iloc[index_pr_comp_total]/ np.nansum(df_pr_out["EM_BY_pr_contrib_var_mean"].iloc[index_pr_comp_total])
        df_pr_out["EM_RY_pr_var_normed"].iloc[index_pr_comp_total] = df_pr_out["EM_RY_pr_contrib_var_mean"].iloc[index_pr_comp_total]/ np.nansum(df_pr_out["EM_RY_pr_contrib_var_mean"].iloc[index_pr_comp_total])
        df_pr_out["EM_trend_normed_pr_var_normed"].iloc[index_pr_comp_total] = df_pr_out["EM_trend_normed_pr_contrib_var_mean"].iloc[index_pr_comp_total]/ np.nansum(df_pr_out["EM_trend_normed_pr_contrib_var_mean"].iloc[index_pr_comp_total])
    
        #Find indexes for the inventory total with and without LULUCF
        index_pr_inv_with_without_lulucf = df_pr_out.index[((df_pr_out["proc_code"].isin(const.PROC_CODE_INVENTORY_WITH_WITHOUT_LULUCF)) & (df_pr_out["comp_id"] == comp_id_total) & (df_pr_out["reso_id"] == reso_id_total) )].tolist() 
        if len(index_pr_inv_with_without_lulucf) == 0:
            check_file.write("Could not find the total with and without LULUCF in pr results!")
            check_file.close()
            raise ValueError("Could not find the total with and without LULUCF in pr results!")
    
    
    else:
        index_mc_comp_total = None
        index_mc_inv_with_without_lulucf = None
        index_pr_comp_total = None
        index_pr_inv_with_without_lulucf = None
    
    
    
    #QC: check that the sum according to the aggregation routine is the same as the sum of all input rows.
    if abs(df_mc_out["EM_BY_mc_mean"].iloc[index_mc_total] - EM_BY_mc_inventory_mean)/EM_BY_mc_inventory_mean > 0.000001:
        check_file.write("There is a problem with the aggregation: sum of aggregated rows assigned to total are not the same of the sum of all rows for BY.\n")
    if abs(df_mc_out["EM_RY_mc_mean"].iloc[index_mc_total] - EM_RY_mc_inventory_mean)/EM_RY_mc_inventory_mean > 0.000001:
        check_file.write("There is a problem with the aggregation: sum of aggregated rows assigned to total are not the same of the sum of all rows for RY.\n")
    
    
    write_pr_mc_results(
            df_EM_u,
            df_pr_out,
            df_pr_out_AD_EF,
            df_mc_out,
            df_mc_out_AD_EF,
            index_pr_total,
            index_pr_proc_sector_total,
            index_pr_comp_total,
            index_pr_inv_with_without_lulucf,
            index_mc_total,
            index_mc_proc_sector_total,
            index_mc_comp_total,
            index_mc_inv_with_without_lulucf,
            BY_string,
            RY_string,
            no_mc,
            routine,
            dict_io_out["filename_out_u"],
            )
    
            
    
    
    #+++++++This the end of the routine for uncertainty+++++++++++++++++++++++


    #+++++++Key category analysis+++++++++++++++++++++++++++++++++++++++++++++
    #TODO key category analysis: run computations here (but do not write excel results within this loop).

    
    #HINT once the KCA is included here, return KCA results directly.
    return df_EM_u, df_pr_out, df_pr_out_AD_EF, df_mc_out, df_mc_out_AD_EF