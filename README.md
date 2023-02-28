# inventory_uncertainty_UNFCCC_CLRTAP
This repository contains a method in Python to compute the uncertainty of an inventory (such as a pollutant inventory or a greenhouse gas inventory), based on input uncertainty for specific sub-categories of this inventory. The main aim of this Python script is to automatise computation tasks that have to performed every year for emission reporting in the framework of:
- the UNECE Convention on Long-range Transboundary Air Pollution (CLRTAP);
- the United Nations Framework Convention on Climate Change (UNFCCC).

The present method propages the uncertainties from individual categories according to two approaches:
- uncertainty propagation (for inventory reporting: also known as "Approach 1");
- Monte Carlo simulations (for inventory reporting: also known as "Approach 2").

The uncertainty propagation methods follows the method recommended in the UNFCCC 2006 and 2019 guidelines and in the EMEP/EEA air pollutant emission inventory guidebook 2019 (note that this is a slightly simplified uncertainty propagation method).

The Monte Carlo method follows as much as possible recommendations from the Bureau International des Poids et Mesures, as expressed in: Evaluation of measurement data — Supplement 1 to the “Guide to the expression of uncertainty in measurement” — Propagation of distributions using a Monte Carlo method.

https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf/325dcaad-c15a-407c-1105-8b7f322d651c

## Installation

The script has been tested with the Anaconda3 environment. We recommend to install Anaconda3 or to make sure the following packages are installed:
- numpy
- pandas
- openpyxl
- numbers
- random
- pathlib
- matplotlib


### Download the source from git

## Quick start

### Python script

Run from...

### Command line
Command line is not supported (yet).

## Organisation

### Input data

"xxxx" = submission year, format YYYY

Input data are saved in a specific folder, under "input_data/input_subxxxx/"

All input data, which normally are updated each year, are in the form of Excel files. This is not usual but based on the fact that Excel is widely used in public administrations.
Each row in the input excel files corresponds to a source category. A source category is uniquely defined by the following attributes (which are saved in specific column in the Excel files):
- nomenclature class, such as CRT for greenhouse gases according to the IPCC Guidelines, or NFR for pollutants according to the EMEP Guidebook;
- source category code according to the chosen nomenclature;
- source category name according to the chosen nomenclature (unsupported so far, please leave blank);
- compound name;
- resource name, this is used in particular in the Energy sector, to specify which fuel is burned.

#### Input emission data

The sum of all input emission data must match the inventory total.
Do not include emissions that should not be included in the inventory total. In particular, do not include:
- sources of natural origin, such as NMVOC emissions from forests or greenhouse gas emissions from wild animals;
- source categories that, according to the official guidelines, should not be included in the inventory total (such as memo items).

You can check the input Excel file for emissions to see how the structure should be. The column structure cannot be modified but the number of rows can be modified as required.

#### Input uncertainty data

The input uncertainties must be given at the same aggregation level as for the emissions. For each source category, the following information must be provided for activity data and emission factor or, if unknown, for emissions:
- distribution type: normal, gamma, triangular, uniform;
- for normal and gamma distributions: standard deviation with a coverage factor of 2;
- for the triangular distribution: lower edge and upper edge expressed in percentage of the mean (not the values at 2.5% and 97.5% of the distribution);
- for the other distributions: lower end and upper end uncertainties at 2.5% and 97.5% of the distribution, expressed in percentage of the mean.
- the information if values are correlated between the base year and the reporting year.

#### Input nomenclature data
These data should be already valid for any simulation and cover:
- nomenclature definition for process names, compound names, resource names;
- for each attribute (process, compound, resource), an aggregation tree.


### Output data
Output data are saved in a specific folder, under "output_data/output_subxxxx/"

#### Computed uncertainty values
Output data to be further used and copied/pasted in reports are written automatically in Excel.

#### Plots
All plots automatically produced with the matplotlib package are saved as PNG figures.

#### Automated quality control
Output data to be used for quality control are written in a text file.
