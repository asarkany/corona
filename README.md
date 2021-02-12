# README

## Data source

1. corona-hun-dead.csv was scraped from https://koronavirus.gov.hu/elhunytak
   1. it contains all individuals who have died. In this visualization I've 
1. wikidata.csv was manually created using the data from the chart on the right on this wikipedia page: https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Hungary#Infections 
    1. the data was directly copied from here: https://en.wikipedia.org/w/index.php?title=Template:COVID-19_pandemic_data/Hungary_medical_cases_chart&action=edit
   
Data needs to be updated manually!!! Last update 2021.02.10.
    
## Data processing
The main assumption when creating these plots is that the order of the deceased can be taken as granted and it can be assigned to the daily death data.

## Verdict: streamlit is awesome
1. Input GUI setup and flow control is very intuitive and fun.
1. Caching is an off-the-shelf usable feature and needed for most applications. 
1. For plotting I suggest using altair directly, instead letting streamlit to it for you
1. Altair is not easy to use but I could do exactly what I wanted in a couple of hours. It's expressiveness is massive, reminds me of ggplot2. 
   This project will be a starting point whenever I'd work with altair again.
1. Sharing and github connection is very convenient.

## License

GPLv3, see [LICENSE](LICENSE) file.