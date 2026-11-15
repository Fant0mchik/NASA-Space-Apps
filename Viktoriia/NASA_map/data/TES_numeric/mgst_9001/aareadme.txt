PDS_VERSION_ID                       = PDS3
RECORD_TYPE                          = STREAM
OBJECT                               = TEXT
  PUBLICATION_DATE                   = 2009-09-17
  NOTE                               = "MGS TES derived thermal inertia 
                                        maps."
END_OBJECT                           = TEXT
END

                MGS TES derived thermal inertia maps 

1. Introduction

This document provides an overview of the Mars Global Surveyor TES Derived 
Thermal Inertia Maps Archive, including a complete listing of the contents 
of the data set.  

This data set consists of Thermal Inertia maps derived using Mars Global 
Surveyor Thermal Emission Spectrometer thermal bolometer temperature 
observations taken over three Mars-years from orbit 1583 to 24346 (note that in 
this context orbit refers to the TES specific Orbit Counter Keeper (OCK)), from 
February 1999 (beginning of mapping mission) to April 2004.  Maps use only 
nightside or dayside data with surface temperatures between 160 and 400 K.  
Nightside (southbound) and dayside (northbound) maps are included and each has 
been infilled between 87 degrees south and 87 degrees north latitude. The derived 
range is 5 to 5000 tiu (tiu = J/(m^2*K*sqrt(s)) ).  Higher and lower values are not 
computed.

An interpolation mask is provided for each map, which identifies those 
pixels where the map has been infilled by interpolation (less than 8% in 
each case).  If the interpolated pixels are not desired, they can be removed 
by multiplying the thermal inertia map by the associated interpolation mask.

Browse color images including scale bars are available in JPEG format for 
nightside and dayside thermal inertia maps.  Large (approximately 3.3 Mb) and 
small (approximately 0.15 Mb) versions are included.


2. Documentation

This data set is described in the file DATASET.CAT in the CATALOG directory.
Also in this directory are files describing the TES instrument (INST.CAT), the
MGS spacecraft (INSTHOST.CAT) and mission (MISSION.CAT), personnel associated 
with this archive volume (PERSON.CAT), and a bibliography of references 
mentioned in these filed (REF.CAT).  The files in this directory are used to 
generate entries in the Planetary Data System online catalog.


3. Data Set Description

The processing of this data set was carried out by Nathaniel E. Putzig, 
currently at the Southwest Research Institute, and Michael T. Mellon, 
currently at the University of Colorado in Boulder.  The processing to 
convert TES bolometer temperature observations to thermal inertia has been 
described in detail elsewhere.  See the papers by Putzig and Mellon [2007] 
and Putzig et al. [2005] listed in ref.cat for more information.

Note that the MGS-TES published bolometric thermal inertia was not used to 
derive these maps.  The thermal inertia model that was used to calculate and 
populate the MGS-TES Bolometer tables is different than that used here,
and querying the thermal inertia data (i.e. from published CDs or from
http://tes.asu.edu/data_tool/index.php) will not reproduce the maps in this
dataset.

This data set comprises several images that include:

(1) Thermal Inertia Maps
(2) Interpolation Masks
(3) Browse JPEGs

(1) Thermal Inertia Maps
These images contain thermal inertia values derived from MGS TES thermal
bolometer temperature observations taken over three Mars-years from orbit 
1583 to 24346, from February 1999 (beginning of mapping mission) to April 
2004.  Maps use only nightside or dayside data with surface temperatures 
between 160 and 400 K.  Nightside (southbound) and dayside (northbound) maps 
are included and each has been infilled between 87 degrees south and 87 
degrees north latitude.  The derived range is 5 to 5000 J/(m^2*K*sqrt(s)).  
Higher and lower values are not computed.  Map resolution is 20 pixels per 
degree.  Dayside and nigthside images are denoted in filenames by "day" and
"night" respectively.  "2007" denotes the year in which these maps were
published.

(2) Interpolation Masks
An interpolation mask is provided for each map, which identifies those 
pixels where the map has been infilled by interpolation (less than 8% in 
each case).  If the interpolated pixels are not desired, they can be removed 
by multiplying the thermal inertia map by the associated interpolation mask. 
There is one interpolation mask each for both the nightside and dayside 
thermal inertia maps.  The resolution of the interpolation masks is 20 
pixels per degree.  Interpolation masks are denoted in filenames by "msk".

(3) Browse JPEGs
The browse JPEGs consist of colorized representations of the thermal inertia 
maps.  A large (approximately 3.3 Mb) and small (approximately 0.15 Mb) 
version is available for both nightside and dayside thermal inertia maps.  A 
scale bar to roughly interpret the value of thermal inertia based on color 
is included on each browse JPEG. Units for the browse images are tiu (tiu = 
J/(m^2*K*sqrt(s)) ). In filenames "d" denotes dayside maps, "n" denotes 
nightside maps, "b" stands for bolometer, and "s" stands for small. 

See the papers by Putzig and Mellon [2007] and Putzig et al. [2005] listed 
in ref.cat for more information on the data products included in this data 
set.

The coordinate system used in this data set is Mars Planetocentric referenced 
to the IAU_1991 ellipsoid, east positive; Mars is assumed to be a sphere with 
radius 3396.0 km.  All images in this data set cover a latitude range of 90 to 
-90 degrees north and a longitude range of -180 to 180 degrees east.  Images are 
centered at 0 degrees north and 0 degrees east. Information about the map 
projection is found in the PDS labels. Formulas for converting between latitude-
longitude and line-sample coordinates are in the file DSMAP.CAT in the CATALOG 
directory.


4. File Formats

The images within this data set are composed of 16 bit MSB-integer pixels. 
The interpolation Mask images are stored as 8-bit MSB-integer pixels.  Each 
image has an accompanying PDS label that describes the format and content of 
the image.  Each PDS label is in a separate file with the same name as the 
image it describes but with the extension .LBL.

All text files in the data set are stream format files, with a carriage 
return (ASCII 13) and a line feed character (ASCII 10) at the end of the 
record.


5. Image Display

The PDS provides software for displaying PDS-labeled images on a variety of 
computer platforms.  The application program for image display is called 
NASAView, which has versions for SUN/SOLARIS, WINDOWS, and LINUX platforms.  
The PDS distributes NASAView through its Web site.  Consult the PDS Web site 
for the status of NASAView in terms of its capabilities and availability.  
The address for the PDS Web site is http://pds.jpl.nasa.gov/.


6. Archive Contents

Files within this data set are organized into a series of
subdirectories below the top-level directory.

Top-level Directory
-------------------

AAREADME.TXT

The file you are currently reading.

VOLDESC.CAT

This text file contains a description of the volume contents as a PDS
catalog object.  It is a required file for PDS archives.

CATALOG Directory
-----------------

Files in the CATALOG directory are text files containing documentation
formatted in PDS object description language.  The files contain information 
about the MGS mission and spacecraft, the TES instrument, the Derived 
Thermal Inertia Maps data set, personnel associated with the data and 
archive, and references.  See the file CATINFO.TXT for details.

INDEX Directory
---------------

The INDEX directory contains PDS index files for this archive.  An index 
file is an ASCII table with each record (or line) in the table containing 
information about a single image in the archive.  See the file INDXINFO.TXT 
for additional details.

Data Directory
----------------

The Derived Thermal Inertia Maps data files are stored in the DATA 
directory.  File names for thermal inertia maps are of the form 
global_ti_xxx_2007.img and interpolation masks are of the form
global_ti_msk_xxx_2007.img where xxx is either "day" or "night" indicating 
dayside and nightside maps interpolation masks, respectively.  

The detached PDS label files use the same naming convention with .LBL
instead of the .IMG of the image file.

Browse Directory
-----------------

The BROWSE directory contains colorized representations of the thermal 
inertia maps.  A large (approximately 3.3 Mb) and small (approximately 
0.15 Mb) version is available for both nightside and dayside thermal 
inertia maps. In filenames "d" denotes dayside maps, "n" denotes nightside
maps, "b" stands for bolometer, and "s" stands for small.


7. Whom To Contact For Information

For questions concerning this data set:

     PDS Geosciences Node
     Washington University
     Dept. of Earth and Planetary Sciences
     1 Brookings Drive
     St. Louis, MO 63130
     314-935-9295
     WWW Site: http://pds-geosciences.wustl.edu
     Electronic mail address: geosci@wunder.wustl.edu

     Nathaniel Putzig
     Southwest Research Institute
     Department of Space Studies
     1050 Walnut Street
     Suite 300
     Boulder, CO 80302
     720-240-0130
     Electronic mail address: nathaniel@putzig.com


8. Cognizant Persons

TES derived thermal inertia maps were provided by Nathaniel Putzig, of the 
Southwest Research Institute, and Mike Mellon, of the University of Colorado 
in Boulder.

This volume was designed and produced by Tabatha Heet and Jennifer Ward,
Planetary Data System Geosciences Node, Washington University, St. Louis, 
Missouri.


9. Citation

The TES derived thermal inertia data set may be cited in published
literature using the following reference.

  Putzig, N.E., M.T. Mellon, T.L. Heet, and J.G. Ward, MGS Mars TES Derived 
  Thermal Inertia Maps V1.0, MGS-M-TES-5-TIMAP-V1.0, NASA Planetary Data 
  System, 2009.
