# inventory_uncertainty_UNFCCC_CLRTAP
This repository contains a method in Python to compute the uncertainty of an inventory (such as a pollutant inventory or a greenhouse gas inventory), based on input uncertainty for specific sub-categories of this inventory. The main aim of this Python script is to automate computation tasks that are performed every year for emission reporting in the framework of:
- the UNECE Convention on Long-range Transboundary Air Pollution (CLRTAP);
- the United Nations Framework Convention on Climate Change (UNFCCC).

The present method propagates the uncertainties from individual categories according to two approaches:
- uncertainty propagation (for inventory reporting: also known as "Approach 1");
- Monte Carlo simulations (for inventory reporting: also known as "Approach 2").

The uncertainty propagation method follows the method recommended in the UNFCCC 2006 and 2019 guidelines and in the EMEP/EEA air pollutant emission inventory guidebook 2019 (note that this is a slightly simplified uncertainty propagation method).

The Monte Carlo method follows as much as possible recommendations from the Bureau International des Poids et Mesures, as expressed in: Evaluation of measurement data — Supplement 1 to the “Guide to the expression of uncertainty in measurement” — Propagation of distributions using a Monte Carlo method.

https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf/325dcaad-c15a-407c-1105-8b7f322d651c

## Installation

The script has been tested with the Anaconda3 environment, version 4.4.0, using Python version 3.6.1. We recommend to install Anaconda3 or to make sure the following packages are installed:
- `datetime`
- `matplotlib`
- `numbers`
- `numpy`
- `openpyxl`
- `pandas`
- `pathlib`
- `random`
- `scipy`

### Download the source from git

## Quick start
There are two main computation procedures, which calls the same functions but using different parameters. These procedures can be started by running the files with names starting with "SCRIPT":
- run [`SCRIPT_POLLUTANTS_with_uncertainty.py`](./SCRIPT_POLLUTANTS_with_uncertainty.py) for pollutants (such as NOx, NMVOC, SOx, NH3, PM10, PM2.5);
- run [`SCRIPT_GHG_inventory.py`](./SCRIPT_GHG_inventory.py) for greenhouse gases.

### Python files "SCRIPT_..."
In these scripts, the input parameters to set manually are:
- `BY_year`: a string with format YYYY, the base year.
- `RY_year`: a string with format YYYY, the reporting year (i.e. the latest year being reported, for example year 2020 for Submission year 2022).
- `no_mc`: an integer, the number of Monte Carlo simulations.
- `use_fuel_used`: a boolean variable, set to True to report according to the "fuel used" aproach. Set to "False" to report according to the "fuel sold" approach.
- `plot_mode`: a boolean variable, set to True to automatically plot some figures.
- `make_new_output_folder`: a boolean variable, set to True to create a new, unique folder name to save the results.

The scripts call the main function `routine_u_kca_wrapper`.

### Main function
The main function is `routine_u_kca_wrapper` and is stored in [`routine_u_kca.py`](./routine_u_kca.py).

### Utility files
All other functions are stored in files whose name starts with `utils_`:
- [`utils_compute.py`](./utils_compute.py): functions to perform computation, including the Monte Carlo simulations and uncertainty propagation, using the packages `numpy` and `random`.
- [`utils_constant.py`](./utils_constant.py): constant values and strings used for all other functions.
- [`utils_io_file_structure.py`](./utils_io_file_structure.py): structure description of all input Excel files, to be used by the `pandas` package.
- [`utils_io_read_check.py`](./utils_io_read_check.py): fonctions mostly using the `pandas` package to read input Excel files and also perform quality checks.
- [`utils_io_write_to_excel.py`](./utils_io_write_to_excel.py): fonctions to write output results to Excel files, using the package `openpyxl`.
- [`utils_plot.py`](./utils_plot.py): function to plot results, using the `matplotlib` package.


### Run from the command line
Command line is not supported (yet).

## Organisation of the computation method

### Input data

"xxxx" = submission year, format YYYY

Input data are saved in a specific folder, under "/input_data/input_subxxxx", for example under [`/input_data/input_sub2023/`](./input_data/input_sub2023/) for the input data for submission year 2023 (where the reporting year is 2021).

All input data, which normally are updated each year, are in the form of Excel files. This is not usual but based on the fact that Excel is widely used in public administrations. This format may be changed to csv files in the future.
Each row in the input excel files corresponds to a source category. A source category is uniquely defined by the following attributes (which are saved in specific column in the Excel files):
- nomenclature class, such as CRT for greenhouse gases according to the IPCC Guidelines, or NFR for pollutants according to the EMEP Guidebook;
- source category code according to the chosen nomenclature;
- source category name according to the chosen nomenclature (unsupported so far, please leave blank);
- compound name;
- resource name, this is used in particular in the Energy sector, to specify which fuel is burned.

#### Input emission data
Input emission data are saved in a specific folder, under "/input_data/input_subxxxx/input_emission".
For submission 2023, the input emission files are saved at: [`/input_data/input_sub2023/input_emission/`](./input_data/input_sub2023/input_emission/)

The sum of all input emission data must match the inventory total.
Do not include emissions that should not be included in the inventory total. In particular, do not include:
- sources of natural origin, such as NMVOC emissions from forests or greenhouse gas emissions from wild animals;
- source categories that, according to the official guidelines, should not be included in the inventory total (such as memo items).

You can check the input Excel file for emissions to see how the structure should be. The column structure cannot be modified but the number of rows can be modified as required.

#### Input uncertainty data
Input uncertainty data are saved in a specific folder, under "/input_data/input_subxxxx/input_uncertainty".
For submission 2023, the input uncertainty files are saved at: [`/input_data/input_sub2023/input_uncertainty/`](./input_data/input_sub2023/input_uncertainty/)

The input uncertainties must be given at the same aggregation level as for the input emissions. For each source category, the following information must be provided for activity data and emission factor or, if unknown, for emissions:
- distribution type: normal, gamma, triangular, uniform;
- for normal and gamma distributions: standard deviation with a coverage factor of 2;
- for the triangular distribution: lower edge and upper edge expressed in percentage of the mean (not the values at 2.5% and 97.5% of the distribution);
- for the other distributions: lower end and upper end uncertainties at 2.5% and 97.5% of the distribution, expressed in percentage of the mean.
- the information if values are correlated between the base year and the reporting year.

#### Input nomenclature data
Input nomenclature data are saved in a specific folder, under "/input_data/input_subxxxx/input_nomenclature".
For submission 2023, the input nomenclature files are saved at: [`/input_data/input_sub2023/input_nomenclature/`](./input_data/input_sub2023/input_nomenclature/)

These data should be already valid for any simulation using only official NFR or CRT nomenclature and cover:
- nomenclature definition for process names, compound names, resource names;
- for each attribute (process, compound, resource), an aggregation tree.


### Output data
Output data are saved in a specific folder, under "/output_data/output_subxxxx/output_subxxx_IIR" for pollutants and under "/output_data/output_subxxxx/output_subxxx_NID" for greenhouse gases.
For submission 2023, the output files are saved at: [`/output_data/output_sub2023/output_sub2023_IIR/`](./output_data/output_sub2023/output_sub2023_IIR/) for pollutants and [`/output_data/output_sub2023/output_sub2023_NID/`](./output_data/output_sub2023/output_sub2023_NID/) for greenhouse gases.

#### Computed uncertainty values
Output data are automatically exported to Excel. These Excel files can be further used and copied/pasted in reports. 

#### Plots
All plots automatically produced with the matplotlib package are saved as PNG figures.

#### Automated quality control
Output data to be used for quality control are written in a text file.
