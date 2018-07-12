# ThermalBlanket

This respository includes tools for processing data collected using the Thermal Blanket heat flow instrument.

Please see Salmi et al., 2013 for more information about the Thermal Blanket processing and construction. 

Generate_GoldenNugget.py - loads the raw temperature records from the ANTARES data logger and writes out both a csv and matlab mat for further processing. 

Required files for processing of the Thermal Blanket are:
1) The top and bottom thermistor .dat files downloaded from data loggers

2) Offset correction file. The thermistors will not read exactly the same temperature and any offset will introduce a bias into the heat flow measurement. The offset calibrations are the required temperature shifts that will remove and bias in the readings. 

The file format should be rows of Logger ID (found on the side of the thermistor), offset calibration (degree C)

An example offset correction file has been included in the Repository titled offsets.csv.

3) Deployment meta data - A csv file for each individual Blanket that include all deployments during the survey.

The columns should include the following data:

Latitude(Degree), Latitude(Minutes), Longitude(Degree), Long(Dec Min), Blanket, Dive number, Date Deployed (Julian day), Deployed Time (Hour), Deployed Time (Min), Date Recovered (Julian day), Time Recovered (Hour), Time Recovered (Min)

An example csv file has been included in the Respository titled Blanket_A.csv 
