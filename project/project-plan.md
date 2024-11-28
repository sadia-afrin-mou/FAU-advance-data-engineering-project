# Project Plan

## Title
<!-- Give your project a short title. -->
Assessing Renewable Energy's Impact on Environmental Health and Pollutant Concentrations in the U.S. within North America region.

## Main Question

<!-- Think about one main question you want to answer based on the data. -->
1. Does increased renewable energy consumption lead to measurable improvements in environmental health and pollutant concentrations?

## Description

<!-- Describe your data science project in max. 200 words. Consider writing about why and how you attempt it. -->
This project investigates how renewable energy consumption affects environmental health and pollutant concentrations in the U.S., situating findings within the North American context. With the shift toward cleaner energy sources, understanding these effects is crucial for shaping policy and investment decisions. Renewable energy promises significant environmental benefits, such as improved air quality, but the extent of these benefits remains underexplored across different regions. This exploration will highlight areas where renewables may yield the greatest positive outcomes, providing insights for more effective energy planning.

The analysis will utilize two key datasets:
* Renewable Energy Consumption data to gauge regional adoption levels.
* Air Pollution data to assess environmental health.

Using correlation and comparative analyses with python's data science toolkits (i.e., numpy, pandas, matplotplib,scikit-learn, etc.), I will assess relationships between renewable energy usage and environmental improvements over time.

## Datasources

<!-- Describe each datasources you plan to use in a section. Use the prefic "DatasourceX" where X is the id of the datasource. -->

### Datasource1: U.S Renewable Energy Consumption
* Metadata URL: https://www.kaggle.com/datasets/alistairking/renewable-energy-consumption-in-the-u-s
* Data URL: https://www.kaggle.com/datasets/alistairking/renewable-energy-consumption-in-the-u-s?select=dataset.csv
* Data Type: CSV

This dataset provides monthly data on renewable energy consumption in the United States from January 1973 to December 2024, broken down by energy source and consumption sector. The data is sourced from the U.S. Energy Information Administration (EIA).

### Datasource2: U.S. Pollution Data 2000 - 2023
* Metadata URL: https://www.kaggle.com/datasets/guslovesmath/us-pollution-data-200-to-2022
* Data URL: https://www.kaggle.com/datasets/guslovesmath/us-pollution-data-200-to-2022?select=pollution_2000_2023.csv
* Data Type: CSV

This dataset spans from the year 2000 to 2023, comprising around 665,414 observations across 21 columns. It provides an analysis of air quality in the United States, with an emphasis on pollutants like Nitrogen Dioxide (NO2), Sulphur Dioxide (SO2), Carbon Monoxide (CO), and Ozone (O3). The data has been continuously updated, and most recently extended to include 2023 data, enhancing its research value.

### Datasource3: U.S. Emissions Data 1990 - 2023
* Metadata URL: https://www.epa.gov/air-emissions-inventories/air-pollutant-emissions-trends-data
* Data URL: https://www.epa.gov/system/files/other-files/2024-02/state_tier1_08feb2024_ktons.xlsx
* Data Type: XLSX

This dataset spans from the year 1990 to 2023. It provides an analysis of pollutant emissions in the United States, with an emphasis on pollutants like Nitrogen Dioxide (NO2), Sulphur Dioxide (SO2), Carbon Monoxide (CO), PM10, PM2.5, and others.

## Work Packages

<!-- List of work packages ordered sequentially, each pointing to an issue with more details. -->

1. Gathering suitable datasets [#1][i1]
2. Initial data exploration using python notebook [#2][i2]
3. Finding correlation among the datasets [#3][i3]
4. Building ETL pipeline. [#4][i4]
5. Pattern analysis and building predictive models [#5][i5]
6. Training and testing the model [#6][i6]
7. Conclude the project and giving future scopes [#7][i7]

[i1]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/1
[i2]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/2
[i3]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/3
[i4]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/4
[i5]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/5
[i6]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/6
[i7]: https://github.com/sadia-afrin-mou/FAU-advance-data-engineering-project/issues/7