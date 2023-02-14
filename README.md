# inventory_uncertainty
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

All input data, which normally are updated each year, are in the form of Excel files. This is not usual but based on the fact that Excel is widely used in public administrations.
Each row in the input excel files corresponds to a source category. A source category is uniquely defined by the following attributes:
- nomenclature class, such as CRT for greenhouse gases according to the IPCC Guidelines, or NFR for pollutants according to the EMEP Guidebook;
- source category code according to the chosen nomenclature;
- source category name according to the chosen nomenclature;
- compound name;
- resource name, this is used in particular to specify the fuel burned for the Energy sector.

#### Input emission data

The sum of all input emission data must match the inventory total.
Do not include emissions that should not be included in the inventory total. In particular, do not include:
- sources of natural origin, such as NMVOC emissions from forests or greenhouse gas emissions from wild animals;
- source categories that, according to the official guidelines, should not be included in the inventory total.

You can check the input Excel file for emissions to see how the structure should be. The column structure cannot be modified but the number of rows can be modified as required.

#### Input uncertainty data

he input uncertainties must be given at the same aggregation level as for the emissions. 

### Output data

Output data to be further used and copied/pasted in reports are written automatically in Excel.
Output data to be used for quality control are written as text files.
