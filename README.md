# Interplanetary Survival Guide: Martian Map

This project was developed in response to NASA’s **Interplanetary Survival Guide: Martian Map** challenge at the 2026 International Space Apps Challenge. The challenge calls for combining data from several NASA science missions into a map of a selected area or route on Mars. The map should help explorers plan surface travel and conduct scientific investigations along the way. [Official NASA challenge](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/)

## Project Objective

Planning travel on Mars requires accounting for local terrain. Craters, canyons, and steep slopes can make a route difficult to traverse and may require a detour.

The current version addresses the terrain assessment and route planning portion of the challenge. The study area covers Gale Crater and its surroundings. A digital elevation model was used to create a 3D map that lets users inspect the surface, identify the coordinates and elevation of locations, and view calculated routes between selected points.

## Implementation and Results

The map uses the Gale HRSC terrain model at a resolution of 30 meters per pixel. The A* algorithm searches for a route based on distance and terrain difficulty. It excludes areas where slopes exceed the specified limit. Elevation changes and local depressions increase the cost of traversing an area, so the algorithm favors gentler terrain.

A white dashed line shows the route, and green markers indicate the start and end points. The two simulations produced the following results.

| Simulation | Route length | Result |
| --- | --- | --- |
| First | 337.8 km | [Route map](gale_hrsc_route.html) |
| Second | 211.8 km | [Route map](gale_hrsc_route2.html) |

Download the corresponding HTML file and open it in a browser. You can rotate and zoom the map and view it offline.

## Simulation Conditions and Limitations

| Simulation conditions |
| --- |
| This version accounts for slopes, elevation changes, and local depressions when calculating a route. This helps the route avoid steep sections of craters, canyons, and other landforms. Rocks, loose soil, and obstacles too small to be captured by the digital elevation model (DEM) are outside the scope of the current model. |
| Both simulations use an assumed maximum slope of 15°. This limit helps the algorithm find a gentler route under the chosen conditions. Assessing whether a route is safe in practice also requires information about surface conditions and the capabilities of the vehicle or explorer. |

The 15° limit was selected for these simulations. Further work on the challenge involves adding data to assess travel conditions and plan scientific activities along the route.

## Data and References

### Challenge and Study Area

- NASA International Space Apps Challenge 2026. The challenge statement and objectives. [Interplanetary Survival Guide: Martian Map](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/)
- NASA / JPL-Caltech. *Mars Science Laboratory Landing Press Kit*, 2012. Information about Gale Crater and Curiosity’s landing site used to verify the location of the study area. [Mission press kit](https://mars.nasa.gov/internal_resources/823/)

### Terrain Model

- Persaud, D. M., Putri, A. D. R., Muller, J.-P. (2021). *30-m HRSC DTM Mosaic of Gale Crater, Mars*, version 1.0.0. The primary source of elevation data for both simulations. The mosaic was created from stereo images acquired by the High Resolution Stereo Camera (HRSC) aboard the European Space Agency’s Mars Express spacecraft. [Dataset, DOI 10.5281/zenodo.5808354](https://zenodo.org/records/5808354)
- Documentation accompanying the HRSC mosaic. Details on the projection, resolution, reference system, and source images. [Dataset README](https://zenodo.org/records/5808354/files/Persaud_2021_HRSC_DTM-README.txt?download=1)
- Fergason, R. L., Hare, T. M., Laura, J. (2018). *HRSC and MOLA Blended Digital Elevation Model at 200m V2*. The reference model used by the authors of the HRSC mosaic. It combines HRSC data with Mars Orbiter Laser Altimeter (MOLA) measurements from NASA’s Mars Global Surveyor mission. The current map incorporates these measurements through the HRSC mosaic. [USGS catalog](https://fdp.astrogeology.usgs.gov/fdp/mars/#:~:text=HRSC%20%2F%20MOLA%20Blended%20Product)
- Kim, J.-R., Muller, J.-P. (2009). *Multi-resolution topographic data extraction from Martian stereo imagery*. The stereo image processing method cited by the authors of the mosaic. [Publication, DOI 10.1016/j.pss.2009.09.024](https://doi.org/10.1016/j.pss.2009.09.024)

### Algorithm and Processing Tools

- Hart, P. E., Nilsson, N. J., Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*. The original publication describing the A* algorithm. [Publication, DOI 10.1109/TSSC.1968.300136](https://doi.org/10.1109/TSSC.1968.300136)
- Rasterio. Documentation for reading and processing raster data by window. [Windowed reading and writing](https://rasterio.readthedocs.io/en/stable/topics/windowed-rw.html)
- NumPy. Documentation for the gradient calculation used to determine slopes. [numpy.gradient](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)
- Plotly. Documentation for rendering the 3D surface and displaying the route. [Mesh3d](https://plotly.com/python/3d-mesh/), [Scatter3d](https://plotly.com/python/reference/scatter3d/)

- Pillow. Documentation for loading, processing, and resizing raster images. [Pillow documentation](https://pillow.readthedocs.io/en/stable/)
- GeoPandas. Documentation for processing and analyzing geospatial vector data. [GeoPandas documentation](https://geopandas.org/en/stable/)
- Matplotlib. Documentation for creating and customizing 2D plots and maps. [Matplotlib documentation](https://matplotlib.org/stable/users/index.html)
- Python Software Foundation. Standard library documentation for `pathlib`, the module used for filesystem paths. [pathlib documentation](https://docs.python.org/3/library/pathlib.html)

### Additional Data Sources and Mapping Resources

- Arizona State University (ASU). Mars Global Data Sets, a catalog used to find and obtain data for map visualizations. [Mars Global Data Sets](https://www.mars.asu.edu/data/)
- NASA. Mars Trek, an interactive mapping tool for exploring the Martian surface. [Mars Trek](https://trek.nasa.gov/mars/#v=0.1&x=0&y=0&z=1&p=urn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A104905&d=&locale=&b=mars&e=-269.999994963537%2C-128.3203101063685%2C269.999994963537%2C128.3203101063685&sfz=&w=)
- California Institute of Technology, Murray Lab. A resource for imagery of the Martian surface acquired by the Context Camera (CTX). [CTX Data](https://murray-lab.caltech.edu/CTX/)

### Use of AI

- OpenAI’s GPT-6 Astra and GPT-6.1 Sol were used to write code, research technical approaches, and locate the NASA data needed for the project.
