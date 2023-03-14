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

Created on Wed Oct 13 14:04:42 2021
"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

import utils_constant as const

#nice colors can be found here:
#https://xkcd.com/color/rgb/



def plot_distributions_EM_trend(
        BY_EM_sum_MCM_mean, 
        BY_EM_sum_MCM_stddev, 
        BY_EM_sum_MCM,
        RY_EM_sum_MCM_mean,
        RY_EM_sum_MCM_stddev,
        RY_EM_sum_MCM,
        trend_EMsum_MCM_mean,
        trend_EMsum_MCM_stddev,
        trend_EMsum_MCM,
        gas_string: str,
        gas_string_latex: str,
        BY_string: str,
        RY_string: str,
        unit_string: str,
        output_filename) -> None:
    """Plot distribution of results obtained by Monte Carlo simulation as a bar plot.
    
    Distribution of emissions for the base year and the reporting year are shown together a the top subplot.
    Distribution for the trend is shown on the bottom subplot.
    
    """

    color_alpha = 0.5
    text_size = 10
    text_size_small = 10
    MC_bar_text = "All sim."
    
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #plot BY_EM and RY_EM on same x_axis
    
    #plot figure with distribution for BY and RY on same graph
    fig1, (ax1, ax2) = plt.subplots(figsize=(7,7), nrows=2, ncols=1)
    #fig1.suptitle( '{}: Distributions for base year and reporting year ({}, {})'.format(gas_string_latex, BY_string, RY_string) + "\n" + "and fit using a normal distribution")
        
    bins = np.linspace(int(round(min(BY_EM_sum_MCM_mean - float(4)*BY_EM_sum_MCM_stddev, RY_EM_sum_MCM_mean - float(4)*RY_EM_sum_MCM_stddev))), 
                       int(round(max(BY_EM_sum_MCM_mean + float(4)*BY_EM_sum_MCM_stddev, RY_EM_sum_MCM_mean + float(4)*RY_EM_sum_MCM_stddev))), 
                       num = 100)
    
    #plot histogam, use "density=True," to normalise histogram
    #for newer Python versions, use "density = True" instead of "normed = True"
    N_BY, bins, patches = ax1.hist(BY_EM_sum_MCM, bins = bins, normed = True, color = const.COLOR_BY, alpha = color_alpha, label = "{}, {}".format(MC_bar_text, BY_string))     
    N_RY, bins, patches = ax1.hist(RY_EM_sum_MCM, bins = bins, normed = True, color = const.COLOR_RY, alpha = color_alpha, label = "{}, {}".format(MC_bar_text, RY_string))
    
    #plot normal distribution on top
    xmin, xmax = ax1.get_xlim()
    x = np.linspace(xmin, xmax, 100)

    pMCM_BY = stats.norm.pdf(x, BY_EM_sum_MCM_mean, BY_EM_sum_MCM_stddev)
    ax1.plot(x, pMCM_BY, color = const.COLOR_BY, linewidth=1)

    pMCM_RY = stats.norm.pdf(x, RY_EM_sum_MCM_mean, RY_EM_sum_MCM_stddev)
    ax1.plot(x, pMCM_RY, color = const.COLOR_RY, linewidth=1)

    # By using ``transform=vax.get_xaxis_transform()`` the y coordinates are scaled
    # such that 0 maps to the bottom of the axes and 1 to the top.
    #ax1.vlines([BY_EM_sum_MCM_mean], 0, 1, transform=ax1.get_xaxis_transform(), colors='xkcd:grey', linestyle = "-.")
    ax1.vlines([BY_EM_sum_MCM_mean], 0, N_BY.max(), colors= const.COLOR_BY, linestyle = "-.")
        
    #plot mean as vertical line
    #plt.plot([BY_EM_sum_MCM_mean, BY_EM_sum_MCM_mean], [0, max_y], 'c--', linewidth=1)
    #ax1.vlines([RY_EM_sum_MCM_mean], 0, 1, transform=ax1.get_xaxis_transform(), colors='xkcd:blue', linestyle = "-.")
    ax1.vlines([RY_EM_sum_MCM_mean], 0, N_RY.max(), colors= const.COLOR_RY, linestyle = "-.")

    
    ax1.set_xlabel("Emissions, {} [{}]".format(gas_string_latex, unit_string), fontsize=text_size)
    ax1.set_ylabel('Probability, normalised', fontsize=text_size)
    #ax1.legend(["Fit, base year ({})".format(BY_string), "Fit, reporting year ({})".format(RY_string), 'mean, base year', 'mean, reporting year'], fontsize = text_size_small)
    ax1.legend(["Fit, {}".format(BY_string), "Fit, {}".format(RY_string), "{}, {}".format(MC_bar_text, BY_string), "{}, {}".format(MC_bar_text, RY_string), "Mean, {}".format(BY_string), "Mean, {}".format(RY_string)], fontsize = text_size_small)


    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #plot distribution for trend
        
    if not np.isnan(trend_EMsum_MCM_mean):        
        bins = np.linspace(int(round(trend_EMsum_MCM_mean - float(4)*trend_EMsum_MCM_stddev)), 
                           int(round(trend_EMsum_MCM_mean + float(4)*trend_EMsum_MCM_stddev)), 
                           num = 100)
        
        N_trend, bins, patches =  ax2.hist(trend_EMsum_MCM, bins = bins,  normed = True, color = 'xkcd:grey', alpha =0.5, label = MC_bar_text)

        #plot normal distribution on top
        xmin, xmax = ax2.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        pMCM   = stats.norm.pdf(x, trend_EMsum_MCM_mean, trend_EMsum_MCM_stddev)
        ax2.plot(x, pMCM, 'xkcd:black', linewidth=1)
                
        # By using ``transform=vax.get_xaxis_transform()`` the y coordinates are scaled
        # such that 0 maps to the bottom of the axes and 1 to the top.
        #ax1.vlines([BY_EM_sum_MCM_mean], 0, 1, transform=ax1.get_xaxis_transform(), colors='xkcd:grey', linestyle = "-.")
        ax2.vlines([trend_EMsum_MCM_mean], 0, N_trend.max(), colors='xkcd:grey', linestyle = "-.")
        
        ax2.set_xlabel("Trend {}-{}, {} [%]".format(BY_string, RY_string, gas_string_latex), fontsize=text_size)
        ax2.set_ylabel('Probability, normalised', fontsize=text_size)
        ax2.legend(["Fit", MC_bar_text, "Mean"], fontsize = text_size_small) #'fit, gamma dist.', 
    
    
    fig_name = output_filename + ".png"
    plt.savefig(fig_name, bbox_inches='tight', transparent = True, dpi = 300)
    
    plt.show()
    plt.close()
    
    return None



def tornado_plot_EM_BY_RY(
        nomenc_list_i, 
        sensitivity_BY, 
        sensitivity_RY, 
        BY_string: str, 
        RY_string: str, 
        gas_string_latex: str,
        output_figname,
        ) -> None:
    """
    Plot tornado plot using sensitivity results.
    Exclude nan values!
    
    sensitivity_max: maximum of sensitivity using sensitivity results for both base year and reporting.
    aim: same scale of x axis for both plots.
    
    """
    color_alpha = 0.75
    text_size = 9
    text_size_small = 8
    
    
    
    #sensitivity_max = np.ceil(float(10.0) *max(max(sensitivity_RY), max(sensitivity_BY)))/float(10.0) 

    #python horizontal bar char
    #https://matplotlib.org/stable/gallery/lines_bars_and_markers/barh.html#sphx-glr-gallery-lines-bars-and-markers-barh-py
    
    #it seems the label for y-axis does not work well if too many ticks
    
    #plot histogram of sum of emission from the chosen nomenclature codes, as obtained from MC simulations
    #plot figure with 2 subplots: distributions for BY EM and RY EM together, and trend
    #plot histograms of likelihood values for true and false fragments/maximal elements
    #fig, ax = plt.subplots(figsize=(8,4), nrows=1, ncols=2, sharey=False) #, nrows=1, ncols=2, sharex=True
    fig, ax = plt.subplots(figsize=(6,7), nrows=2, ncols=1, sharex=True)


    if gas_string_latex is not None:

        #fig.suptitle(gas_string_latex + ", " + year_string + ": Sensitivity of total emission" + "\n" + " to contributions from categories")
        label_BY = gas_string_latex + ", " + BY_string
        label_RY = gas_string_latex + ", " + RY_string

    else:
        #fig.suptitle('Sensitivity of total emission to contributions from categories')
        label_BY = BY_string
        label_RY = RY_string

    #****BY**************    
    #remove nan values
    indexes_nan = np.isnan(sensitivity_BY)
    nomenc_list = [nomenc_list_i[i] for i in range(len(indexes_nan)) if indexes_nan[i] == False]
    sensitivity = [sensitivity_BY[i] for i in range(len(indexes_nan)) if indexes_nan[i] == False]
    
    #sort by sensitivity estimator, by decreasing order    
    y_pos_ordered_inc = np.argsort(np.abs(sensitivity))
    y_pos_ordered = y_pos_ordered_inc[::-1] #take in decreasing order of sensitivity!
    
    #keep only the first 20 values
    max_nomenc = min (20, len(y_pos_ordered))
    y_pos_ordered_first20 = y_pos_ordered[0:max_nomenc]    
    nomenc_list_first20 = [nomenc_list[i] for i in y_pos_ordered_first20]
    sensitivity_first20 = [sensitivity[i] for i in y_pos_ordered_first20]
        
    y_pos = np.arange(len(y_pos_ordered_first20))

    ax[0].barh(y_pos, sensitivity_first20,  align='center', color = const.COLOR_BY , alpha = color_alpha) #xerr=error,
    ax[0].set_yticks(y_pos)
    ax[0].set_yticklabels(nomenc_list_first20, fontsize = text_size_small) #ax.set_yticks(y_pos, labels = nomenc_list)    
    ax[0].invert_yaxis()  # labels read top-to-bottom
    ax[0].legend([label_BY], loc = 'lower right', fontsize = text_size)
    #ax[0].set_xlabel("Sensitivity [normalised value between -1 and +1]", fontsize=text_size) #Correlation coefficient between total emissions and category emission
    #grid works but since bars are transparent, does not look nice
    #ax[0].grid(visible=True, which='major', axis='both', linestyle = "--", linewidth = 1, color = color_grid)

    #***RY****
    indexes_nan = np.isnan(sensitivity_RY)
    nomenc_list = [nomenc_list_i[i] for i in range(len(indexes_nan)) if indexes_nan[i] == False]
    sensitivity = [sensitivity_RY[i] for i in range(len(indexes_nan)) if indexes_nan[i] == False]
    
    #sort by sensitivity estimator, by decreasing order    
    y_pos_ordered_inc = np.argsort(np.abs(sensitivity))
    y_pos_ordered = y_pos_ordered_inc[::-1] #take in decrasing order of importance!
    
    #keep only the first 20 values
    max_nomenc = min (20, len(y_pos_ordered))
    y_pos_ordered_first20 = y_pos_ordered[0:max_nomenc]    
    nomenc_list_first20 = [nomenc_list[i] for i in y_pos_ordered_first20]
    sensitivity_first20 = [sensitivity[i] for i in y_pos_ordered_first20]
        
    y_pos = np.arange(len(y_pos_ordered_first20))

    ax[1].barh(y_pos, sensitivity_first20,  align='center', color = const.COLOR_RY , alpha =color_alpha) #xerr=error,
    ax[1].set_yticks(y_pos)
    ax[1].set_yticklabels(nomenc_list_first20, fontsize = text_size_small) #ax.set_yticks(y_pos, labels = nomenc_list)    
    ax[1].invert_yaxis()  # labels read top-to-bottom
    ax[1].legend([label_RY], loc = 'lower right', fontsize = text_size)
    ax[1].set_xlabel('Sensitivity [normalised value between -1 and +1]', fontsize=text_size) #Correlation coefficient between total emissions and category emission


    plt.savefig(output_figname, bbox_inches='tight', transparent = True, dpi = 300)
    
    plt.show()
    plt.close()


    return None 

