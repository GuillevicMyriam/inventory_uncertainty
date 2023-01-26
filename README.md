# inventory_uncertainty
This repository contains a method in Python to compute the uncertainty of an inventory (such as a pollutant inventory or a greenhouse gas inventory), based on input uncertainty for specific sub-categories of this inventory.
The present method propages the uncertainties from individual categories according to two approaches:
- uncertainty propagation (for inventory reporting: also known as "Approach 1");
- Monte Carlo simulations (for inventory reporting: also known as "Approach 2").

The uncertainty propagation methods follows the method recommended in the UNFCCC guidelines (note that this is a slightly simplified uncertainty propagation method).

The Monte Carlo method follows as much as possible recommendations from the Bureau International des Poids et Mesures, as expressed in: Evaluation of measurement data — Supplement 1 to the “Guide to the expression of uncertainty in measurement” — Propagation of distributions using a Monte Carlo method.

https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf/325dcaad-c15a-407c-1105-8b7f322d651c
