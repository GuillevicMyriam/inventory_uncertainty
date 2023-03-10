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

Created on Wed Sep 29 12:04:04 2021

"""

import numpy as np
import pandas as pd
import random
import utils_constant as const
from scipy.stats import gamma, triang #,norm,  , lognorm




def compute_U_propagation_em_pd(
        df
        ):
    """Compute uncertainty propagation (IPCC guidebook: approach 1)
    
    Compute the uncertainty propagation as described in the IPCC guidebook on uncertainty.
    Note that the IPCC guidebook describes a simplified procedure, as compared to the 
    Guide for uncertainty of Measurements from Bureau International des Poids et Mesures.
    ALL resulting uncertainty values U_lower_p and U_upper_p must be 
    values at 2.5% and 97.5% of the distributions.
    They are NOT edges!
    
    Args:
        df: pandas DataFrame containg all input data
        
    Returns:
        df_u: pandas DataFrame containing the uncertainties according to approach 1.
        
    """
    
    len_df = len(df)
    #https://www.statology.org/pandas-create-dataframe-with-column-names/
    df_u = pd.DataFrame(
            np.float(0.0), #fill all cells with zeros, this is the default result (not nan!)
            columns=[
            "AD_RY_pr_U_lower_p",
            "AD_RY_pr_U_upper_p",
            "AD_BY_pr_U_lower_p",
            "AD_BY_pr_U_upper_p",        
            "EF_RY_pr_U_lower_p",
            "EF_RY_pr_U_upper_p",
            "EF_BY_pr_U_lower_p",
            "EF_BY_pr_U_upper_p",
            "EM_RY_pr_U_lower_p",
            "EM_RY_pr_U_upper_p",
            "EM_BY_pr_U_lower_p",
            "EM_BY_pr_U_upper_p",
            "EM_BY_pr_contrib_var_lower",
            "EM_BY_pr_contrib_var_upper",
            "EM_RY_pr_contrib_var_lower",
            "EM_RY_pr_contrib_var_upper",
            #do not add the following columns here, unnecessary
            #"sens_corr", #sensitivity if correlation between base year and reporting year
            #"sens_no_corr", ##sensitivity if no correlation between base year and reporting year
            #"AD_trend_pr_contrib_var_lower",
            #"AD_trend_pr_contrib_var_upper",
            #"EF_trend_pr_contrib_var_lower",
            #"EF_trend_pr_contrib_var_upper",
            #"EM_trend_pr_contrib_var_lower",
            #"EM_trend_pr_contrib_var_upper",
            ],
            index=range(len_df))

    
    #for each type distribution, compute values at 2.5% and 97.5% of the distribution
    
    #gamma distribution: re-compute lower end border value
    #ppf_edge_lower = const.DIST_PPF_EDGE_LOWER
    #ppf_edge_upper = const.DIST_PPF_EDGE_UPPER
    #assume 2.5% of distribution on left side, 
    #(this might be reduced to
    #because usually gamma dist is non-symetric,
    #but I could not find a way to choose the value then)
            
            
    for i_year in range(2):
        if i_year == int(0):
            input_year = "BY"
            #print("doing for BY")
        elif i_year == int(1):
            input_year = "RY"
            #print("doing for RY")
            
        #print("doing for {}".format(input_year))
        u_AD_is_num = "uAD_is_num_{}".format(input_year)
        u_EF_is_num = "uEF_is_num_{}".format(input_year)
        EM_pr_U_lower_p = "EM_{}_pr_U_lower_p".format(input_year)
        EM_pr_U_upper_p = "EM_{}_pr_U_upper_p".format(input_year)
        AD_pr_U_lower_p = "AD_{}_pr_U_lower_p".format(input_year)
        AD_pr_U_upper_p = "AD_{}_pr_U_upper_p".format(input_year)
        EF_pr_U_lower_p = "EF_{}_pr_U_lower_p".format(input_year)
        EF_pr_U_upper_p = "EF_{}_pr_U_upper_p".format(input_year)
        EM_contrib_var_lower = "EM_{}_pr_contrib_var_lower".format(input_year)
        EM_contrib_var_upper = "EM_{}_pr_contrib_var_upper".format(input_year)

        em_is_num = "EM_is_num_{}".format(input_year)
        em = "EM_{}".format(input_year)
        

        for i_type in range(3):
            if i_type == 0:
                input_type = "AD"
            elif i_type == 1:
                input_type = "EF"
            elif i_type == 2:
                input_type = "EM"


            #Column names for the input columns
            u_dist = "u{}_dist_{}".format(input_type, input_year)
            #u_status = "u{}_status_{}".format(input_type, input_year)
            #u_sym_f = "u{}_sym_f_{}".format(input_type, input_year)
            u_lower_f = "u{}_lower_f_{}".format(input_type, input_year)
            u_upper_f = "u{}_upper_f_{}".format(input_type, input_year)
            u_is_num = "u{}_is_num_{}".format(input_type, input_year)
            #u_corr = "u{}_corr_{}".format(input_type, input_year) #correlation between base year and reporting year
            #u_ref = "u{}_ref_{}".format(input_type, input_year)
            
            
            #column names for the output columns
            #we use pr for propagation as in uncertainty propagation
            _pr_U_lower_p = "{}_{}_pr_U_lower_p".format(input_type, input_year)
            _pr_U_upper_p = "{}_{}_pr_U_upper_p".format(input_type, input_year)


            for i in range(len(df)):
                if df[u_is_num].iloc[i] and df[em].iloc[i] != np.float64(0.0):
                    #print("{} {} {}".format(input_year, input_type, df[u_is_num].iloc[i], df[em].iloc[i] != np.float64(0.0)))
                
                    if df[u_dist].iloc[i] == const.DIST_NORMAL:
                        df_u[_pr_U_lower_p].iloc[i] = df[u_lower_f].iloc[i]*float(200.0)
                        df_u[_pr_U_upper_p].iloc[i] = df[u_upper_f].iloc[i]*float(200.0)

                    elif df[u_dist].iloc[i] == const.DIST_GAMMA:
                        #implicitely, value is one because input U is in percent
                        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html
                        variance = (df[u_upper_f].iloc[i])**2
                        beta = variance #/1 #mean is one
                        alpha = float(1.0) / beta 
                        df_u[_pr_U_lower_p].iloc[i] = (float(1.0) - gamma.ppf(const.DIST_PPF_EDGE_LOWER, alpha, loc = 0, scale =beta))*float(100.0) #2 sigma 
                        df_u[_pr_U_upper_p].iloc[i] = (gamma.ppf(const.DIST_PPF_EDGE_UPPER, alpha, loc = 0, scale =beta) - float(1.0))*float(100.0)
                                
                    elif df[u_dist].iloc[i] == const.DIST_TRIANGULAR:
                        #input U is the edge, in fraction of the mean
                        #equations for pdf distribution is from wikipedia
                        #https://en.wikipedia.org/wiki/Triangular_distribution
                        #equation from GUM can be used ONLY IF the triangular distribution is symmetric
                        #we use the function <triang> from scipy.stats
                        triangle_min = float(1.0) - df[u_lower_f].iloc[i]
                        triangle_max = float(1.0) + df[u_upper_f].iloc[i]
                        triangle_modus = float(1.0) * float(3.0) - triangle_min - triangle_max
                        triangle_scale = triangle_max - triangle_min
                        triangle_c = (triangle_modus - triangle_min)/triangle_scale            
                        df_u[_pr_U_lower_p].iloc[i] = (float(1.0) - triang.ppf(q = const.DIST_PPF_EDGE_LOWER, c = triangle_c, loc = triangle_min, scale = triangle_scale)) * float(100.0)
                        df_u[_pr_U_upper_p].iloc[i] = (triang.ppf(q = const.DIST_PPF_EDGE_UPPER, c = triangle_c, loc = triangle_min, scale = triangle_scale) - float(1.0)) * float(100.0)
        
                    #TODO GMY 20230228 add lognormal distribution
        
        for i in range(len(df)):
            #TODO GMY 20230215 check if this is the right condition
            if df[u_AD_is_num].iloc[i] and df[u_EF_is_num].iloc[i] and df[em].iloc[i] != np.float64(0.0):
                df_u[EM_pr_U_lower_p].iloc[i] = np.sqrt(np.square(df_u[AD_pr_U_lower_p].iloc[i]) + np.square(df_u[EF_pr_U_lower_p].iloc[i]))
                df_u[EM_pr_U_upper_p].iloc[i] = np.sqrt(np.square(df_u[AD_pr_U_upper_p].iloc[i]) + np.square(df_u[EF_pr_U_upper_p].iloc[i]))
                
        
        #col IPCC H, but without normalisation, so that it can be use to compute per gas
        #if emission values are zero the value of the contribution to variance will be zero, ok
        df_u[EM_contrib_var_lower].loc[df[em_is_num]] = np.square(df_u[EM_pr_U_lower_p].loc[df[em_is_num]]*df[em].loc[df[em_is_num]])
        df_u[EM_contrib_var_upper].loc[df[em_is_num]] = np.square(df_u[EM_pr_U_upper_p].loc[df[em_is_num]]*df[em].loc[df[em_is_num]])
    
    return df_u


def compute_U_propagation_trend_pd(
        df,
        df_u,
        EM_BY_sum,
        EM_RY_sum,
        ):
    """Compute uncertainty for the trend according to uncertainty propagation.
    
    Do this after aggregation has been performed.
    
    
    """



    df_u["sens_corr"] = np.float(0.0) #sensitivity if correlation between base year and reporting year
    df_u["sens_no_corr"] = np.float(0.0) #sensitivity if no correlation between base year and reporting year
    df_u["AD_trend_normed_pr_contrib_var_lower"] = np.float(0.0)
    df_u["AD_trend_normed_pr_contrib_var_upper"] = np.float(0.0)
    df_u["EF_trend_normed_pr_contrib_var_lower"] = np.float(0.0)
    df_u["EF_trend_normed_pr_contrib_var_upper"] = np.float(0.0)
    df_u["EM_trend_normed_pr_contrib_var_lower"] = np.float(0.0)
    df_u["EM_trend_normed_pr_contrib_var_upper"] = np.float(0.0)

    
    #indexes = [i for i in range(len(df_u)) if df_u['is_num'][i]]
    indexes = df.index[df['EM_is_num_BY'] | df['EM_is_num_RY']].tolist()

    df_u['sens_corr'][indexes] = np.abs((0.01* df['EM_RY'][indexes] + EM_RY_sum - (0.01* df['EM_BY'][indexes] + EM_BY_sum)) / (0.01* df['EM_BY'][indexes] + EM_BY_sum) *float(100) - (EM_RY_sum - EM_BY_sum)/ EM_BY_sum* float(100.0))
    df_u['sens_no_corr'][indexes] = np.abs(df['EM_RY'][indexes]/EM_BY_sum) #IPCC: type B sensitivity

    #i_is_num_AD_EF = 
    #i_is_num_dEM = 
    
    for i in indexes:
        if df['EM_is_num_RY'][i]:
            if df["import"][i] and not df['uEM_is_num_BY'][i] and not df['uEM_is_num_RY'][i]:
                #Inputs given, and for AD and EF
                if df['uAD_corr'][i]:
                    df_u['AD_trend_normed_pr_contrib_var_lower'][i] = df_u['sens_corr'][i] * df_u['AD_RY_pr_U_lower_p'][i] #df_u['uAD_RY_lower_f'][i]* float(200.0)
                    df_u['AD_trend_normed_pr_contrib_var_upper'][i] = df_u['sens_corr'][i] * df_u['AD_RY_pr_U_upper_p'][i] #df_u['uAD_RY_upper_f'][i]* float(200.0)
                else:
                    df_u['AD_trend_normed_pr_contrib_var_lower'][i] = df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['AD_RY_pr_U_lower_p'][i] #df_u['uAD_RY_lower_f'][i]* float(200.0)
                    df_u['AD_trend_normed_pr_contrib_var_upper'][i] = df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['AD_RY_pr_U_upper_p'][i] #df_u['uAD_RY_upper_f'][i]* float(200.0)
                    
                if df['uEF_corr'][i]:
                    df_u['EF_trend_normed_pr_contrib_var_lower'][i] = df_u['sens_corr'][i] * df_u['EF_RY_pr_U_lower_p'][i] #df_u['uEF_RY_lower_f'][i]* float(200.0)
                    df_u['EF_trend_normed_pr_contrib_var_upper'][i] = df_u['sens_corr'][i] * df_u['EF_RY_pr_U_upper_p'][i] #df_u['uEF_RY_upper_f'][i]* float(200.0)
                else:
                    df_u['EF_trend_normed_pr_contrib_var_lower'][i] = df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['EF_RY_pr_U_lower_p'][i] #df_u['uEF_RY_lower_f'][i]* float(200.0)
                    df_u['EF_trend_normed_pr_contrib_var_upper'][i] = df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['EF_RY_pr_U_upper_p'][i] #df_u['uEF_RY_upper_f'][i]* float(200.0)
    
                df_u['EM_trend_normed_pr_contrib_var_lower'][i] = np.square(df_u['EF_trend_normed_pr_contrib_var_lower'][i]) + np.square(df_u['AD_trend_normed_pr_contrib_var_lower'][i])
                df_u['EM_trend_normed_pr_contrib_var_upper'][i] = np.square(df_u['EF_trend_normed_pr_contrib_var_upper'][i]) + np.square(df_u['AD_trend_normed_pr_contrib_var_upper'][i])
    
    
            else:
                #This is a direct emission
                if df['uEM_corr'][i]:
                    df_u['EM_trend_normed_pr_contrib_var_lower'][i] = np.square(df_u['sens_corr'][i] * df_u['EM_RY_pr_U_lower_p'][i]) #df_u['udEM_RY_lower_f'][i]* float(200.0))
                    df_u['EM_trend_normed_pr_contrib_var_upper'][i] = np.square(df_u['sens_corr'][i] * df_u['EM_RY_pr_U_upper_p'][i]) #df_u['udEM_RY_upper_f'][i]* float(200.0))
                else:
                    df_u['EM_trend_normed_pr_contrib_var_lower'][i] = np.square(df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['EM_RY_pr_U_lower_p'][i]) #df_u['udEM_RY_lower_f'][i]* float(200.0))
                    df_u['EM_trend_normed_pr_contrib_var_upper'][i] = np.square(df_u['sens_no_corr'][i] * np.sqrt(2.0) * df_u['EM_RY_pr_U_upper_p'][i]) #df_u['udEM_RY_upper_f'][i]* float(200.0))


    return df_u


def compute_U_propagation_normalisation_pd(
        df_pr_out, 
        y_string,
        index_total,
        ):
    
    """Normalise variance contribution by emission of the same row
    
    For emissions: the aggregated variance must be normalised by the aggregated emission,
    and then the square root must be computed.
    For the trend: the square root must be computed
    
    """
    
    
    if y_string == "BY" or y_string == "RY":
        indexes = df_pr_out.index[df_pr_out["EM_is_num_{}".format(y_string)]].tolist()
        factor_variance_norm = np.square(df_pr_out["EM_{}".format(y_string)].iloc[indexes])
        df_pr_out["EM_{}_pr_U_lower_p".format(y_string)].iloc[indexes] = np.sqrt(df_pr_out["EM_{}_pr_contrib_var_lower".format(y_string)].iloc[indexes]/factor_variance_norm)
        df_pr_out["EM_{}_pr_U_upper_p".format(y_string)].iloc[indexes] = np.sqrt(df_pr_out["EM_{}_pr_contrib_var_upper".format(y_string)].iloc[indexes]/factor_variance_norm)

        #values normalised by inventory sum
        factor_variance_norm_inv = np.square(df_pr_out["EM_{}".format(y_string)].iloc[index_total])
        if factor_variance_norm_inv != np.float(0.0):
            df_pr_out["EM_{}_pr_contrib_var_normed_lower".format(y_string)] = df_pr_out["EM_{}_pr_contrib_var_lower".format(y_string)]/factor_variance_norm_inv
            df_pr_out["EM_{}_pr_contrib_var_normed_upper".format(y_string)] = df_pr_out["EM_{}_pr_contrib_var_upper".format(y_string)]/factor_variance_norm_inv
        else:
            df_pr_out["EM_{}_pr_contrib_var_normed_lower".format(y_string)] = np.float(0.0)
            df_pr_out["EM_{}_pr_contrib_var_normed_upper".format(y_string)] = np.float(0.0)
    
    
    
    elif y_string == "trend_normed":
        #factor_variance_norm = np.float(1.0)
        df_pr_out["EM_{}_pr_U_lower_p".format(y_string)] = np.sqrt(df_pr_out["EM_{}_pr_contrib_var_lower".format(y_string)])
        df_pr_out["EM_{}_pr_U_upper_p".format(y_string)] = np.sqrt(df_pr_out["EM_{}_pr_contrib_var_upper".format(y_string)])
    

    df_pr_out["EM_{}_pr_contrib_var_mean".format(y_string)] = (df_pr_out["EM_{}_pr_contrib_var_lower".format(y_string)] + df_pr_out["EM_{}_pr_contrib_var_upper".format(y_string)])/float(2.0)
    df_pr_out["EM_{}_pr_U_mean_p".format(y_string)] = (df_pr_out["EM_{}_pr_U_lower_p".format(y_string)] + df_pr_out["EM_{}_pr_U_upper_p".format(y_string)])/float(2.0)

    return df_pr_out
    



def generate_random_value(dist, mean, u_left, u_right, no_random):
    #XXX generate random values using package random
    """
    This function contains the generation of one or several random number(s)
    according to distribution type and corresponding parameters.
    
    INPUT:
        dist: disribution type. Supported types are:
            normal (gaussian)
            triangular
            gamma
        
        mean: mean (average) value
        
        u_left: uncertainty value on the left hand side of the mean,
                in absolute value (not in percent)
        u_right: uncertainty value on the right hand side of the mean,
                in absolute value (not in percent)
        no_random: number of simulations
    """
    val = None

    if dist == const.DIST_NORMAL:
        """
        Normal distribution. 
        mu is the mean, and 
        sigma is the standard deviation.
        """
        #mean: mean
        #u_left: standard deviation (1 sigma, in absolute value (not percent))
            
        val = [random.normalvariate(mu = mean, sigma = u_left) for i in range(no_random)]


    elif dist == const.DIST_GAMMA:

        """
        random.gammavariate(alpha, beta)
        
            Gamma distribution. (Not the gamma function!) Conditions on the parameters are alpha > 0 and beta > 0.
        
            The probability distribution function is:
        
                      x ** (alpha - 1) * math.exp(-x / beta)
            pdf(x) =  --------------------------------------
                        math.gamma(alpha) * beta ** alpha
                        
        Note: 
            alpha parameter here is the same as k in Wikipedia, Gamma distribution.
            beta parameter here is the same as teta in Wikipedia, Gamma distribution.
        
        """

        if mean > float(0.0):
            #variance = u_left**2
            #important: use u_right as input for variance,
            #not u_left because u_left was re-computed as border at 2.5%
            #to prepare for uncertainty approach 1
            variance = u_right**2
            beta = variance/mean
            alpha = mean/beta
            
            val = [random.gammavariate(alpha = alpha, beta = beta) for i in range(no_random)]
        else:
            val = [mean]*no_random


    elif dist == const.DIST_UNIFORM:
        """   
        random.uniform(a, b)
    
        Return a random floating point number N such that
        a <= N <= b for a <= b and b <= N <= a for b < a.
    
        The end-point value b may or may not be included 
        in the range depending on floating-point rounding 
        in the equation a + (b-a) * random().
        
        a and b are the edges of the uniform distribution!
        not the values at 2.5% and 97.5% of the interval.

        u_left must be the distance from mean to left edge (point of the triangle)
        u_left is not the value at 2.5% of the distribution!
        u_right must be the distance from mean to right edge (point of the triangle)
        u_right is not the value at 97.5% of the distribution!
        """ 
        left_edge = mean - u_left
        right_edge = mean + u_right

        if right_edge == left_edge:
            val = [mean]*no_random
        elif right_edge < left_edge:
            raise ValueError("Uniform distribution: right edge < left edge, please check input value.")
        else:            
            val = [random.uniform(a = left_edge, b = right_edge) for i in range(no_random)]



    elif dist == const.DIST_TRIANGULAR:
        """
        u_left must be the distance from mean to left edge (point of the triangle)
        u_left is not the value at 2.5% of the distribution!
        u_right must be the distance from mean to right edge (point of the triangle)
        u_right is not the value at 97.5% of the distribution!
        """            
        #special case following email exchange with Daniel Bretscher 13.01.2022
        #the uncetainty refers to the mode, not the mean, he wrote
        #(GMY note: The IPCC guidelines are not clear at all about this)
        #but until now for approach 1 is was assumed, implicitely, 
        #that uncertainty was given as percentage of the mean.
        #input u_left and u_right are one sigma only
        #input u_left and u_right are values at 95% /2, not edges!!!
        
        #factor_dist_triangular = np.sqrt(6.0)/np.float(2.0)
        #factor_dist_triangular = 1.0
        left_edge  = mean - u_left #*float(2.0) #*factor_dist_triangular
        right_edge = mean + u_right #*float(2.0) #*factor_dist_triangular
        if right_edge == left_edge:
            val = [mean]*no_random
        elif right_edge < left_edge:
            raise ValueError("Uniform distribution: right edge < left edge, please check input value.")
        else:            
            mode = mean*float(3.0) - left_edge - right_edge
            if mode < left_edge:
                raise ValueError("Triangular distribution: mode < left_edge: {} < {}.".format(mode, left_edge))
            if mode > right_edge:
                raise ValueError("Triangular distribution: mode > right_edge: {} < {}.".format(mode, right_edge))
    
            #left_edge, #left edge of triangle
            #right_edge, #right edge of triangle
            #mode) #modus of triangle
            val = [random.triangular(left_edge, right_edge, mode) for i in range(no_random)]


                
    elif dist == const.DIST_LOGNORMAL:
        """
        Documentation from
        https://docs.python.org/3/library/random.html

        random.lognormvariate(mu, sigma)
    
        Log normal distribution. 
        If you take the natural logarithm of this distribution, 
        you’ll get a normal distribution 
        with mean mu and standard deviation sigma. 
        mu can have any value, and sigma must be greater than zero.
        """        
        
        #("lognorm")
        #print(u_right)
        #print(mean)
        if mean > float(0.0):

            lognorm_sigma = u_right/mean
            
            val = [random.lognormvariate(np.log(mean), lognorm_sigma) for i in range(no_random)]
        else:
            val = [mean]*no_random

        
        
    elif dist is None:
        raise ValueError("Distribution type is None, please check for potential missing input value.")
        
    else:
        raise ValueError("Given distribution type <{}> does not correspond to anything programmed.".format(dist))
    
    return val

def generate_random_value_np(dist, mean, u_left, u_right, no_random):
    #TODO work in progress: generate random values using the numpy package.
    """
    GMY 2022.03.16
    WORK IN PROGRESS
    FOR TEST PURPOSE: DO THE SAME AS generate_random_value 
    BUT USING NUMPY FUNCTIONS.
    
    This function contains the generation of one or several random number(s)
    according to distribution type and corresponding parameters.
    
    INPUT:
        dist: disribution type. Supported types are:
            normal (gaussian)
            triangular
            gamma
        
        mean: mean (average) value
        
        u_left: uncertainty value on the left hand side of the mean,
                in absolute value (not in percent)
        u_right: uncertainty value on the right hand side of the mean,
                in absolute value (not in percent)
        no_random: number of simulations
    """
    val = None

    if dist == const.DIST_NORMAL:
        """
        Normal distribution. 
        loc is the mean, and 
        scale is the standard deviation.
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html
        """
        #mean: mean
        #u_left: standard deviation (1 sigma, in absolute value (not percent))
            
        #val = [random.normalvariate(mu = mean, sigma = u_left) for i in range(no_random)]
        val = np.random.normal(loc = mean, scale = u_left, size = no_random)


    elif dist == const.DIST_GAMMA:

        """
        random.gammavariate(alpha, beta)
        
            Gamma distribution. (Not the gamma function!) Conditions on the parameters are alpha > 0 and beta > 0.
        
            The probability distribution function is:
        
                      x ** (alpha - 1) * math.exp(-x / beta)
            pdf(x) =  --------------------------------------
                        math.gamma(alpha) * beta ** alpha
                        
        Note: 
            alpha parameter here is the same as k in Wikipedia, Gamma distribution.
            beta parameter here is the same as teta in Wikipedia, Gamma distribution.
            
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.gamma.html
        
        """

        if mean > float(0.0):
            #variance = u_left**2
            #important: use u_right as input for variance,
            #not u_left because u_left was re-computed as border at 2.5%
            #to prepare for uncertainty approach 1
            variance = u_right**2
            beta = variance/mean
            alpha = mean/beta
            
            #val = [random.gammavariate(alpha = alpha, beta = beta) for i in range(no_random)]
            #gamma.ppf(const.DIST_PPF_EDGE_LOWER, alpha, loc = 0, scale =beta)
            val = np.random.gamma(shape = alpha, scale = beta, size = no_random)
        else:
            val = [mean]*no_random


    elif dist == const.DIST_UNIFORM:
        """   
        random.uniform(a, b)
    
        Return a random floating point number N such that
        a <= N <= b for a <= b and b <= N <= a for b < a.
    
        The end-point value b may or may not be included 
        in the range depending on floating-point rounding 
        in the equation a + (b-a) * random().
        
        a and b are the edges of the uniform distribution!
        not the values at 2.5% and 97.5% of the interval.

        u_left must be the distance from mean to left edge (point of the triangle)
        u_left is not the value at 2.5% of the distribution!
        u_right must be the distance from mean to right edge (point of the triangle)
        u_right is not the value at 97.5% of the distribution!
        
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.uniform.html
        random.uniform(low=0.0, high=1.0, size=None)
        """ 
        left_edge = mean - u_left
        right_edge = mean + u_right
        
        if right_edge == left_edge:
            val = [mean]*no_random
        elif right_edge < left_edge:
            raise ValueError("Uniform distribution: right edge < left edge, please check input value.")
        else:            
            #val = [random.uniform(a = left_edge, b = right_edge) for i in range(no_random)]
            val = np.random.uniform(low = left_edge, high = right_edge, size = no_random)



    elif dist == const.DIST_TRIANGULAR:
        """
        u_left must be the distance from mean to left edge (point of the triangle)
        u_left is not the value at 2.5% of the distribution!
        u_right must be the distance from mean to right edge (point of the triangle)
        u_right is not the value at 97.5% of the distribution!
        
        mode: mode of the triangle, i.e. x position where the probability is maximum,
        i.e. this is the likeliest value to be sampled, or the tip of the triangle. 
        If the triangle is symetric: mode = mean = median.
        If the triangle is not symetric, the mode is not the mean and is not the median.
        
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.triangular.html
        random.triangular(left, mode, right, size=None)
        """            

        left_edge  = mean - u_left
        right_edge = mean + u_right

        if right_edge == left_edge:
            val = [mean]*no_random
        elif right_edge < left_edge:
            raise ValueError("Uniform distribution: right edge < left edge, please check input value.")
        else:            
            mode = mean*float(3.0) - left_edge - right_edge
            if mode < left_edge:
                raise ValueError("Triangular distribution: mode < left_edge: {} < {}.".format(mode, left_edge))
            if mode > right_edge:
                raise ValueError("Triangular distribution: mode > right_edge: {} < {}.".format(mode, right_edge))
    
            #val = [random.triangular(left_edge, right_edge, mode) for i in range(no_random)]
            val = np.random.triangular(left = left_edge, right = right_edge, mode = mode, size = no_random)


                
    elif dist == const.DIST_LOGNORMAL:
        """
        Documentation from
        https://docs.python.org/3/library/random.html

        random.lognormvariate(mu, sigma)
    
        Log normal distribution. 
        If you take the natural logarithm of this distribution, 
        you’ll get a normal distribution 
        with mean mu and standard deviation sigma. 
        mu can have any value, and sigma must be greater than zero.
        """        
        
        #("lognorm")
        #print(u_right)
        #print(mean)
        if mean > float(0.0):

            lognorm_sigma = u_right/mean
            
            val = [random.lognormvariate(np.log(mean), lognorm_sigma) for i in range(no_random)]
        else:
            val = [mean]*no_random

        
        
    elif dist is None:
        raise ValueError("Distribution type is None, please check for potential missing input value.")
        
    else:
        raise ValueError("Given distribution type <{}> does not correspond to anything programmed.".format(dist))
    
    return val


#def dist_triangular_pdf

def find_interval(x, p):
    #XXX find interval from a list
    """
    Find the smallest interval of values from x that represents the fraction
    "p" of the dataset.
    A typical value for p is 0.95.
    x does not need to contain values in strictly ascending order.
    Return the values at the lower and upper edges of the interval.
    Note: if the distribution is non-symetric, then the median may not be 
    in the middle of edge_min, edge_max.
    Note: if the distribution is symetric, 
    (1-p)/2 = edge_min = 0.025 if p = 0.95
    edge_max - p = edge_min
    Note, this may not be true if the distribution is not symetric.
    
    To then compute uncertainties:
        U_upper = edge_max - mean (equiv. to 2 sigmas)
        U_lower = mean - edge_min (equiv. to 2 sigmas)
    """
    edge_min = np.nan
    edge_max = np.nan    
    #remove all nan values
    #try:
    x = x[np.logical_not(np.isnan(x))]
    #except:
    #    x = x[np.logical_not(pd.isnull(x))]
    no_MC = len(x)

    #if no_MC<2:
    #    continue
    #    print("Data length (without nan) is less than 2, there is no interval.")

    if no_MC > 2 and min(x) < max(x):
        #The interval can be computed.
        np.ndarray.sort(x) #sort by strictly ascending order
        #list.sort(trend_EMsum_MCM) #for no numpy format
        #interv_len_min = int(round(p*no_MC))+1 #min no of item to take after trend_qi to represent at least 95% of all data
        interv_len_min = int(np.ceil(p*no_MC))
        qi = 0 #index at start position
        qj = qi+interv_len_min #index at stop position
        
        interv_diff = abs(x[no_MC-1] - x[0])
        qi_opt = 0 #optimum index value at start of interval
        qj_opt = 0 #optimum index value at stop of interval
        interv_opt = interv_diff
    
        while qj<no_MC-1:
            qj = qi+interv_len_min
            interv_diff = abs(x[qj] - x[qi])
            if interv_diff<interv_opt:
                qi_opt = qi
                qj_opt = qj
                interv_opt = interv_diff
            qi += 1
        edge_min = x[qi_opt]
        edge_max  = x[qj_opt]
        #test if distribution is symmetric
        #print("Interv., Pos. of indexes: " + str(qi_opt) + " -- " + str(no_MC-qj_opt+1))

    elif no_MC > 2 and min(x)==max(x):
        #print("Data have uniform value of " + str(min(x)) + ", min and max are the same.")
        edge_min = min(x)
        edge_max = edge_min

    return edge_min, edge_max  

def find_interval_np(x, p):
    #XXX find inteval from a numpy array
    """
    Find the smallest interval of values from x that represents the fraction
    "p" of the dataset.
    A typical value for p is 0.95.
    x does not contain any nan value.
    x does not need to contain values in strictly ascending order.
    Return the values at the lower and upper edges of the interval.
    Note: if the distribution is non-symetric, then the median may not be 
    in the middle of edge_min, edge_max.
    Note: if the distribution is symetric, 
    (1-p)/2 = edge_min = 0.025 if p = 0.95
    edge_max - p = edge_min
    Note, this may not be true if the distribution is not symetric.
    
    To then compute uncertainties:
        U_upper = edge_max - mean (equiv. to 2 sigmas)
        U_lower = mean - edge_min (equiv. to 2 sigmas)
    """
    
    #TODO GMY 20230216
    #use partition to speed up sorting
    #use partition estimate values from uncertainty propagation
    #https://numpy.org/doc/stable/reference/generated/numpy.ndarray.partition.html#numpy.ndarray.partition
    edge_min = np.nan
    edge_max = np.nan    
    #remove all nan values
    x = x[np.logical_not(np.isnan(x))]
    no_mc = len(x)

    if no_mc > 1:
        np.ndarray.sort(x) #sort by strictly ascending order

        if x[0] < x[no_mc-1]:
            #minimum interval defined by fraction of points compared to tal number of points
            no_interv = int(np.ceil(p*no_mc)) #950 if no_mc = 1000
                    
            #x[0:50 + 1] -> data from zero to 50: len = 51
            #x[950 -1 : 1000] -> data from 949 to 999 : len = 51
    
            #data will be compared from index zero to index interv_len_min included,
            #so we need here to remove one, otherwise the total interval is
            # interv_len_min + 1        
            a = np.abs(x[0:no_mc - no_interv + 1] - x[no_interv - 1:no_mc])
            #print("qi_stop_diff " + str(no_mc - interv_len_min +1))
            #print("interv_len_min " + str(interv_len_min))
    
            #find index of smallest value for the difference:
            qi_opt = np.argmin(a) #result is a scalar value
            #print("qi_opt " + str(qi_opt))
            qj_opt = qi_opt + no_interv - 1
            #print("qj_opt " + str(qj_opt))
            
            edge_min = x[qi_opt]
            edge_max  = x[qj_opt]

    else:
        #print("Data have uniform value of " + str(min(x)) + ", min and max are the same.")
        edge_min = x[0]
        edge_max = x[no_mc-1]

    return edge_min, edge_max  

def find_interval_pd(x, p):
    #XXX find interval from a pandas DataFrame
    """
    Find the smallest interval of values from x that represents the fraction
    "p" of the dataset.
    A typical value for p is 0.95.
    x does not need to contain values in strictly ascending order.
    x must be a pandas Series.
    Return the values at the lower and upper edges of the interval.
    Note: if the distribution is non-symetric, then the median may not be 
    in the middle of edge_min, edge_max.
    Note: if the distribution is symetric, 
    (1-p)/2 = edge_min = 0.025 if p = 0.95
    edge_max - p = edge_min
    Note, this may not be true if the distribution is not symetric.
    
    To then compute uncertainties:
        U_upper = edge_max - mean (equiv. to 2 sigmas)
        U_lower = mean - edge_min (equiv. to 2 sigmas)
    """

    #TODO GMY 20230216
    #use partition to speed up sorting
    #use partition estimate values from uncertainty propagation
    #https://numpy.org/doc/stable/reference/generated/numpy.ndarray.partition.html#numpy.ndarray.partition

    edge_min = np.nan
    edge_max = np.nan    
    #remove all nan values
    x.dropna(inplace = True) #remove nan values
    no_mc = len(x)

    if no_mc > 2:
        #The interval can be computed.
        x.sort_values(
                axis = 0, #use axis = 0 to sort rows, use axis =1 to sort columns
                ascending=True,
                inplace = True,
                #ignore_index = True, #set True to relabel index axis, does not work for pandas version < xxx
                )
        x.reset_index(inplace = True, drop = True) #it is necessary to reset the index!
    
        if x.iloc[0] < x.iloc[no_mc-1]:
            #minimum interval defined by fraction of points compared to total number of points
            no_interv = int(np.ceil(p*no_mc)) #950 if no_mc = 1000
                    
            #x[0:50 + 1] -> data from zero to 50: len = 51
            #x[950 -1 : 1000] -> data from 949 to 999 : len = 51
    
            #data will be compared from index zero to index interv_len_min included,
            #so we need here to remove one, otherwise the total interval is
            # interv_len_min + 1        
            a = (x.iloc[0:no_mc - no_interv + 1] - x.iloc[no_interv - 1:no_mc])
            a = a.abs()
    
            #find index of smallest value for the difference:
            qi_opt = a.idxmin(axis=0, skipna=True) #result is a scalar value
            #print("qi_opt " + str(qi_opt))
            qj_opt = qi_opt + no_interv - 1
            #print("qj_opt " + str(qj_opt))
            
            edge_min = x.iloc[qi_opt]
            edge_max = x.iloc[qj_opt]

    else:
        #print("Data have uniform value of " + str(min(x)) + ", min and max are the same.")
        edge_min = x.iloc[0]
        edge_max = x.iloc[no_mc-1]

    return edge_min, edge_max       

def find_interval_np_zeronan(y, no_mc, no_interv):
    #XXX find inteval from a numpy array without nan values
    """
    Find the interval of len no_interv from x of len mo_mc
    with the smallest value difference between the first and last value of the interval.
    x does not contain any nan value.
    x does not need to contain values in strictly ascending order.
    Return the values at the lower and upper edges of the interval.
    Note: if the distribution is non-symetric, then the median may not be 
    in the middle of edge_min, edge_max.
    Note: if the distribution is symetric, 
    (1-p)/2 = edge_min = 0.025 if p = 0.95
    edge_max - p = edge_min
    Note, this may not be true if the distribution is not symetric.
    
    To then compute uncertainties:
        U_upper = edge_max - mean (equiv. to 2 sigmas)
        U_lower = mean - edge_min (equiv. to 2 sigmas)
    """

    #TODO GMY 20230203 use np.partition to put values in 3 groups,
    #and sort only first group and last group.
    #https://numpy.org/doc/stable/reference/generated/numpy.partition.html#numpy.partition
    #numpy.partition(a, kth, axis=-1, kind='introselect', order=None)
    #for input distributions,
    #it is possible to compute the value at (1-p_dist) and the value at p_dist.

    #use partition to speed up sorting
    #use partition estimate values from uncertainty propagation
    #https://numpy.org/doc/stable/reference/generated/numpy.ndarray.partition.html#numpy.ndarray.partition
    
    #p1 = 1
    #p2 = 3
    #x.partition((1, 3))
    
    #get index of p1
    #we need i_p1 >= no_mc - no_interv
    #get index of p2
    #we need i_p2 <= no_interv - 1
    #sort all values from index 0 to i_p1
    #sort all values from i_p2 to end.

    #needs a deep copy here!
    x = y.copy()
    np.ndarray.sort(x) #sort by strictly ascending order
    
    #minimum interval defined by fraction of points compared to tal number of points
    #no_interv = int(np.ceil(p*no_mc)) #950 if no_mc = 1000
            
    #x[0:50 + 1] -> data from zero to 50: len = 51
    #x[950 -1 : 1000] -> data from 949 to 999 : len = 51

    #data will be compared from index zero to index interv_len_min included,
    #so we need here to remove one, otherwise the total interval is
    # interv_len_min + 1        
    a = np.abs(x[0:no_mc - no_interv + 1] - x[no_interv - 1:no_mc])

    #find index of smallest value for the difference:
    qi_opt = np.argmin(a) #result is a scalar value
    #print("qi_opt " + str(qi_opt))
    qj_opt = qi_opt + no_interv - 1
    #print("qj_opt " + str(qj_opt))
    
    edge_min = x[qi_opt]
    edge_max  = x[qj_opt]

    return edge_min, edge_max  


def find_interval_centered(x, p):
    #XXX find an interval artificially centered
    """
    Find the interval of values from x that represents the fraction
    "p" of the dataset.
    The interval must be centered from 2.5 % to 97.5% of the points;
    so it is not necessarily the narrowest possible interval.
    A typical value for p is 0.95.
    x does not need to contain values in strictly ascending order.
    Return the lower and upper edges of the interval.
    Note: if the distribution is non-symetric, then the median may not be 
    in the middle of edge_min, edge_max.
    Note: if the distribution is symetric, 
    (1-p)/2 = edge_min = 0.025 if p = 0.95
    edge_max - p = edge_min
    Note, this may not be true if the distribution is not symetric.
    """
    edge_min = np.nan
    edge_max = np.nan    
    #remove all nan values
    x = x[np.logical_not(np.isnan(x))]
    no_MC = len(x)

    if no_MC<2:
        print("Data length (without nan) is less than 2, there is no interval.")
    elif min(x)==max(x):
        #print("Data have uniform value of " + str(min(x)) + ", min and max are the same.")
        edge_min = min(x)
        edge_max = edge_min
    else:
        #The interval can be computed.
        np.ndarray.sort(x) #sort by strictly ascending order
        #list.sort(trend_EMsum_MCM) #for no numpy format
        #interv_len_min = int(round(p*no_MC))+1 #min no of item to take after trend_qi to represent at least 95% of all data
        interv_len_min = int(np.ceil(p*no_MC))
        qi_opt = int(round((float(1.0)-p)/float(2.0)*no_MC))
        qj_opt = qi_opt + interv_len_min

        edge_min = x[qi_opt]
        edge_max  = x[qj_opt]

    return edge_min, edge_max




def groupby_one_attribute_pd(
        df,
        df_agg_tree,
        use_cols_for_agg,
        agg_str,
        child_id_left,
        col_unique_groupby_extra,
        col_EM_status,
        ):



    depth_id = "depth_id{}".format(agg_str)
    parent_id = "parent_id{}".format(agg_str)
    child_id = "child_id{}".format(agg_str)
    parent_id_tree = "parent_id{}_tree".format(agg_str)
    child_id_tree = "child_id{}_tree".format(agg_str)
    parent_id_agg = "parent_id{}_agg".format(agg_str)
    


    #this is working
    df_test = pd.merge(
            df[[child_id_left]],
            df_agg_tree,
            left_on=[child_id_left], 
            right_on = [child_id], 
            how="left", 
            indicator="exists_agg")
            
    #https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html#merging-together-values-within-series-or-dataframe-columns
    df[depth_id] = df_test[depth_id].copy()
    df[parent_id] = df_test[parent_id].copy()        

    agg_max_depth = np.int(np.max(df[depth_id]))
        
    for i_depth in range(agg_max_depth, 0, -1):
        #aggregate only to one level above
        print("i_depth: " + str(i_depth))
        
        print("group by: " + str([parent_id] + col_unique_groupby_extra + [depth_id]))

        df_agg_mc = df.loc[df[depth_id] == i_depth].groupby(
                by = [parent_id] + col_unique_groupby_extra + [depth_id]).sum().reset_index()

        
        #TODO GMY 20230216 The next loop is very slow. 
        #Find a better way using .agg
        df_agg_mc[col_EM_status] = "ES"
        #df_agg_mc["EM_is_num_BY"] = True
        for i in range(len(df_agg_mc)):
            status_list = pd.unique(df[col_EM_status].loc[
                    (df[col_unique_groupby_extra[0]] == df_agg_mc[col_unique_groupby_extra[0]].iloc[i])
                    & (df[col_unique_groupby_extra[1]] == df_agg_mc[col_unique_groupby_extra[1]].iloc[i])
                    & (df[parent_id] == df_agg_mc[parent_id].iloc[i])
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
        #drop redundant columns
        df_agg_mc.drop([parent_id_agg, child_id], axis=1, inplace=True) #, "exists_agg"
    
        #Technical aspect: drop this column resulting from the merge
        #because it will be added with the next merge with the aggregation tree
        #df_agg_mc["exists_agg"] = np.where(df_agg_mc["exists_agg"] == "both", True, False)
        df_agg_mc.drop(["exists_agg"], axis=1, inplace=True) #,     
        
        
        #Concatenate the aggregated rows with the original DataFrame, to get all results into one DataFrame
        #TODO GMY 20230217: think abut a less memory-intensive method.
        #The problem is, such intermediate results are needed for subsequent aggregations.
        df = pd.concat([df, df_agg_mc], axis =0, ignore_index=True)

    return df