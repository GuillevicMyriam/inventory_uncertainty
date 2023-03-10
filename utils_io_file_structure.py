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

Created on Thu Feb  9 11:09:33 2023

"""
#import from general libraries
import numpy as np
import datetime
from pathlib import Path
import random


def make_new_folder(output_folder_name_start: str):
    
    """Make a new folder name for outputs.
    
    Args:
        output_folder_name: start of output folder name.
    """
    
    """
    if routine == const.ROUTINE_IIR or routine == const.ROUTINE_IIR_WITHOUT_U:
        routine_text = "_IIR/"
    elif routine == const.ROUTINE_NID:
        routine_text = "_NID/"

    output_folder_name = root_path + "output_data/output_sub" + SY_string + "/" + "output_sub" + SY_string + routine_text
    """

    #generate random, unique folder name    
    allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"    
    date = datetime.datetime.now()
    random_string = "".join(random.sample(allowed_chars, 10))
    
    unique = False
    while unique is False:
        unique_out_folder_name = output_folder_name_start + "{0:%Y%m%d_%Hh%M}".format(date) + "_" + random_string + "/"
        
        if not Path(unique_out_folder_name).is_dir():
            unique = True
            Path(unique_out_folder_name).mkdir()    
        
    
    return unique_out_folder_name


#XXX Define file structure to read input nomenclature definition

def io_nomenc(root_path, SY_string):
    """
    Create exact path and names of Excel file(s) to read for the nomenclature and put all variable in a dictionary.
    
    The obtained dictionary is valid for any type of input data
    (pollutants, greenhouse gases, indirect emissions, anything).
    This function does not need yearly actualisation.
    This function needs actualisation only if the input excel file structure should change.
    
    Args:
        root_path: path frm root where to look for files.
        SY_string: string for the submission year, format YYYY.
        
    Returns:
        dict_io_nomenc: dictionary containing all needed information
            about the file structure to read in the nmenclature.
    """
    
    dict_io_nomenc = {}
        
    #===========================================================================
    # DEFINE PATH, NAME AND STRUCTURE OF INPUT FILE FOR NOMENCLATURE
    # FOR PROCESS, COMPOUND AND RESOURCE
    #===========================================================================
    
    in_nomenc_foldername = root_path + "input_data/input_sub" + SY_string + "/input_nomenclature/"
    in_nomenc_filename = "nomenclature_sub{}.xlsx".format(SY_string)
    in_nomenc_pathname = in_nomenc_foldername + in_nomenc_filename
        
    in_proc_sheetname = "process"
    in_comp_sheetname = "compound"
    in_reso_sheetname = "resource"
    
    in_proc_agg_tree_nfr_sheetname = "aggregation_process_nfr"
    in_proc_agg_tree_crt_sheetname = "aggregation_process_crt"
    in_comp_agg_tree_sheetname = "aggregation_compound"
    in_reso_agg_tree_sheetname = "aggregation_resource"
    
    
    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR CATEGORY/PROCESS NOMENCLATURE
    #===========================================================================
    
    in_header_proc = 0
    in_skiprows_proc = None
    in_col_names_proc_class_id = "proc_class_id"
    in_usecols_proc = [0, 1, 2, 3, 4, 8]
    in_col_names_proc = ["proc_id", "proc_code_name", "proc_class", "proc_code", "proc_name", "proc_rank"]
    
    in_merge_with_proc_left = ["proc_class", "proc_code"] #, "proc_name"
    in_merge_with_proc_right = ["proc_class", "proc_code"] #, "proc_name"
    in_check_proc_left = ["proc_class", "proc_code"]
    in_check_proc_right = ["proc_class", "proc_code"]
    
    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR COMPOUND NOMENCLATURE
    #===========================================================================
    
    in_header_comp = 0
    in_skiprows_comp = None
    in_usecols_comp = [0, 1, 2, 3]
    in_col_names_comp = ["comp_id", "comp_name", "comp_name_latex", "comp_rank"]
    
    in_merge_with_comp_left = ["comp_id"]
    in_merge_with_comp_right = ["comp_id"]
    in_check_comp_left = ["comp_id"]
    in_check_comp_right = ["comp_id"]
    
    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR RESOURCE NOMENCLATURE
    #===========================================================================
    
    in_header_reso = 0
    in_skiprows_reso = None
    in_usecols_reso = [0, 1, 2, 3]
    in_col_names_reso = ["reso_id", "reso_name", "reso_name_latex", "reso_rank"]

    in_merge_with_reso_left = ["reso_id"]
    in_merge_with_reso_right = ["reso_id"]
    in_check_reso_left = ["reso_id"]
    in_check_reso_right = ["reso_id"]

    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR PROCESS AGGREGATION
    #===========================================================================
    
    in_header_agg_proc = 0
    in_skiprows_agg_proc = 0
    in_usecols_agg_proc = [0, 1, 2, 3, 4]
    in_names_agg_proc = ["child_id_proc_class", "child_id_proc_code", "parent_id_proc_class", "parent_id_proc_code", "depth_id_proc"]
    in_dtype_agg_proc = {"child_id_proc_class": np.str, "child_id_proc_code": np.str, "parent_id_proc_class": np.str, "parent_id_proc_code": np.str, "depth_id_proc": np.int}
    

    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR COMPOUND AGGREGATION
    #===========================================================================
    
    in_header_agg_comp = 0
    in_skiprows_agg_comp = 0
    in_usecols_agg_comp = [0, 1, 2]
    in_names_agg_comp = ["child_id_comp", "parent_id_comp", "depth_id_comp"]
    in_dtype_agg_comp = {"child_id_comp": np.str, "parent_id_comp": np.str, "depth_id_comp": np.int}
    

    #===========================================================================
    # DEFINE STRUCTURE OF INPUT FILE FOR RESOURCE AGGREGATION
    #===========================================================================
    
    in_header_agg_reso = 0
    in_skiprows_agg_reso = 0
    in_usecols_agg_reso = [0, 1, 2]
    in_names_agg_reso = ["child_id_reso", "parent_id_reso", "depth_id_reso"]
    in_dtype_agg_reso = {"child_id_reso": np.str, "parent_id_reso": np.str, "depth_id_reso": np.int}
            
    
    dict_io_nomenc["in_nomenc_foldername"] = in_nomenc_foldername
    dict_io_nomenc["in_nomenc_filename"] = in_nomenc_filename
    dict_io_nomenc["in_nomenc_pathname"] = in_nomenc_pathname
    dict_io_nomenc["in_proc_sheetname"] = in_proc_sheetname
    dict_io_nomenc["in_comp_sheetname"] = in_comp_sheetname
    dict_io_nomenc["in_reso_sheetname"] = in_reso_sheetname
    dict_io_nomenc["in_proc_agg_tree_nfr_sheetname"] = in_proc_agg_tree_nfr_sheetname
    dict_io_nomenc["in_proc_agg_tree_crt_sheetname"] = in_proc_agg_tree_crt_sheetname
    dict_io_nomenc["in_comp_agg_tree_sheetname"] = in_comp_agg_tree_sheetname
    dict_io_nomenc["in_reso_agg_tree_sheetname"] = in_reso_agg_tree_sheetname
    dict_io_nomenc["in_header_proc"] = in_header_proc
    dict_io_nomenc["in_skiprows_proc"] = in_skiprows_proc
    dict_io_nomenc["in_col_names_proc_class_id"] = in_col_names_proc_class_id
    dict_io_nomenc["in_usecols_proc"] = in_usecols_proc
    dict_io_nomenc["in_col_names_proc"] = in_col_names_proc
    dict_io_nomenc["in_merge_with_proc_left"] = in_merge_with_proc_left
    dict_io_nomenc["in_merge_with_proc_right"] = in_merge_with_proc_right
    dict_io_nomenc["in_check_proc_left"] = in_check_proc_left
    dict_io_nomenc["in_check_proc_right"] = in_check_proc_right
    dict_io_nomenc["in_header_comp"] = in_header_comp
    dict_io_nomenc["in_skiprows_comp"] = in_skiprows_comp
    dict_io_nomenc["in_usecols_comp"] = in_usecols_comp
    dict_io_nomenc["in_col_names_comp"] = in_col_names_comp
    dict_io_nomenc["in_merge_with_comp_left"] = in_merge_with_comp_left
    dict_io_nomenc["in_merge_with_comp_right"] = in_merge_with_comp_right
    dict_io_nomenc["in_check_comp_left"] = in_check_comp_left
    dict_io_nomenc["in_check_comp_right"] = in_check_comp_right
    dict_io_nomenc["in_header_reso"] = in_header_reso
    dict_io_nomenc["in_skiprows_reso"] = in_skiprows_reso
    dict_io_nomenc["in_usecols_reso"] = in_usecols_reso
    dict_io_nomenc["in_col_names_reso"] = in_col_names_reso
    dict_io_nomenc["in_merge_with_reso_left"] = in_merge_with_reso_left
    dict_io_nomenc["in_merge_with_reso_right"] = in_merge_with_reso_right
    dict_io_nomenc["in_check_reso_left"] = in_check_reso_left
    dict_io_nomenc["in_check_reso_right"] = in_check_reso_right
    dict_io_nomenc["in_header_agg_proc"] = in_header_agg_proc
    dict_io_nomenc["in_skiprows_agg_proc"] = in_skiprows_agg_proc
    dict_io_nomenc["in_usecols_agg_proc"] = in_usecols_agg_proc
    dict_io_nomenc["in_names_agg_proc"] = in_names_agg_proc
    dict_io_nomenc["in_dtype_agg_proc"] = in_dtype_agg_proc
    dict_io_nomenc["in_header_agg_comp"] = in_header_agg_comp
    dict_io_nomenc["in_skiprows_agg_comp"] = in_skiprows_agg_comp
    dict_io_nomenc["in_usecols_agg_comp"] = in_usecols_agg_comp
    dict_io_nomenc["in_names_agg_comp"] = in_names_agg_comp
    dict_io_nomenc["in_dtype_agg_comp"] = in_dtype_agg_comp
    dict_io_nomenc["in_header_agg_reso"] = in_header_agg_reso
    dict_io_nomenc["in_skiprows_agg_reso"] = in_skiprows_agg_reso
    dict_io_nomenc["in_usecols_agg_reso"] = in_usecols_agg_reso
    dict_io_nomenc["in_names_agg_reso"] = in_names_agg_reso
    dict_io_nomenc["in_dtype_agg_reso"] = in_dtype_agg_reso
   
    return dict_io_nomenc


#XXX Below: define file structure to read nomenclature to use for reporting, define output file names

def io_out_inventory_crt(root_path, SY_string, make_new_output_folder):
    """Define file names for output files.
    """

    dict_io_out = {}
    dict_io_out["out_name_script"] = "inventory"

    dict_io_out["output_foldername"] = root_path + "output_data/output_sub" + SY_string + "/" + "output_sub" + SY_string + "_NID/"
    if make_new_output_folder:
        folder_name_start = dict_io_out["output_foldername"] + "NID_sub{}_{}_".format(SY_string, dict_io_out["out_name_script"])
        dict_io_out["output_foldername"] = make_new_folder(folder_name_start)

    #Warning! Do not add the .xlsx extension here. This is aded later on.
    dict_io_out["filename_out_KCA_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_KCA1_KCA2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_input_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_input".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_app1_app2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_tornado_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_tornado".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_distribution_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_distribution".format(SY_string, dict_io_out["out_name_script"])

    #name of output check file
    dict_io_out["check_filename"] = "NID_sub{}_{}_uncertainties_KCA_check_file.txt".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["check_filename"] = dict_io_out["output_foldername"] + dict_io_out["check_filename"]

    #The nomenclature to use for reporting is defined in the same file as input uncertainties    
    dict_io_out["out_nomenc_filename"] = "Uncertainties_Overview_NID_IIR_Sub{}.xlsx".format(SY_string)
    dict_io_out["out_nomenc_sheetname"] = "NID_output_CRT_codes"
    
    dict_io_out["out_nomenc_foldername"]  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    dict_io_out["out_nomenc_pathname"] = dict_io_out["out_nomenc_foldername"] + dict_io_out["out_nomenc_filename"]
        
    dict_io_out["header_out_nomenc"] = None
    dict_io_out["skiprows_out_nomenc"] = 10
    dict_io_out["usecols_out_nomenc"] = [0, 1, 3, 4]
    dict_io_out["col_names_out_nomenc"] = [
            "proc_class", #0
            "proc_code", #1
            #"proc_name", #2
            "reso_id", #3
            "comp_id", #4
            ]

    dict_io_out["col_dtype_out_nomenc"] = {
            "proc_class": str,
            "proc_code": str,
            "reso_id": str,
            "comp_id": str,
            }
       
    return dict_io_out


def io_out_indirect(root_path, SY_string, make_new_output_folder):
    """
    Create exact path and names of Excel file(s) for output files and put all variables in a dictionary.
    
    The obtained dictionary is valid for indirect emissions only.
    This function does not need yearly actualisation.
    This function needs actualisation only if the output excel file structure should change.
    
    Args:
        root_path: path frm root where to look for files.
        SY_string: string for the submission year, format YYYY.
        
    Returns:
        dict_io_out: dictionary containing all needed information
            about the file structure to write the output data.
    """

    dict_io_out = {}
    dict_io_out["out_name_script"] = "indirectEM"
    
    dict_io_out["output_foldername"] = root_path + "output_data/output_sub" + SY_string + "/" + "output_sub" + SY_string + "_NID/"    
    if make_new_output_folder:
        folder_name_start = dict_io_out["output_foldername"] + "NID_sub{}_{}_".format(SY_string, dict_io_out["out_name_script"])
        dict_io_out["output_foldername"] = make_new_folder(folder_name_start)
    
    #Warning! Do not add the .xlsx extension here. This is aded later on.
    dict_io_out["filename_out_KCA_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_KCA1_KCA2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_input_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_input".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_app1_app2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_tornado_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_tornado".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_distribution_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_distribution".format(SY_string, dict_io_out["out_name_script"])

    #name of output check file
    dict_io_out["check_filename"] = "NID_sub{}_{}_uncertainties_KCA_check_file.txt".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["check_filename"] = dict_io_out["output_foldername"] + dict_io_out["check_filename"]

    #Where to read nomenclature to use to report output
    dict_io_out["out_nomenc_filename"] = "Uncertainties_Overview_NID_IIR_Sub{}.xlsx".format(SY_string)
    dict_io_out["out_nomenc_sheetname"] = "NID_output_CRT_codes"
    
    dict_io_out["out_nomenc_foldername"]  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    dict_io_out["out_nomenc_pathname"] = dict_io_out["out_nomenc_foldername"] + dict_io_out["out_nomenc_filename"]
    
    
    dict_io_out["header_out_nomenc"] = None
    dict_io_out["skiprows_out_nomenc"] = 10
    dict_io_out["usecols_out_nomenc"] = [0, 1, 3, 4]
    dict_io_out["col_names_out_nomenc"] = [
            "proc_class", #0
            "proc_code", #1
            #"proc_name", #2
            "reso_id", #3
            "comp_id", #4
            ]
    dict_io_out["col_dtype_out_nomenc"] = {
            "proc_class": str,
            "proc_code": str,
            "reso_id": str,
            "comp_id": str,
            }    
   
    return dict_io_out


def io_out_lulucf(root_path, SY_string, make_new_output_folder):
    """
    Create exact path and names of Excel file(s) for output files and put all variables in a dictionary.
    
    The obtained dictionary is valid for LULUCF emissions only.
    This function does not need yearly actualisation.
    This function needs actualisation only if the output excel file structure should change.
    
    Args:
        root_path: path frm root where to look for files.
        SY_string: string for the submission year, format YYYY.
        
    Returns:
        dict_io_out: dictionary containing all needed information
            about the file structure to write the output data.
    """

    dict_io_out = {}
    dict_io_out["out_name_script"] = "LULUCF"

    dict_io_out["output_foldername"] = root_path + "output_data/output_sub" + SY_string + "/" + "output_sub" + SY_string + "_NID/"
    if make_new_output_folder:
        folder_name_start = dict_io_out["output_foldername"] + "NID_sub{}_{}_".format(SY_string, dict_io_out["out_name_script"])
        dict_io_out["output_foldername"] = make_new_folder(folder_name_start)

    #Warning! Do not add the .xlsx extension here. This is aded later on.
    dict_io_out["filename_out_KCA_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_KCA1_KCA2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_input_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_input".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_uncertainties_app1_app2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_tornado_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_tornado".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_distribution_root"] = dict_io_out["output_foldername"] + "NID_sub{}_{}_fig_mc_distribution".format(SY_string, dict_io_out["out_name_script"])

    #name of output check file
    dict_io_out["check_filename"] = "NID_sub{}_{}_uncertainties_KCA_check_file.txt".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["check_filename"] = dict_io_out["output_foldername"] + dict_io_out["check_filename"]

    #Where to read nomenclature to use to report output    
    dict_io_out["out_nomenc_filename"] = "Uncertainties_Overview_NID_IIR_Sub{}.xlsx".format(SY_string)
    dict_io_out["out_nomenc_sheetname"] = "NID_output_CRT_codes"
    
    dict_io_out["out_nomenc_foldername"]  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    dict_io_out["out_nomenc_pathname"] = dict_io_out["out_nomenc_foldername"] + dict_io_out["out_nomenc_filename"]
    
    
    dict_io_out["header_out_nomenc"] = None
    dict_io_out["skiprows_out_nomenc"] = 10
    dict_io_out["usecols_out_nomenc"] = [0, 1, 3, 4]
    dict_io_out["col_names_out_nomenc"] = [
            "proc_class", #0
            "proc_code", #1
            #"proc_name", #2
            "reso_id", #3
            "comp_id", #4
            ]

    dict_io_out["col_dtype_out_nomenc"] = {
            "proc_class": str,
            "proc_code": str,
            "reso_id": str,
            "comp_id": str,
            }
       
    return dict_io_out



def io_out_inventory_nfr(root_path, SY_string, make_new_output_folder):
    """Define file names for output files.
    Define file name for check file.
    Read in nomenclature to use for source categories to report.
    
    Warning! Do not define final file names for output files,
    i.e. do not give an extension yet,
    because the final name requires compound name, and we don't have it yet.
    """

    dict_io_out = {}
    dict_io_out["out_name_script"] = "inventory"

    dict_io_out["output_foldername"] = root_path + "output_data/output_sub" + SY_string + "/" + "output_sub" + SY_string + "_IIR/"
    if make_new_output_folder:
        folder_name_start = dict_io_out["output_foldername"] + "IIR_sub{}_{}_".format(SY_string, dict_io_out["out_name_script"])
        dict_io_out["output_foldername"] = make_new_folder(folder_name_start)

    #Warning! Do not add the .xlsx extension here. This is aded later on.
    dict_io_out["filename_out_KCA_root"] = dict_io_out["output_foldername"] + "IIR_sub{}_{}_KCA1_KCA2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_input_root"] = dict_io_out["output_foldername"] + "IIR_sub{}_{}_uncertainties_input".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["filename_out_u_root"] = dict_io_out["output_foldername"] + "IIR_sub{}_{}_uncertainties_app1_app2".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_tornado_root"] = dict_io_out["output_foldername"] + "IIR_sub{}_{}_fig_mc_tornado".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["figname_out_mc_distribution_root"] = dict_io_out["output_foldername"] + "IIR_sub{}_{}_fig_mc_distribution".format(SY_string, dict_io_out["out_name_script"])

    #name of output check file
    dict_io_out["check_filename"] = "IIR_sub{}_{}_uncertainties_KCA_check_file.txt".format(SY_string, dict_io_out["out_name_script"])
    dict_io_out["check_filename"] = dict_io_out["output_foldername"] + dict_io_out["check_filename"]

    #For pollutants, the output nomenclature to use is exactly the NFR table, so just read in the NFR table
    dict_io_em = io_em_inventory_nfr(root_path, SY_string)
        
    dict_io_out["out_nomenc_filename"] = dict_io_em["in_EM_RY_filename"] #"Uncertainties_Overview_NID_IIR_Sub{}.xlsx".format(SY_string)
    dict_io_out["out_nomenc_sheetname"] = dict_io_em["in_EM_RY_sheetname"] #"NID_output_CRT_codes"
    
    dict_io_out["out_nomenc_foldername"]  = dict_io_em["in_EM_RY_foldername"]#root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    dict_io_out["out_nomenc_pathname"] = dict_io_out["out_nomenc_foldername"] + dict_io_out["out_nomenc_filename"]
        
    dict_io_out["header_out_nomenc"] = dict_io_em["in_header_EM_RY"] #None
    dict_io_out["skiprows_out_nomenc"] = dict_io_em["in_skiprows_EM_RY"]
    dict_io_out["usecols_out_nomenc"] = dict_io_em["in_usecols_EM_BY_nomenc"]
    dict_io_out["col_names_out_nomenc"] = dict_io_em["in_col_names_EM_RY_nomenc"] #proc_code

    dict_io_out["col_dtype_out_nomenc"] = dict_io_em["in_col_dtype_EM_RY"]
   
    return dict_io_out



#XXX Below: define file structure to read input uncertainties

def io_u_inventory_crt(root_path, SY_string, BY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    
    RY_string = str(int(SY_string)-2)

    #set the name of the input uncertainty file.
    #Uncertainties for the reporting year at least should be given.
    #Uncertainties for the base year can be given in the same file, in a different tab.
    #If there are no uncertainties given for the base year,
    #uncertainties are assumed to be the same as for the reporting year.
    in_U_BY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    in_U_RY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    
    in_U_RY_sheetname = "U_NID_{}_sub{}".format(RY_string, SY_string)
    in_U_BY_sheetname = "U_NID_{}_sub{}".format(BY_string, SY_string)

    in_U_BY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_BY_pathname = in_U_BY_foldername + in_U_BY_filename
    in_U_RY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_RY_pathname = in_U_RY_foldername + in_U_RY_filename
    
    in_header_u = None
    in_skiprows_u = 10
    
    in_usecols_u = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    in_col_names_u = [
            "proc_class", #0
            "proc_code", #1
            #"proc_name", #2
            "reso_id", #3
            "comp_id", #4
            "uAD_dist", #5
            "uAD_sym_f", #6
            "uAD_lower_f", #7
            "uAD_upper_f", #8
            "uAD_corr", #9
            #"uAD_ref", # not applicable for indirect emissions
            "uEF_dist", #10
            "uEF_sym_f", #11
            "uEF_lower_f", #12
            "uEF_upper_f", #13
            "uEF_corr", #14
            #"uEF_ref", # not applicable for indirect emissions
            "uEM_dist", #15
            "uEM_sym_f", #16
            "uEM_lower_f", #17
            "uEM_upper_f", #18
            "uEM_corr", #18
            #"uEM_ref", # not applicable for indirect emissions
                    ]
        
    in_col_dtype_u = {
            "uAD_dist": object,
            "uAD_sym_f": object,
            "uAD_lower_f": object,
            "uAD_upper_f": object,
            "uAD_corr": object,
            "uEF_dist": object,
            "uEF_sym_f": object,
            "uEF_lower_f": object,
            "uEF_upper_f": object,
            "uEF_corr": object,
            "uEM_dist": object,
            "uEM_sym_f": object,
            "uEM_lower_f": object,
            "uEM_upper_f": object,
            "uEM_corr": object,
            }    
    
    dict_io_u = {}
    
    dict_io_u["in_U_BY_filename"] = in_U_BY_filename
    dict_io_u["in_U_RY_filename"] = in_U_RY_filename
    dict_io_u["in_U_RY_sheetname"] = in_U_RY_sheetname
    dict_io_u["in_U_BY_sheetname"] = in_U_BY_sheetname
    dict_io_u["in_U_BY_foldername"] = in_U_BY_foldername
    dict_io_u["in_U_BY_pathname"] = in_U_BY_pathname
    dict_io_u["in_U_RY_foldername"] = in_U_RY_foldername
    dict_io_u["in_U_RY_pathname"] = in_U_RY_pathname
    dict_io_u["in_header_u"] = in_header_u
    dict_io_u["in_skiprows_u"] = in_skiprows_u
    dict_io_u["in_usecols_u"] = in_usecols_u
    dict_io_u["in_col_names_u"] = in_col_names_u
    dict_io_u["in_col_dtype_u"] = in_col_dtype_u
    
    return dict_io_u


def io_u_indirect(root_path, SY_string, BY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    RY_string = str(int(SY_string)-2)

    #set the name of the input uncertainty file.
    #Uncertainties for the reporting year at least should be given.
    #Uncertainties for the base year can be given in the same file, in a different tab.
    #If there are no uncertainties given for the base year,
    #uncertainties are assumed to be the same as for the reporting year.
    in_U_BY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    in_U_RY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    
    in_U_RY_sheetname = "U_NID_indirect_{}_sub{}".format(RY_string, SY_string)
    in_U_BY_sheetname = None
    

    in_U_BY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_BY_pathname = in_U_BY_foldername + in_U_BY_filename
    in_U_RY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_RY_pathname = in_U_RY_foldername + in_U_RY_filename

    dict_io_u_inventory_crt = io_u_inventory_crt(root_path, SY_string, BY_string)   
    
    dict_io_u = {}
    
    dict_io_u["in_U_BY_filename"] = in_U_BY_filename
    dict_io_u["in_U_RY_filename"] = in_U_RY_filename
    dict_io_u["in_U_RY_sheetname"] = in_U_RY_sheetname
    dict_io_u["in_U_BY_sheetname"] = in_U_BY_sheetname
    dict_io_u["in_U_BY_foldername"] = in_U_BY_foldername
    dict_io_u["in_U_BY_pathname"] = in_U_BY_pathname
    dict_io_u["in_U_RY_foldername"] = in_U_RY_foldername
    dict_io_u["in_U_RY_pathname"] = in_U_RY_pathname

    dict_io_u["in_header_u"] = dict_io_u_inventory_crt["in_header_u"] #in_header_u
    dict_io_u["in_skiprows_u"] = dict_io_u_inventory_crt["in_skiprows_u"] #in_skiprows_u
    dict_io_u["in_usecols_u"] = dict_io_u_inventory_crt["in_usecols_u"] #in_usecols_u
    dict_io_u["in_col_names_u"] = dict_io_u_inventory_crt["in_col_names_u"] #in_col_names_u
    dict_io_u["in_col_dtype_u"] = dict_io_u_inventory_crt["in_col_dtype_u"] #in_col_dtype_u
    
    return dict_io_u


def io_u_lulucf(root_path, SY_string, BY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    
    RY_string = str(int(SY_string)-2)

    #set the name of the input uncertainty file.
    #Uncertainties for the reporting year at least should be given.
    #Uncertainties for the base year can be given in the same file, in a different tab.
    #If there are no uncertainties given for the base year,
    #uncertainties are assumed to be the same as for the reporting year.
    in_U_BY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    in_U_RY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    
    in_U_RY_sheetname = "U_LULUCF_{}_sub{}".format(RY_string, SY_string)
    in_U_BY_sheetname = "U_LULUCF_{}_sub{}".format(BY_string, SY_string)

    in_U_BY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_BY_pathname = in_U_BY_foldername + in_U_BY_filename
    in_U_RY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_RY_pathname = in_U_RY_foldername + in_U_RY_filename

    dict_io_u_inventory_crt = io_u_inventory_crt(root_path, SY_string, BY_string)      
    
    dict_io_u = {}
    
    dict_io_u["in_U_BY_filename"] = in_U_BY_filename
    dict_io_u["in_U_RY_filename"] = in_U_RY_filename
    dict_io_u["in_U_RY_sheetname"] = in_U_RY_sheetname
    dict_io_u["in_U_BY_sheetname"] = in_U_BY_sheetname
    dict_io_u["in_U_BY_foldername"] = in_U_BY_foldername
    dict_io_u["in_U_BY_pathname"] = in_U_BY_pathname
    dict_io_u["in_U_RY_foldername"] = in_U_RY_foldername
    dict_io_u["in_U_RY_pathname"] = in_U_RY_pathname

    dict_io_u["in_header_u"] = dict_io_u_inventory_crt["in_header_u"] #in_header_u
    dict_io_u["in_skiprows_u"] = dict_io_u_inventory_crt["in_skiprows_u"] #in_skiprows_u
    dict_io_u["in_usecols_u"] = dict_io_u_inventory_crt["in_usecols_u"] #in_usecols_u
    dict_io_u["in_col_names_u"] = dict_io_u_inventory_crt["in_col_names_u"] #in_col_names_u
    dict_io_u["in_col_dtype_u"] = dict_io_u_inventory_crt["in_col_dtype_u"] #in_col_dtype_u
    
    return dict_io_u



def io_u_inventory_nfr(root_path, SY_string, BY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    
    dict_io_u = {}

    RY_string = str(int(SY_string)-2)

    #set the name of the input uncertainty file.
    #Uncertainties for the reporting year at least should be given.
    #Uncertainties for the base year can be given in the same file, in a different tab.
    #If there are no uncertainties given for the base year,
    #uncertainties are assumed to be the same as for the reporting year.
    in_U_BY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    in_U_RY_filename = "Uncertainties_Overview_NID_IIR_sub{}.xlsx".format(SY_string)
    
    in_U_RY_sheetname = "U_IIR_{}_sub{}".format(RY_string, SY_string)
    #in_U_BY_sheetname = "U_IIR_{}_sub{}".format(BY_string, SY_string)
    in_U_BY_sheetname = None

    in_U_BY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_BY_pathname = in_U_BY_foldername + in_U_BY_filename
    in_U_RY_foldername  = root_path + "input_data/input_sub" + SY_string + "/input_uncertainty/"
    in_U_RY_pathname = in_U_RY_foldername + in_U_RY_filename
    
    in_header_u = None
    in_skiprows_u = 10


    in_usecols_u_nomenc = [0, 1] #column 2 would be for the process name maybe in the future
    in_usecols_u_AD = [3,4,5,6,7,8]#[i for i in range(3,51)]
    in_usecols_u_EF = [
            [9,10,11,12,13,14], #NOx
            [15,16,17,18,19,20],#NMVOC
            [21,22,23,24,25,26],#SOx
            [27,28,29,30,31,32],#NH3
            [33,34,35,36,37,38],#PM2.5
            [39,40,41,42,43,44],#PM10
            ]
            
    
    in_col_names_u = [
            "proc_class", #0
            "proc_code", #1
            #"proc_name", #2
            #"reso_id", #3
            #"comp_id", #4
            "uAD_dist", #5
            "uAD_sym_f", #6
            "uAD_lower_f", #7
            "uAD_upper_f", #8
            "uAD_corr", #9
            "uAD_ref", # not applicable for crt emissions
            "uEF_dist", #10
            "uEF_sym_f", #11
            "uEF_lower_f", #12
            "uEF_upper_f", #13
            "uEF_corr", #14
            "uEF_ref", # not applicable for crt emissions
            #"uEM_dist", #15
            #"uEM_sym_f", #16
            #"uEM_lower_f", #17
            #"uEM_upper_f", #18
            #"uEM_corr", #18
            #"uEM_ref", # not applicable for crt emissions
                    ]
        
    in_col_dtype_u = {
            "uAD_dist": object,
            "uAD_sym_f": object,
            "uAD_lower_f": object,
            "uAD_upper_f": object,
            "uAD_corr": object,
            "uEF_dist": object,
            "uEF_sym_f": object,
            "uEF_lower_f": object,
            "uEF_upper_f": object,
            "uEF_corr": object,
            "uEM_dist": object,
            "uEM_sym_f": object,
            "uEM_lower_f": object,
            "uEM_upper_f": object,
            "uEM_corr": object,
            }    
    
    dict_io_u = {}
    
    dict_io_u["in_U_BY_filename"] = in_U_BY_filename
    dict_io_u["in_U_RY_filename"] = in_U_RY_filename
    dict_io_u["in_U_RY_sheetname"] = in_U_RY_sheetname
    dict_io_u["in_U_BY_sheetname"] = in_U_BY_sheetname
    dict_io_u["in_U_BY_foldername"] = in_U_BY_foldername
    dict_io_u["in_U_BY_pathname"] = in_U_BY_pathname
    dict_io_u["in_U_RY_foldername"] = in_U_RY_foldername
    dict_io_u["in_U_RY_pathname"] = in_U_RY_pathname
    dict_io_u["in_header_u"] = in_header_u
    dict_io_u["in_skiprows_u"] = in_skiprows_u
    #dict_io_u["in_usecols_u"] = in_usecols_u
    dict_io_u["in_usecols_u_nomenc"] = in_usecols_u_nomenc #in_usecols_u_nomenc
    dict_io_u["in_usecols_u_AD"] = in_usecols_u_AD
    dict_io_u["in_usecols_u_EF"] = in_usecols_u_EF
    dict_io_u["in_col_names_u"] = in_col_names_u
    dict_io_u["in_col_dtype_u"] = in_col_dtype_u
    
    return dict_io_u


#XXX Below: define file structure to read input emissions

def io_em_inventory_crt(root_path, SY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    
    #===========================================================================
    # SET NAME OF INPUT EMISSIONS DATA FILES
    #===========================================================================
    
    #For sumission 2022 it is the same input file for base year and reporting year.
    
    #set the name of the input emission file for the base year
    in_EM_BY_filename = "EM_GHGs_inventory_sub{}.xlsm".format(SY_string)
    in_EM_BY_sheetname = "EM_for_U_KCA"
    #set the name of the input emission file for the reporting year
    in_EM_RY_filename = "EM_GHGs_inventory_sub{}.xlsm".format(SY_string)
    in_EM_RY_sheetname = "EM_for_U_KCA"

    in_EM_foldername = root_path + "input_data/input_sub" + SY_string + "/input_EM_GHG/"
    in_EM_BY_pathname = in_EM_foldername + in_EM_BY_filename
    in_EM_RY_pathname = in_EM_foldername + in_EM_RY_filename
    
        
    #^^^^^^^^^^^^^Define format of input file for emissions^^^^^^^^^^^^^^^^^^^^
    
    #Input EM: indirect emission for base year    
    in_pathname_EM_BY = in_EM_BY_pathname
    in_sheetname_EM_BY = in_EM_BY_sheetname
    in_header_EM_BY = None
    in_skiprows_EM_BY = 9
    in_usecols_EM_BY = [0, 1, 3, 4, 5, 6]
    in_col_names_EM_BY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_BY = {"EM_status": str} #object
    in_usecols_EM_BY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_BY_val = [6] #columns for the numeric values
    
    #Input EM: indirect emission for reporting year
    in_pathname_EM_RY = in_EM_RY_pathname
    in_sheetname_EM_RY = in_EM_RY_sheetname
    in_header_EM_RY = None
    in_skiprows_EM_RY = 9
    in_usecols_EM_RY = [0, 1, 3, 4, 5, 7]
    in_col_names_EM_RY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_RY = {"EM_status": str} #object    
    in_usecols_EM_RY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_RY_val = [7] #columns for the numeric values

    #Column defining the SQL equivalent of a primary key
    in_col_unique_em = ["proc_id", "reso_id", "comp_id"]        
    in_col_from_main_proc = ["proc_id", "proc_class", "proc_code"] #use from main to merge


    dict_io_em = {}
    
    dict_io_em["in_EM_BY_filename"] = in_EM_BY_filename
    dict_io_em["in_EM_BY_sheetname"] = in_EM_BY_sheetname
    dict_io_em["in_EM_RY_filename"] = in_EM_RY_filename
    dict_io_em["in_EM_RY_sheetname"] = in_EM_RY_sheetname
    dict_io_em["in_EM_BY_pathname"] = in_EM_BY_pathname
    dict_io_em["in_EM_RY_pathname"] = in_EM_RY_pathname
    dict_io_em["in_pathname_EM_BY"] = in_pathname_EM_BY
    dict_io_em["in_sheetname_EM_BY"] = in_sheetname_EM_BY
    dict_io_em["in_header_EM_BY"] = in_header_EM_BY
    dict_io_em["in_skiprows_EM_BY"] = in_skiprows_EM_BY
    dict_io_em["in_usecols_EM_BY"] = in_usecols_EM_BY
    dict_io_em["in_col_names_EM_BY"] = in_col_names_EM_BY
    dict_io_em["in_col_dtype_EM_BY"] = in_col_dtype_EM_BY
    dict_io_em["in_pathname_EM_RY"] = in_pathname_EM_RY
    dict_io_em["in_sheetname_EM_RY"] = in_sheetname_EM_RY
    dict_io_em["in_header_EM_RY"] = in_header_EM_RY
    dict_io_em["in_skiprows_EM_RY"] = in_skiprows_EM_RY
    dict_io_em["in_usecols_EM_RY"] = in_usecols_EM_RY
    dict_io_em["in_col_names_EM_RY"] = in_col_names_EM_RY
    dict_io_em["in_col_dtype_EM_RY"] = in_col_dtype_EM_RY
    dict_io_em["in_col_unique_em"] = in_col_unique_em
    dict_io_em["in_col_from_main_proc"] = in_col_from_main_proc

    dict_io_em["in_usecols_EM_BY_nomenc"] = in_usecols_EM_BY_nomenc
    dict_io_em["in_usecols_EM_BY_val"] = in_usecols_EM_BY_val
    dict_io_em["in_usecols_EM_RY_nomenc"] = in_usecols_EM_RY_nomenc
    dict_io_em["in_usecols_EM_RY_val"] = in_usecols_EM_RY_val

    
    return dict_io_em


def io_em_indirect(root_path, SY_string):
    """
    Create exact path and names of Excel file(s) to read for the emissions and put all variables in a dictionnary.
    
    BY_string: base year in string format
    RY_string: reporting year in string format
    SY_string: submission year in string format
    """

    #===========================================================================
    # SET NAME OF INPUT EMISSIONS DATA FILES
    #===========================================================================
    
    #For sumission 2022 it is the same input file for base year and reporting year.
    
    #set the name of the input emission file for the base year
    in_EM_BY_filename = "EM_GHGs_indirect_sub{}.xlsm".format(SY_string)
    in_EM_BY_sheetname = "EM_for_U_KCA"
    #set the name of the input emission file for the reporting year
    in_EM_RY_filename = "EM_GHGs_indirect_sub{}.xlsm".format(SY_string)
    in_EM_RY_sheetname = "EM_for_U_KCA"

    in_EM_foldername = root_path + "input_data/input_sub" + SY_string + "/input_EM_GHG/"
    in_EM_BY_pathname = in_EM_foldername + in_EM_BY_filename
    in_EM_RY_pathname = in_EM_foldername + in_EM_RY_filename
    
        
    #^^^^^^^^^^^^^Define format of input file for emissions^^^^^^^^^^^^^^^^^^^^
    
    #Input EM: indirect emission for base year    
    in_pathname_EM_BY = in_EM_BY_pathname
    in_sheetname_EM_BY = in_EM_BY_sheetname
    in_header_EM_BY = None
    in_skiprows_EM_BY = 9
    in_usecols_EM_BY = [0, 1, 3, 4, 5, 6]
    in_col_names_EM_BY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_BY = {"EM_status": str} #object
    in_usecols_EM_BY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_BY_val = [6] #columns for the numeric values
    
    #Input EM: indirect emission for reporting year
    in_pathname_EM_RY = in_EM_RY_pathname
    in_sheetname_EM_RY = in_EM_RY_sheetname
    in_header_EM_RY = None
    in_skiprows_EM_RY = 9
    in_usecols_EM_RY = [0, 1, 3, 4, 5, 7]
    in_col_names_EM_RY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_RY = {"EM_status": str} #object    
    in_usecols_EM_RY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_RY_val = [7] #columns for the numeric values

    #Column defining the SQL equivalent of a primary key
    in_col_unique_em = ["proc_id", "reso_id", "comp_id"]        
    in_col_from_main_proc = ["proc_id", "proc_class", "proc_code"] #use from main to merge


    dict_io_em = {}
    
    dict_io_em["in_EM_BY_filename"] = in_EM_BY_filename
    dict_io_em["in_EM_BY_sheetname"] = in_EM_BY_sheetname
    dict_io_em["in_EM_RY_filename"] = in_EM_RY_filename
    dict_io_em["in_EM_RY_sheetname"] = in_EM_RY_sheetname
    dict_io_em["in_EM_BY_pathname"] = in_EM_BY_pathname
    dict_io_em["in_EM_RY_pathname"] = in_EM_RY_pathname
    dict_io_em["in_pathname_EM_BY"] = in_pathname_EM_BY
    dict_io_em["in_sheetname_EM_BY"] = in_sheetname_EM_BY
    dict_io_em["in_header_EM_BY"] = in_header_EM_BY
    dict_io_em["in_skiprows_EM_BY"] = in_skiprows_EM_BY
    dict_io_em["in_usecols_EM_BY"] = in_usecols_EM_BY
    dict_io_em["in_col_names_EM_BY"] = in_col_names_EM_BY
    dict_io_em["in_col_dtype_EM_BY"] = in_col_dtype_EM_BY
    dict_io_em["in_pathname_EM_RY"] = in_pathname_EM_RY
    dict_io_em["in_sheetname_EM_RY"] = in_sheetname_EM_RY
    dict_io_em["in_header_EM_RY"] = in_header_EM_RY
    dict_io_em["in_skiprows_EM_RY"] = in_skiprows_EM_RY
    dict_io_em["in_usecols_EM_RY"] = in_usecols_EM_RY
    dict_io_em["in_col_names_EM_RY"] = in_col_names_EM_RY
    dict_io_em["in_col_dtype_EM_RY"] = in_col_dtype_EM_RY
    dict_io_em["in_col_unique_em"] = in_col_unique_em
    dict_io_em["in_col_from_main_proc"] = in_col_from_main_proc

    dict_io_em["in_usecols_EM_BY_nomenc"] = in_usecols_EM_BY_nomenc
    dict_io_em["in_usecols_EM_BY_val"] = in_usecols_EM_BY_val
    dict_io_em["in_usecols_EM_RY_nomenc"] = in_usecols_EM_RY_nomenc
    dict_io_em["in_usecols_EM_RY_val"] = in_usecols_EM_RY_val
    
    return dict_io_em



def io_em_lulucf(root_path, SY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """
    
    #===========================================================================
    # SET NAME OF INPUT EMISSIONS DATA FILES
    #===========================================================================
    
    #For sumission 2022 it is the same input file for base year and reporting year.
    
    #set the name of the input emission file for the base year
    in_EM_BY_filename = "EM_GHGs_inventory_sub{}.xlsm".format(SY_string)
    in_EM_BY_sheetname = "LULUCF_EM_for_U_KCA"
    #set the name of the input emission file for the reporting year
    in_EM_RY_filename = "EM_GHGs_inventory_sub{}.xlsm".format(SY_string)
    in_EM_RY_sheetname = "LULUCF_EM_for_U_KCA"

    in_EM_foldername = root_path + "input_data/input_sub" + SY_string + "/input_EM_GHG/"
    in_EM_BY_pathname = in_EM_foldername + in_EM_BY_filename
    in_EM_RY_pathname = in_EM_foldername + in_EM_RY_filename
    
        
    #^^^^^^^^^^^^^Define format of input file for emissions^^^^^^^^^^^^^^^^^^^^
    
    #Input EM: indirect emission for base year    
    in_pathname_EM_BY = in_EM_BY_pathname
    in_sheetname_EM_BY = in_EM_BY_sheetname
    in_header_EM_BY = None
    in_skiprows_EM_BY = 9
    in_usecols_EM_BY = [0, 1, 3, 4, 5, 6]
    in_col_names_EM_BY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_BY = {"EM_status": str} #object
    in_usecols_EM_BY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_BY_val = [6] #columns for the numeric values
    
    #Input EM: indirect emission for reporting year
    in_pathname_EM_RY = in_EM_RY_pathname
    in_sheetname_EM_RY = in_EM_RY_sheetname
    in_header_EM_RY = None
    in_skiprows_EM_RY = 9
    in_usecols_EM_RY = [0, 1, 3, 4, 5, 7]
    in_col_names_EM_RY = ["proc_class", "proc_code", "reso_id", "comp_id", "unit", "EM_status"]
    in_col_dtype_EM_RY = {"EM_status": str} #object    
    in_usecols_EM_RY_nomenc = [0, 1, 3, 4, 5] #columns for source category definitions
    in_usecols_EM_RY_val = [7] #columns for the numeric values

    #Column defining the SQL equivalent of a primary key
    in_col_unique_em = ["proc_id", "reso_id", "comp_id"]        
    in_col_from_main_proc = ["proc_id", "proc_class", "proc_code"] #use from main to merge


    dict_io_em = {}
    
    dict_io_em["in_EM_BY_filename"] = in_EM_BY_filename
    dict_io_em["in_EM_BY_sheetname"] = in_EM_BY_sheetname
    dict_io_em["in_EM_RY_filename"] = in_EM_RY_filename
    dict_io_em["in_EM_RY_sheetname"] = in_EM_RY_sheetname
    dict_io_em["in_EM_BY_pathname"] = in_EM_BY_pathname
    dict_io_em["in_EM_RY_pathname"] = in_EM_RY_pathname
    dict_io_em["in_pathname_EM_BY"] = in_pathname_EM_BY
    dict_io_em["in_sheetname_EM_BY"] = in_sheetname_EM_BY
    dict_io_em["in_header_EM_BY"] = in_header_EM_BY
    dict_io_em["in_skiprows_EM_BY"] = in_skiprows_EM_BY
    dict_io_em["in_usecols_EM_BY"] = in_usecols_EM_BY
    dict_io_em["in_col_names_EM_BY"] = in_col_names_EM_BY
    dict_io_em["in_col_dtype_EM_BY"] = in_col_dtype_EM_BY
    dict_io_em["in_pathname_EM_RY"] = in_pathname_EM_RY
    dict_io_em["in_sheetname_EM_RY"] = in_sheetname_EM_RY
    dict_io_em["in_header_EM_RY"] = in_header_EM_RY
    dict_io_em["in_skiprows_EM_RY"] = in_skiprows_EM_RY
    dict_io_em["in_usecols_EM_RY"] = in_usecols_EM_RY
    dict_io_em["in_col_names_EM_RY"] = in_col_names_EM_RY
    dict_io_em["in_col_dtype_EM_RY"] = in_col_dtype_EM_RY
    dict_io_em["in_col_unique_em"] = in_col_unique_em
    dict_io_em["in_col_from_main_proc"] = in_col_from_main_proc

    dict_io_em["in_usecols_EM_BY_nomenc"] = in_usecols_EM_BY_nomenc
    dict_io_em["in_usecols_EM_BY_val"] = in_usecols_EM_BY_val
    dict_io_em["in_usecols_EM_RY_nomenc"] = in_usecols_EM_RY_nomenc
    dict_io_em["in_usecols_EM_RY_val"] = in_usecols_EM_RY_val
    
    return dict_io_em



def io_em_inventory_nfr(root_path, SY_string):
    """
    Create exact path and names of Excel file(s) to read for the uncertainties and put all variables in a dictionnary.
    """

    #===========================================================================
    # SET NAME OF INPUT EMISSIONS DATA FILES
    #===========================================================================
    
    RY_string = str(int(float(SY_string))-2)
    
    #set the name of the input emission file for the base year
    in_EM_BY_filename = "UNECE {} Table 1 - 1990-1999.xlsm".format(SY_string) #UNECE {} Table 1 - 1990-1999
    in_EM_BY_sheetname = "1990"
    #set the name of the input emission file for the reporting year
    in_EM_RY_filename = "UNECE {} Table 1 - 2010-{}.xlsm".format(SY_string, RY_string) #UNECE {} Table 1 - 2010-{}
    in_EM_RY_sheetname = RY_string

    in_EM_foldername = root_path + "input_data/input_sub" + SY_string + "/input_EM_pollutant/"
    in_EM_BY_pathname = in_EM_foldername + in_EM_BY_filename
    in_EM_RY_pathname = in_EM_foldername + in_EM_RY_filename
    
        
    #^^^^^^^^^^^^^Define format of input file for emissions^^^^^^^^^^^^^^^^^^^^
    
    #NOx, NMVOC, SOx, NH3, PM2.5, PM10
    
    #Input EM: emission for base year    
    in_pathname_EM_BY = in_EM_BY_pathname
    in_sheetname_EM_BY = in_EM_BY_sheetname
    in_header_EM_BY = None
    in_skiprows_EM_BY = 12
    in_usecols_EM_BY_nomenc = [1] #excel column starts at zero
    in_usecols_EM_BY_val = [4, 5, 6, 7, 8, 9] #special for pollutants: one column per pollutant
    in_usecols_EM_BY = in_usecols_EM_BY_nomenc
    
    in_col_names_EM_BY_nomenc = ["proc_code"]
    in_col_dtype_EM_BY_nomenc = {"proc_code": str}
    in_col_names_EM_BY = ["proc_code", "EM_status"]
    in_col_dtype_EM_BY = {"EM_status": str}

    
    #Input EM: emission for reporting year
    in_pathname_EM_RY = in_EM_RY_pathname
    in_sheetname_EM_RY = in_EM_RY_sheetname
    in_header_EM_RY = in_header_EM_BY
    in_skiprows_EM_RY = in_skiprows_EM_BY
    in_usecols_EM_RY_nomenc = in_usecols_EM_BY_nomenc
    in_usecols_EM_RY_val = in_usecols_EM_BY_val
    in_usecols_EM_RY = in_usecols_EM_BY

    in_col_names_EM_RY = in_col_names_EM_BY
    in_col_dtype_EM_RY = in_col_dtype_EM_BY  

    #Column defining the SQL equivalent of a primary key
    in_col_unique_em = ["proc_id", "reso_id", "comp_id"]        
    in_col_from_main_proc = ["proc_id", "proc_class", "proc_code"] #use from main to merge

    
    dict_io_em = {}

    dict_io_em["in_EM_BY_filename"] = in_EM_BY_filename
    dict_io_em["in_EM_BY_sheetname"] = in_EM_BY_sheetname
    dict_io_em["in_EM_RY_filename"] = in_EM_RY_filename
    dict_io_em["in_EM_RY_sheetname"] = in_EM_RY_sheetname
    dict_io_em["in_EM_RY_foldername"] = in_EM_foldername
    dict_io_em["in_EM_BY_pathname"] = in_EM_BY_pathname
    dict_io_em["in_EM_RY_pathname"] = in_EM_RY_pathname
    dict_io_em["in_pathname_EM_BY"] = in_pathname_EM_BY
    dict_io_em["in_sheetname_EM_BY"] = in_sheetname_EM_BY
    dict_io_em["in_header_EM_BY"] = in_header_EM_BY
    dict_io_em["in_skiprows_EM_BY"] = in_skiprows_EM_BY
    dict_io_em["in_usecols_EM_BY"] = in_usecols_EM_BY
    dict_io_em["in_col_names_EM_BY"] = in_col_names_EM_BY
    dict_io_em["in_col_dtype_EM_BY"] = in_col_dtype_EM_BY
    dict_io_em["in_pathname_EM_RY"] = in_pathname_EM_RY
    dict_io_em["in_sheetname_EM_RY"] = in_sheetname_EM_RY
    dict_io_em["in_header_EM_RY"] = in_header_EM_RY
    dict_io_em["in_skiprows_EM_RY"] = in_skiprows_EM_RY
    dict_io_em["in_usecols_EM_RY"] = in_usecols_EM_RY
    dict_io_em["in_col_names_EM_RY"] = in_col_names_EM_RY
    dict_io_em["in_col_dtype_EM_RY"] = in_col_dtype_EM_RY
    dict_io_em["in_col_unique_em"] = in_col_unique_em
    dict_io_em["in_col_from_main_proc"] = in_col_from_main_proc
    
    dict_io_em["in_usecols_EM_BY_nomenc"] = in_usecols_EM_BY_nomenc
    dict_io_em["in_usecols_EM_BY_val"] = in_usecols_EM_BY_val
    dict_io_em["in_usecols_EM_RY_nomenc"] = in_usecols_EM_RY_nomenc
    dict_io_em["in_usecols_EM_RY_val"] = in_usecols_EM_RY_val
    dict_io_em["in_col_names_EM_RY_nomenc"] = in_col_names_EM_BY_nomenc
    dict_io_em["in_col_dtype_EM_RY"] = in_col_dtype_EM_BY_nomenc
    
    dict_io_em["in_col_names_comp"] = ["NOx", "NMVOC", "SOx", "NH3", "PM2.5", "PM10"]
    
    return dict_io_em


