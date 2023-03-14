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
from numbers import Number

import utils_constant as const




def check_duplicate(
        df: pd.DataFrame,
        in_pathname: str,
        in_sheetname: str,
        df_str_name: str,
        in_col_unique: list,
        check_file,
        ) -> None:

    """Check for the presence of duplicate rows.
    
    A duplicate is found based on matches between one or multiple specified columns.
    
    Args:
        df: DataFrame to be checked.
        in_pathname: path name of df. Used for QC.
        in_sheetname: sheet name of df. Used for QC.
        df_str_name: name of the dataframe as a string. Used for QC.
        in_col_unique: list of column names for which each row must be unique.
        check_file: already open text file where to write infos for QC.
        
    Return:
        None.
        
    Raises:
        Error in case a duplicate is found. df is not modified, duplicates are not removed.
        
    """

    duplicateRows = df[df.duplicated(subset = in_col_unique, keep = False)]
    if len(duplicateRows)>0:
        
        if in_pathname is not None and in_sheetname is not None:
            check_file.write("There were duplicated rows in file <{}>, tab <{}>:\n".format(in_pathname, in_sheetname))
        elif df_str_name is not None:
            check_file.write("There were duplicated rows in DataFrame <{}>.\n".format(df_str_name))
        else:
            check_file.write("There were duplicated rows.\n")
            
        check_file.write("Code\tName\tCompound\tResource\n")
        for i_duplicate in range(len(duplicateRows["proc_id"])):
            check_file.write("{}\t{}\t{}\t{}\n".format(duplicateRows["proc_id"].iloc[i_duplicate], duplicateRows["name"].iloc[i_duplicate], duplicateRows["comp_id"].iloc[i_duplicate], duplicateRows["reso_id"].iloc[i_duplicate]))
        check_file.close()
        raise ValueError("There were duplicated rows in file <{}>, tab <{}>.\n".format(in_pathname, in_sheetname))
    else:
        if in_pathname is not None and in_sheetname is not None:
            check_file.write("Found no duplicated rows in file <{}>, tab <{}>.\n".format(in_pathname, in_sheetname))
        elif df_str_name is not None:
            check_file.write("Found no duplicated rows in DataFrame <{}>.\n".format(df_str_name))
        #else: no error so do nothing.

    return None

def check_reso_id_default(df: pd.DataFrame) -> pd.DataFrame:
    """Check input string for resource and fill with default string in case of blank.
    
    Args:
        df: input DataFrame.
        
    Returns:
        df, with updated strings for resources.
        
    """    
    
    string_intermediate_total = const.RESO_TOTAL_INTERMEDIATE #"All resources"
    string_total = const.RESO_TOTAL
        
    if "reso_id" not in df.columns:
        df["reso_id"] = string_total
    else:
        #Fill empty resource by "All resources"
        count_empty = 0
        for i in range(len(df["reso_id"])):
            if df["reso_id"].iloc[i] == "" or df["reso_id"].iloc[i] == "MI" or pd.isnull(df["reso_id"].iloc[i]):
                count_empty += 1
                df["reso_id"].iloc[i] = string_intermediate_total
        if count_empty == len(df):
            #the column exists but all inputs are empty, assign aggregated value to all
            df["reso_id"] = string_total
            
    return df

def select_fuel_sold_used(
        df: pd.DataFrame, 
        use_fuel_used: bool,
        check_file,
        ) -> pd.DataFrame:
    """Remove source categories (rows) that do not correspond to the chosen method.
    
    The chosen methods are: fuel sold or fuel used.
    In the CLRTAP nomenclature, names of source categories for fuel used contain the string "(fu)".
    This feature is used here to distinguish between fuel used and fuel sold source categories.
    Noe that this distinction is applicable only for the source categories listed in:
        const.PROC_CODE_FUEL_SOLD
        const.PROC_CODE_FUEL_USED
        
    For greenhouse gas inventory, a priori the method should be fuel sold.
    For safety reason, the fuel sold method is applied only if the corresponding
    names for the source categories are found.
    
    This function does not check that each code for fuel used has an exact match for fuel sold
    (or vice versa),
    this would require to check the resources and compounds as well.
    
    """
    
    #print("check fuel sold fuel used, set to {}.".format(use_fuel_used))

    #Fuel sold vs fuel used: keep correct nomenclature names and drop the others
    if "proc_code" in df.columns:
        index_fuel_sold_len = len(df.index[df["proc_code"].isin(const.PROC_CODE_FUEL_SOLD)].tolist())
        index_fuel_used_len = len(df.index[df["proc_code"].isin(const.PROC_CODE_FUEL_USED)].tolist())
        
        #print("number of found indexes for fuel sold: {}.".format(len(index_fuel_sold)))
        #print("number of found indexes for fuel used: {}.".format(len(index_fuel_used)))

        if use_fuel_used:
            if index_fuel_used_len == 0 and index_fuel_sold_len > 0:
                check_file.write(
                        "The chosen inventory type is fuel used but no source categories were found for fuel used. Please check your input files or try setting use_fuel_used to False."
                        )
                check_file.close()
                raise ValueError(
                        "The chosen inventory type is fuel used but no source categories were found for fuel used. Please check your input files or try setting use_fuel_used to False."
                        )

            elif index_fuel_used_len > 0 and index_fuel_used_len < index_fuel_sold_len:
                check_file.write(
                        "The chosen inventory type is fuel used. Source categories were found for fuel sold but (some) corresponding source categories were not found for fuel used. Please check your input files."
                        )
                check_file.close()
                raise ValueError("The chosen inventory type is fuel used. Source categories were found for fuel sold but (some) corresponding source categories were not found for fuel used. Please check your input files.")
            
            else:
                #drop rows that contain any value in the list
                #https://www.statology.org/pandas-drop-rows-with-value/
                df = df[df["proc_code"].isin(const.PROC_CODE_FUEL_SOLD) == False]

        else: #use fuel sold
            if index_fuel_sold_len == 0 and index_fuel_used_len > 0:
                check_file.write(
                        "The chosen inventory type is fuel sold but no source categories were found for fuel sold, while at least one was found for fuel used. Please check your input files or try setting use_fuel_used to True."
                        )
                check_file.close()
                raise ValueError(
                        "The chosen inventory type is fuel sold but no source categories were found for fuel sold, while at least one was found for fuel used. Please check your input files or try setting use_fuel_used to True."
                        )

            elif index_fuel_sold_len > 0 and index_fuel_sold_len < index_fuel_used_len:
                check_file.write(
                        "The chosen inventory type is fuel sold. Source categories were found for fuel used but (some) corresponding source categories were not found for fuel sold. Please check your input files."
                        )
                check_file.close()
                raise ValueError(
                        "The chosen inventory type is fuel sold. Source categories were found for fuel used but (some) corresponding source categories were not found for fuel sold. Please check your input files."
                        )
            else:
                #drop rows that contain any value in the list
                #https://www.statology.org/pandas-drop-rows-with-value/
                df = df[df["proc_code"].isin(const.PROC_CODE_FUEL_USED) == False]
                
    return df


def check_main(
        df: pd.DataFrame,
        df_main: pd.DataFrame, #this is the table containing the defintion of the text, i.e. list of allowed text.
        col_left: list,
        col_right: list,
        check_file,
        ) -> pd.DataFrame:
    
    """Checks if values are contained in a list of main (allowed) values.

    Check if values in a specified column of a pandas DataFrame
    can all be found in the values listed in a specified column of (another) DataFrame.
    This is equivalent to checking in SQL that all values of a column 
    are secondary keys of a primary key.
    
    Args:
        df: pandas DataFrame containing the column to check.
        df_main: pandas DataFrame containing the main or primary column.
        col_left: name of the column to check in df.
        col_right: name of the column to use as primary in df_main.
        check_file: file where to write issues for QC.
    
    Returns: 
        df: pandas DataFrame without rows where the value was not found in the primary column.
        
    Raises:
        None.
    """
    
    df_test = pd.merge(
            df[col_left], #df[[col_left]],
            df_main[col_right], #df_main[[col_right]],
            left_on = col_left, #[col_left]
            right_on = col_right, #[col_right]
            how = "left",
            indicator = "exists_main",
            copy = False,
            )
    
    count_not_found = 0

    #add column to show if each row in first DataFrame exists in second
    df_test["exists_main"] = np.where(df_test["exists_main"] == "both", True, False)
    
    for i in range(len(df_test["exists_main"])):
        if not df_test["exists_main"].iloc[i]:
            check_file.write("The string was not recognised for input <{}> at line <{}>.\n".format(df[col_left].iloc[i], i))
            count_not_found += 1
    #drop rows without match in the official nomenclature
    df =df[df_test["exists_main"] == True]
    df.reset_index(drop = True)
    
    if count_not_found > 0:
        check_file.write("There were unrecognised entries, please consult comments from above.")
        check_file.close()
        raise ValueError("There were unrecognised entries, please consult the check file.")
    
    return df


def merge_with_main(
        df: pd.DataFrame,
        df_main: pd.DataFrame,
        merge_with_main_left,
        merge_with_main_right,
        check_file,
        ) -> pd.DataFrame:
    """Merge two DataFrames based on specific merge columns, equivalent to SQL join.

    Merge two pandas DataFrame based on match between values in specified columns
    of each DataFrame.
    This is equivalent to joining two tables in SQL 
    based on a secondary and a primary column.
    df contain a column which values are considered equivalent to a secondary key in SQL,
    i.e. they all refer to the primary key column.
    The primary key column may contain values not present in the secondary key,
    but the reverse is not allowed.
    
    Args:
        df: pandas DataFrame containing the column with values of type "secondary key".
        df_main: pandas DataFrame containing the main or "primary key" column.
        col_left: name of the column containing the values of type "secondary key".
        col_right: name of the column to use as primary in df_main.
        check_file: file where to write issues.
    
    Returns:
        df: pandas DataFrame without rows where the value was not found in the primary column.
        
    Raises:
        None.
    """
    
    #---------------------------------------------
    #CHECK MATCH WITH MAIN TABLE AND DROP ROWS WITHOUT MATCH
    #---------------------------------------------

    df = pd.merge(
            df, 
            df_main, 
            left_on = merge_with_main_left,
            right_on = merge_with_main_right,
            how="left", 
            indicator="exists_main",
            copy = False
            #,suffixes = []
            ) #, validate = 'one_to_one'
    
    #add column to show if each row in first DataFrame exists in second
    df["exists_main"] = np.where(df["exists_main"] == "both", True, False)
    
    count_not_found = 0
    for i in range(len(df["exists_main"])):
        if not df["exists_main"].iloc[i]:
            count_not_found += 1
            if merge_with_main_left == "comp_id":
                check_file.write("The compound was not recognised: <{}>.\n".format(df[merge_with_main_left].iloc[i]))
            elif merge_with_main_left == "reso_id":
                check_file.write("The resource was not recognised: <{}>.\n".format(df[merge_with_main_left].iloc[i]))
            #else:
            #    check_file.write("The compound was not recognised for input code <{}>.\n".format(df["proc_id"].iloc[i]))
                
    #drop rows without match in the official nomenclature
    if count_not_found > 0:
        df =df[df["exists_main"] == True].reset_index(drop = True)

    #---------------------------------------------
    #FINISH PREPARATION OF COLUMN STRUCTURE FOR LATER MERGES
    #---------------------------------------------
            
    #drop columns
    #nomenc_code is same as code    
    df.drop(["exists_main"], axis=1, inplace=True)

    return df

def merge_with_proc(
        df: pd.DataFrame,
        df_proc: pd.DataFrame,
        col_from_main, #columns to use from the main (primary) df
        col_merge_left_on, #cols to merge on from df
        col_merge_right_on, #cols to merge on from primary df
        col_merge_drop_left,
        col_name_proc_id,
        check_file,
        ) -> pd.DataFrame:
    
    """Merge a DataFrame with the primary DataFrame for process nomenclature.
    
    Merge from any df the columns proc_class and proc_code
    (in the future, maybe also proc_name)
    with, from the primary df for process nomenclature,
    the columns proc_class, proc_code (to match) and proc_id.
    Then keep only proc_id as unique id column for process identification.
    The string in this column is a concatenation of proc_class, proc_code and proc_name.    
    We do this in order to keep only one column to identify the process,
    instead of the two we have in the input files (proc_class, proc_code).
    We keep 2 columns in the input files to simplify preparation work.
    
    Args:
        df: df containing the "secondary column" (in a SQL sense)
        df_proc: primary df for process nomenclature
        col_from_main: columns to use from the main (primary) df
        col_merge_left_on: cols to merge on from df
        col_merge_right_on: cols to merge on from primary df
        col_merge_drop_left: cols from df to drop after the merge
        col_name_proc_id: column name to apply to column "proc_id" after the merge.
            This is needed in case this function is used where df is an aggregation tree,
            because "proc_id" must be "child_proc_id" or "parent_proc_id".
        check_file:
            
    Returns:
        df: same as df but after the merge.
        
    """
    
    #---------------------------------------------
    #CHECK MATCH WITH NOMENCLATURE AND DROP ROWS WITHOUT MATCH
    #---------------------------------------------
    if col_name_proc_id is not None:
        #rename columns befor merge, special to merge aggregatio tree for proc with main_proc
        #https://www.statology.org/pandas-rename-columns/
        #df.rename(columns = {'old_col1':'new_col1', 'old_col2':'new_col2'}, inplace = True)
        for i_col in range(len(col_merge_left_on)):
            df.rename(columns = {col_merge_left_on[i_col]:col_merge_right_on[i_col]}, inplace = True)
        col_merge_left_on = col_merge_right_on.copy()


    df = pd.merge(
            df, 
            df_proc[col_from_main], #["proc_id", "proc_class", "proc_code"]
            left_on = col_merge_left_on, #["proc_class", "proc_code"]
            right_on = col_merge_right_on, #["proc_class", "proc_code"]
            how="left", 
            indicator="exists_proc",
            copy = False
            #,suffixes = []
            ) #, validate = 'one_to_one'
    
    #add column to show if each row in first DataFrame exists in second
    df["exists_proc"] = np.where(df["exists_proc"] == "both", True, False)
    
    for i in range(len(df["exists_proc"])):
        if not df["exists_proc"].iloc[i]:
            if "proc_class" in col_merge_left_on and "proc_code" in col_merge_left_on and "proc_name" in col_merge_left_on:
                check_file.write("The nomenclature was not recognised for input code <{} {}> with input name <{}>.\n".format(df["proc_class"].iloc[i], df["proc_code"].iloc[i], df["proc_name"].iloc[i]))
            elif "proc_code" in col_merge_left_on:
                check_file.write("The nomenclature was not recognised for input code <{}>.\n".format(df["proc_code"].iloc[i]))
                
    #drop rows without match in the official nomenclature
    df =df[df["exists_proc"] == True].reset_index(drop = True)   
    df.drop(["exists_proc"], axis=1, inplace=True)

    #remove all original columns on the left side of the merge (= from df)
    if col_merge_drop_left is None:
        for col_name in col_merge_left_on:
            #this is the initial merge type to get proc_id from primary df.
            #Drop all other redundant columns.
            if col_name in df.columns:
                df.drop([col_name], axis=1, inplace=True)
    else:
        for col_name in col_merge_drop_left:
            if col_name in df.columns:
                df.drop([col_name], axis=1, inplace=True)
        
    if col_name_proc_id is not None:
        #https://www.statology.org/pandas-rename-columns/
        #df.rename(columns = {'old_col1':'new_col1', 'old_col2':'new_col2'}, inplace = True)
        df.rename(columns = {"proc_id":col_name_proc_id}, inplace = True)
                   
    return df



def read_excel_nomenc_def(
        in_pathname,
        in_sheetname,
        in_header,
        in_skiprows,
        in_usecols,
        in_col_names,
        in_col_dtype,
        in_col_unique,
        col_from_main_proc,
        col_merge_left_on_proc,
        col_merge_right_on_proc,
        df_proc: pd.DataFrame,
        col_check_left_on_comp,
        col_check_right_on_comp,
        df_comp: pd.DataFrame,
        col_check_left_on_reso,
        col_check_right_on_reso,
        df_reso: pd.DataFrame,
        comp_string,
        use_fuel_used,
        check_file,
        ) -> pd.DataFrame:
    """read columns defining source categories.
    
    For the general case, these columns are: proc_id (or proc_name, proc_code, proc_class),
    comp_id, reso_id.
    """

    #---------------------------------------------
    #READ INPUT VALUES AS STRING AND DROP ROWS WITH MISSING CODE
    #---------------------------------------------
    df = pd.read_excel(
            io = in_pathname, 
            sheetname = in_sheetname, #Warning! for newer pandas version use sheet_name
            header = in_header, 
            skiprows = in_skiprows,
            usecols = in_usecols,
            names = in_col_names,
            dtype = in_col_dtype,
            keep_default_na = False, #required otherwise "NA" recognised as nan value
            #engine = "openpyxl"
            )
    
    #Special manual modification for pollutant-type input emission file,
    #needed because the NFR table is read and there is no column with the nomenclature class.
    if "proc_class" not in in_col_names:
        df["proc_class"] = "NFR"
    #To read NFR table: there is no column with a compound name.
    if "comp_id" not in in_col_names and comp_string is not None:
        df["comp_id"] = comp_string
        
    #remove nan rows where the code is nan or the process class (CRT, NFR, etc.) is nan
    df.dropna(subset=["proc_code"], inplace=True) #.reset_index(drop = True)
    df.dropna(subset=["proc_class"], inplace=True) #.reset_index(drop = True)

    #Fuel sold vs fuel used: keep correct nomenclature names and drop the others
    df = select_fuel_sold_used(df, use_fuel_used, check_file)
    
    
    #---------------------------------------------
    #CHECK MATCH WITH NOMENCLATURE AND DROP ROWS WITHOUT MATCH
    #---------------------------------------------
    #DONE GMY 20230210: only check that nomenclature exists, do not merge
    #merge with cols: proc_id, proc_code, proc_name
    
    df = merge_with_proc(
        df = df,
        df_proc = df_proc,
        col_from_main = col_from_main_proc, #columns to use from the main (primary) df
        col_merge_left_on = col_merge_left_on_proc, #cols to merge on from df
        col_merge_right_on = col_merge_right_on_proc, #cols to merge on from primary df
        col_merge_drop_left = None,
        col_name_proc_id = None,
        check_file = check_file,
        )


    
    #Only check that compound exists, do not merge
    df = check_main(
            df = df,
            df_main = df_comp,
            col_left = col_check_left_on_comp,
            col_right = col_check_right_on_comp,
            check_file = check_file,
            )

    #---------------------------------------------
    #FINISH PREPARATION OF COLUMN STRUCTURE FOR LATER MERGES
    #---------------------------------------------
    #fill in with default value for reso_id in case input is empty
    df = check_reso_id_default(df)
    
    df = check_main(
            df = df,
            df_main = df_reso,
            col_left = col_check_left_on_reso,
            col_right = col_check_right_on_reso,
            check_file = check_file,
            )   

    #find duplicated rows               
    check_duplicate(
        df = df,
        in_pathname = in_pathname,
        in_sheetname = in_sheetname,
        df_str_name = None,
        in_col_unique = ["proc_id", "comp_id", "reso_id"], #in_col_unique,
        check_file = check_file,                
            )
        
    return df


def input_em_data_check(
        df: pd.DataFrame,
        input_year: str,
        check_file,
        ) -> pd.DataFrame:

    """Check input emissions (notation keys or values).


    Args:
        df: pandas DataFrame containing the emissions.
        input_year: string with the input year (BY, RY) used for documentation.
        check_file: text file to document the checks.
        
    Returns:
        df.

    Raises:
        None.

    """
    
    #Check for notation keys or valid numeric values
    #create new col: "EM" contains numeric values
    df["EM"] = [np.float(val) if (isinstance(val, Number) and not pd.isnull(val)) else np.float(0.0) for val in df["EM_status"]]
   
    for i in range(len(df["EM_status"])):
        #if df["EM_status"][i] in ["NA", "NO", "NE", "C", "IE"]:
            #all good, do nothing
        val = df.iloc[i, df.columns.get_loc("EM_status")]
        #print("val read for emission: " + str(val))
        if val in const.NOTATION_KEY:
            #status = val.copy()
            #print("val recognised as notation key: " + str(val))
            check_file.write("Code <{}>, compound <{}>, resource <{}>, <{}>: emission input recognised as notation key: {}.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], input_year, val))
        else: #if val not in const.NOTATION_KEY:
            #DONE GMY 20230122: in pd.read_excel, use option keep_default_na = False
            #otherwise it seems that notation key "NA" is assimilated to nan.
            
            if pd.isnull(val):
                status = "MI"
            if not pd.isnull(val) and isinstance(val, Number):
                status = "ES"
            else:
                status = "MI"
            df.iloc[i, df.columns.get_loc("EM_status")] = status
            if status == "MI":
                check_file.write("Notation key or value not recognised for emission at line {}: {}.\n".format(i, val))
            if df.iloc[i, df.columns.get_loc("EM")] == np.float(0.0):
                check_file.write("Code <{}>, compound <{}>, resource <{}>, <{}>: emission is zero! Please write notation key instead.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], input_year))
    
    no_valid_input = sum([1 if val in const.NOTATION_KEY else 0 for val in df["EM_status"]])
    df["EM_is_num"] = [True if val in const.NOTATION_KEY else False for val in df["EM_status"]]
    check_file.write("Found {} numeric entries or notation keys for EM for {}.\n".format(no_valid_input, input_year))  

    
    return df



def input_u_data_preparation(
        df: pd.DataFrame, 
        input_type: str, 
        input_year: str,
        check_file,
        ) -> pd.DataFrame:
    """Check that input parameters for uncertainties are statistically valid.
    
    :arg df: pandas data frame containing row data
    :arg input_type: string: AD, EF, EM
    :arg input_year: string: BY, RY.
    :arg check_file
    
    """
    
    u_dist = "u{}_dist".format(input_type)
    u_status = "u{}_status".format(input_type)
    u_sym_f = "u{}_sym_f".format(input_type)
    u_lower_f = "u{}_lower_f".format(input_type)
    u_upper_f = "u{}_upper_f".format(input_type)
    u_is_num = "u{}_is_num".format(input_type)
    u_corr = "u{}_corr".format(input_type) #correlation between base year and reporting year
    u_ref = "u{}_ref".format(input_type)

    if u_ref not in df.columns:
        df[u_ref] = None

 
    df_len = len(df)

    #From a pandas vector containing
    #text of distribution as from input uncertainty file, 
    #assign code for distribution type.
    #If the text is not recognised, the assigned distribution is None.
    
    for i in range(df_len):
        dist_string = df[u_dist].iloc[i]
        #print(dist_string)
        #dist_string = df.iloc[i]
        #dist_string= df.iloc[i, df.columns.get_loc(col_name)]

        #if dist_string in const.NOTATION_KEY:
        #    dist_val = np.nan
        if dist_string == "normal": 
            dist_val = const.DIST_NORMAL
        elif dist_string == "uniform":
            dist_val = const.DIST_UNIFORM
        elif dist_string == "triangle":
            dist_val = const.DIST_TRIANGULAR
        elif dist_string == "lognormal":
            dist_val = const.DIST_LOGNORMAL
        elif dist_string == "gamma":
            dist_val = const.DIST_GAMMA
        elif dist_string == "fractile":
            dist_val = const.DIST_FRACTILE
        else:
            dist_val = int(-1) #np.nan #None
        df[u_dist].iloc[i] = dist_val


    if sum([0 if np.isnan(df[u_dist].iloc[i]) else 1 for i in range(df_len)]) > 0:
        df[u_dist] = df[u_dist].astype(str).astype(int) #.astype(float)
    
    index_u_dist_sym = df.index[(
            (df[u_dist] == const.DIST_NORMAL) | 
            (df[u_dist] == const.DIST_UNIFORM) | 
            (df[u_dist] == const.DIST_GAMMA))
        ].tolist()
    index_u_dist_notsym = [i for i in range(df_len) if i not in index_u_dist_sym] #will contain as well all non-recognised distributions

    #print("index_u_dist_sym")
    #print(index_u_dist_sym)
    
    #print("index_u_dist_notsym")
    #print(index_u_dist_notsym)
    
    df[u_status] = "MI" #for missing information, by default
    
    if len(index_u_dist_sym) > 0:
        for i in index_u_dist_sym:
            if pd.isnull(df[u_sym_f].iloc[i]): 
                val = "MI"
            elif isinstance(df[u_sym_f].iloc[i], Number): 
                val = "ES"
            elif df[u_sym_f].iloc[i] in const.NOTATION_KEY: 
                val = str(df[u_sym_f].iloc[i]) #str(df[u_sym_f].iloc[i].copy())
            else:
                val = "MI"
            df[u_status].iloc[i] = val

            if not df[u_dist].iloc[i] == int(-1) and not pd.isnull(df[u_dist].iloc[i]):
                if val == "MI":
                    #Quality check: distribution given (and symetric) but uncertainty value is missing
                    check_file.write("{}, {}, {}: distribution type is <{}> but input uncertainty value is missing <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_sym_f].iloc[i]))
                if val == "ES" and df[u_sym_f].iloc[i] <= 0:
                    #Quality check: distribution given (and symetric) but uncertainty value is zero
                    check_file.write("{}, {}, {}>: distribution type is <{}> but input uncertainty value is <= zero <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_sym_f].iloc[i]))
            if (pd.isnull(df[u_dist].iloc[i]) or df[u_dist].iloc[i] == int(-1)) and val == "ES":
                #Quality check: uncertainty value is > 0 but distribution type is not recognised
                check_file.write("{}, {}, {}>: distribution type is not recognised <{}> but uncertainty value is > 0 <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i]), df[u_sym_f].iloc[i])
    
    if len(index_u_dist_notsym) > 0:
        
        for i in index_u_dist_notsym:
            if pd.isnull(df[u_lower_f].iloc[i]) or pd.isnull(df[u_upper_f].iloc[i]): 
                val = "MI"
            elif isinstance(df[u_lower_f].iloc[i], Number) and isinstance(df[u_upper_f].iloc[i], Number): 
                val = "ES"
            elif df[u_lower_f].iloc[i] in const.NOTATION_KEY and df[u_lower_f].iloc[i] == df[u_upper_f].iloc[i]: 
                val = str(df[u_lower_f].iloc[i]) #str(df[u_lower_f].iloc[i].copy())
            else:
                val = "MI"
            df[u_status].iloc[i] = val

            if not df[u_dist].iloc[i] == int(-1) and not pd.isnull(df[u_dist].iloc[i]):
                if val == "MI":
                    #Quality check: distribution given (and not symetric) but uncertainty value is missing
                    check_file.write("{}, {}, {}: distribution type is <{}> but input uncertainty value is missing <{}> <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_lower_f].iloc[i], df[u_upper_f].iloc[i]))
                if val == "ES" and df[u_lower_f].iloc[i] <= 0:
                    #Quality check: distribution given (and not symetric) but uncertainty value is zero for lower edge
                    check_file.write("{}, {}, {}: distribution type is <{}> but input uncertainty value for lower edge is <= zero <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_lower_f].iloc[i]))
                if val == "ES" and df[u_upper_f].iloc[i] <= 0:
                    #Quality check: distribution given (and not symetric) but uncertainty value is zero for upper edge
                    check_file.write("{}, {}, {}: distribution type is <{}> but input uncertainty value for upper edge is <= zero <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_upper_f].iloc[i]))

                #TODO GMY 20230210 check that input parameters are valid for chosen distribution type
                
                
                #Check that parameters for triangular distribution are valid
                if val == "ES" and df[u_dist].iloc[i] == const.DIST_TRIANGULAR:
                    df[u_dist].iloc[i], df[u_lower_f].iloc[i], df[u_upper_f].iloc[i] = check_dist_triangular(
                            df[u_lower_f].iloc[i],
                            df[u_upper_f].iloc[i],
                            df["proc_id"].iloc[i],
                            df["comp_id"].iloc[i],
                            df["reso_id"].iloc[i], 
                            "RY",
                            "EF",
                            check_file,
                            )


            if (pd.isnull(df[u_dist].iloc[i]) or df[u_dist].iloc[i] == int(-1)) and val == "ES":
                #Quality check: distribution type is not recognised but uncertainty value is > 0 for lower edge or upper edge
                check_file.write("{}, {}, {}: distribution type is not recognised <{}> but uncertainty value is > 0 for lower edge <{}> or upper edge <{}>.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i], df[u_dist].iloc[i], df[u_lower_f].iloc[i], df[u_upper_f].iloc[i]))


    
    #Quality check: the input uncertainty is valid if the distribution type is valid and the input numeric values are valid.
    df[u_is_num] = [True if df[u_status].iloc[i] == "ES" and not pd.isnull(df[u_dist].iloc[i]) else False for i in range(df_len)]    
    #next line does not work: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all()
    #df[u_is_num] = np.where(((df[u_status] == "ES") & (not pd.isnull(df[u_dist]))), True, False)

    check_file.write("Found {} numeric entries for u_{}_{}.\n".format(np.nansum(np.where(df[u_is_num], np.int(1), np.int(0))), input_type, input_year))  
   
    #replace list comprehension by where function?
    df[u_sym_f] = [np.float(val) if (isinstance(val, Number) and not pd.isnull(val)) else np.float(0.0) for val in df[u_sym_f].copy()]
    df[u_lower_f] = [np.float(val) if (isinstance(val, Number) and not pd.isnull(val)) else np.float(0.0) for val in df[u_lower_f].copy()]
    df[u_upper_f] = [np.float(val) if (isinstance(val, Number) and not pd.isnull(val)) else np.float(0.0) for val in df[u_upper_f].copy()]
    
    #For all distribution types, convert input in percent to fraction
    df[u_sym_f] = df[u_sym_f] / float(100.0)
    df[u_lower_f] = df[u_lower_f] / float(100.0)
    df[u_upper_f] = df[u_upper_f] / float(100.0)

    #For symetric distribution types, we need to transform a 95% confidence interval to a standard deviation
    #because according to metrology standards, the variance (square of standard deviation) should be propagated, not the 95% confidence interval.
    df[u_sym_f].iloc[index_u_dist_sym] = df[u_sym_f].iloc[index_u_dist_sym] / const.FACTOR_U_DIST_95_PERCENT
    df[u_lower_f].iloc[index_u_dist_sym] = df[u_sym_f].iloc[index_u_dist_sym]
    df[u_upper_f].iloc[index_u_dist_sym] = df[u_sym_f].iloc[index_u_dist_sym]

    #For the triangular distribution, do not divide by the coverage factor const.FACTOR_U_DIST_95_PERCENT.
    #We need to keep the exact edges of the distribution.
        

    df[u_corr] = [True if val == const.STRING_CORRELATED else False for val in df[u_corr]]
    
    return df


def input_u_data_check_completeness_per_year(
        df: pd.DataFrame,
        input_year: str,
        check_file,
        ) -> pd.DataFrame:
    """
    Perform quality checks on the input uncertainties for AD, EF and EM for a given year (BY or RY).
    
    Args:
        df: pandas DataFrame containing values to be checked.
        input_year: string used to write in the chek_file, BY or RY.
        check_file: file where results of checks are written for QC.
        
    Returns:
        df: same as input df but with updated values if required.
        
    Raises:
        None.
        
    """

    df["u_is_num"] = True
    for i in range(len(df)):

        #input valid for nothing
        if not df["uAD_is_num"].iloc[i] and not df["uEF_is_num"].iloc[i] and not df["uEM_is_num"].iloc[i]:
            df["u_is_num"].iloc[i] = False
            check_file.write("Code <{}>, {}: input uncertainty is valid for neither AD, nor EF nor EM.\n".format(df["proc_id"].iloc[i], input_year))

        #input valid for AD only
        if df["uAD_is_num"].iloc[i] and not df["uEF_is_num"].iloc[i] and not df["uEM_is_num"].iloc[i]:
            df["u_is_num"].iloc[i] = False
            check_file.write("Code <{}>, {}: input uncertainty is valid for AD but not for EF or EM.\n".format(df["proc_id"].iloc[i], input_year))
    
        #input valid for EF only
        if not df["uAD_is_num"].iloc[i] and df["uEF_is_num"].iloc[i] and not df["uEM_is_num"].iloc[i]:
            df["u_is_num"].iloc[i] = False
            check_file.write("Code <{}>, {}: input uncertainty is valid for EF but not for AD or EM.\n".format(df["proc_id"].iloc[i], input_year))
    
        #input valid for AD and EM but not for EF: input for AD will be ignored, only input for EM will be used
        if df["uAD_is_num"].iloc[i] and not df["uEF_is_num"].iloc[i] and df["uEM_is_num"].iloc[i]:
            df["uAD_is_num"].iloc[i] = False
            df["uAD_status"].iloc[i] = "MI"
            check_file.write("Code <{}>, {}: input uncertainty is valid for AD and EM but not for EF, input for EM only will be used.\n".format(df["proc_id"].iloc[i], input_year))
    
        #input valid for EF and EM but not for AD: inut for EF will be ignored, only input for EM will be used
        if not df["uAD_is_num"].iloc[i] and df["uEF_is_num"].iloc[i] and df["uEM_is_num"].iloc[i]:
            df["uEF_is_num"].iloc[i] = False
            df["uEF_status"].iloc[i] = "MI"
            check_file.write("Code <{}>, {}: input uncertainty is valid for EF and EM but not for AD, input for EM only will be used.\n".format(df["proc_id"].iloc[i], input_year))

        #input valud for AD, EF, EM: use AD and EF only.    
        if df["uAD_is_num"].iloc[i] and df["uEF_is_num"].iloc[i] and df["uEM_is_num"].iloc[i]:
            df["uEM_is_num"].iloc[i] = False
            df["uEM_status"].iloc[i] = "MI"
            check_file.write("Code <{}>, {}: input uncertainty is valid for AD, EF and EM: input for EM will be ignored.\n".format(df["proc_id"].iloc[i], input_year))
    
    return df


def input_u_data_check_correlation(
        df: pd.DataFrame,
        check_file,
        ) -> pd.DataFrame:
    """Check that if input u for BY and RY are correlated, input dist and values must be exactly the same.
    
    Otherwise, set data as not correlated between base year and reporting year.
    
    Args:
        df: pandas DataFrame containing values to be checked.
        check_file: file where results of checks are written for QC.
        
    Returns:
        df: same as input df but with updated values for correlation status if required.
        
    Raises:
        None.
    """

    for i in range(len(df)):
        
        if df["uAD_dist_BY"].iloc[i] != df["uAD_dist_RY"].iloc[i]:
            if df["uAD_corr"].iloc[i]:
                df["uAD_corr"].iloc[i] = False
                check_file.write("Code <{}>: input uncertainties for BY and RY are correlated but distributions for BY and RY are not identical, correlation set to False.\n".format(df["proc_id"].iloc[i]))
            else:
                check_file.write("Code <{}>: use specific input uncertainty distribution for BY.\n".format(df["proc_id"].iloc[i]))
    
        if df["uAD_lower_f_BY"].iloc[i] != df["uAD_lower_f_RY"].iloc[i]:
            if df["uAD_corr"].iloc[i]:
                df["uAD_corr"].iloc[i] = False
                check_file.write("Code <{}>: input uncertainties for BY and RY are correlated but lower uncertainty values for BY and RY are not identical, correlation set to False.\n".format(df["proc_id"].iloc[i]))
            else:
                check_file.write("Code <{}>: use specific input uncertainty value for BY.\n".format(df["proc_id"].iloc[i]))
    
        if df["uAD_upper_f_BY"].iloc[i] != df["uAD_upper_f_RY"].iloc[i]:
            if df["uAD_corr"].iloc[i]:
                df["uAD_corr"].iloc[i] = False
                check_file.write("Code <{}>: input uncertainties for BY and RY are correlated but upper uncertainty values for BY and RY are not identical, correlation set to False.\n".format(df["proc_id"].iloc[i]))
            else:
                check_file.write("Code <{}>: use specific input uncertainty value for BY.\n".format(df["proc_id"].iloc[i]))
    
        if not df["u_is_num_BY"].iloc[i]:
            df["u_is_num"].iloc[i] = False
            check_file.write("Code <{}>, compound <{}>, resource <{}>: no input uncertainty value for BY.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i]))
    
        if not df["u_is_num_RY"].iloc[i]:
            df["u_is_num"].iloc[i] = False
            check_file.write("Code <{}>, compound <{}>, resource <{}>: no input uncertainty value for RY.\n".format(df["proc_id"].iloc[i], df["comp_id"].iloc[i], df["reso_id"].iloc[i]))
    
    return df
    
                    


def check_dist_triangular(
        u_lower_p,
        u_upper_p,
        proc: str,
        comp: str, #used to give input line in case the compound is not known (old method).
        reso: str,
        year_string: str, #BY or RY,
        type_string: str,  #AD, EF or EM
        check_file,
        ):
    #XXX Check if the input parameters for the triangular distribution are statistically valid
    """Check if the input parameters for the triangular distribution are statistically valid
    
    """
    
    dist = const.DIST_TRIANGULAR
    if comp != "":
        comp = " " + comp
    if reso != "":
        reso = " " + reso
    u_edge_lower = float(1.0) - u_lower_p/float(100.0)
    u_edge_upper = float(1.0) + u_upper_p/float(100.0)
    mode = float(3.0) - u_edge_lower - u_edge_upper
    
    if mode < u_edge_lower or mode > u_edge_upper:
        if mode < u_edge_lower:
            cause_text = "Mode < u_edge_lower: mode - u_edge_lower = {}".format(mode - u_edge_lower)
        elif mode > u_edge_upper:
            cause_text = "Mode > u_edge_upper: mode - u_edge_upper = {}".format(mode - u_edge_upper)
    
        if u_lower_p > u_upper_p:
            #use a normal distribution instead
            dist = const.DIST_NORMAL
            u_upper_p = u_lower_p
            solution_text = "Since lower U > upper U, use normal disttribution instead"
        elif u_lower_p < u_upper_p:
            #use a gamma distribution instead
            dist = const.DIST_GAMMA
            u_lower_p = u_upper_p
            solution_text = "Since lower U > upper U, use gamma distribution instead"
            
        check_file.write("Triangular U input not valid for {} {} {}{}{}. {}. {}.\n".format(year_string, type_string, proc, comp, reso, cause_text, solution_text))
            
    return dist, u_lower_p, u_upper_p



def find_index_inventory_total(
        df: pd.DataFrame,
        proc_id_total: str,
        comp_id_total: str,
        reso_id_total: str,
        text: str,
        check_file,
        ) -> int:
    
    """    Find the index of the DataFrame corresponding to the inventory total emission.
    
    """
    index_total = df.index[((df["proc_id"] == proc_id_total) & (df["comp_id"] == comp_id_total) & (df["reso_id"] == reso_id_total) )].tolist() 
    if len(index_total) == 0:
        check_file.write("Could not find the inventory total in {} results!".format(text))
        check_file.close()
        raise ValueError("Could not find the inventory total in {} results!".format(text))
    elif len(index_total) > 1:
        check_file.write("There were multiple results for the inventory total in {} results: {}.\n".format(text, index_total))
        check_file.close()
        raise ValueError("There were multiple results for the inventory total in {} results: {}.".format(text, index_total))
    index_total = index_total[0]

    return index_total
    