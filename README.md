# README

## Data source

Data updates automatically, set to a period of 1 day.
1. Deceased people demographics are scraped from https://koronavirus.gov.hu/elhunytak
   1. it contains all individuals who have died.
1. Daily counts are scraped from: https://en.wikipedia.org/wiki/COVID-19_pandemic_in_Hungary#Infections 
   
    
## Data processing
The main assumption when creating these plots is that the order of the deceased can be taken as granted and it can be assigned to the daily death data.

## Verdict: streamlit is awesome
1. Input GUI setup and flow control is very intuitive and fun.
1. Caching is an off-the-shelf usable feature and needed for most applications. 
1. For plotting I suggest using altair directly, instead letting streamlit to it for you
1. Altair is not easy to use but I could do exactly what I wanted in a couple of hours. It's expressiveness is massive, reminds me of ggplot2. 
   This project will be a starting point whenever I'd work with altair again.
1. Sharing and github connection is very convenient.

## Copyright
2021, András Sárkány

[sarkany.andris@gmail.com](mailto:sarkany.andris@gmail.com)


## License

[CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode), see [LICENSE](LICENSE) file.
