import json
from csv import DictReader
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

import altair as alt
from altair import Chart, Order
from pandas import Index, Int64Index

from scrape_data import scrape_wikipedia, scrape_govhu


@st.cache(ttl=86400) # rerun once every day
def prepare_data():
    scrape_wikipedia()
    scrape_govhu()

    corona_dead_raw_data = []
    with open('corona-hun-dead.csv', 'r') as f:
        reader = DictReader(f)
        for row in reader:
            corona_dead_raw_data.append(row)

    corona_dead_data = pd.DataFrame.from_dict(corona_dead_raw_data)
    corona_dead_data.columns = ["Sorszam", "Nem", "Kor", "Betegsegek"]
    if (corona_dead_data["Sorszam"] == "14").sum() > 1:
        # fix issues with erronous multiple 14 indexes
        corona_dead_data = pd.concat([corona_dead_data[:-14299-97+1],corona_dead_data[-14299:]])
    corona_dead_data["Sorszam"] = corona_dead_data["Sorszam"].astype(int)
    corona_dead_data.set_index("Sorszam", inplace=True)
    corona_dead_data.sort_index(inplace=True)

    corona_dead_data["Nem"] = corona_dead_data["Nem"].str.lower().str.slice(0,1)

    corona_dead_data["Kor"] = corona_dead_data["Kor"].astype(int)

    fixed_index = list(corona_dead_data.index)
    fixed_index[1762] = 1763 #this is the 2nd (erronous) 1762 id

    corona_dead_data.index = Int64Index(data=fixed_index, name="Sorszam")

    #betegsegek_indicators = corona_dead_data["Betegsegek"].str.get_dummies()(",")

    #daily_deaths = json.load(open("daily_deaths.json","r"))

    wikidata = pd.read_csv("wikidata.csv")
    wikidata = wikidata[["date","death_all"]]
    wikidata["new_deaths"] = wikidata["death_all"].diff()
    wikidata.set_index("date",inplace=True)
    wikidata.sort_index(inplace=True)

    assert len(corona_dead_data) == wikidata["new_deaths"].sum()
    full_death_counter = 0
    for date, wiki_row in wikidata.iterrows():
        if wiki_row["new_deaths"] > 0:
            for daily_death_counter in range(int(wiki_row["new_deaths"])):
                full_death_counter += 1
                corona_dead_data.loc[full_death_counter,"Datum"] = date

    corona_dead_data["Datum"] = pd.to_datetime(corona_dead_data["Datum"])

    corona_dead_data_by_date = corona_dead_data.reset_index().set_index("Datum")

    return corona_dead_data_by_date

if __name__ == "__main__":
    #STREAMLIT
    corona_dead_data_by_date = prepare_data()
    st.markdown("""
        <style>
        .css-1v3fvcr {
            align-items: flex-start;
            padding-left: 50px;
        }
        </style>
        """, unsafe_allow_html = True)

    st.sidebar.markdown(f"**Set the days in the moving average!**")
    rolling_days = st.sidebar.slider(
        'Days in the moving average',
        min_value=1, max_value=31,
        value=7)

    st.sidebar.markdown(f"**Set the desired number of age segments, then set the segment delimiters!**")

    number_of_age_segments = st.sidebar.selectbox(
        'Number of age segments',
        list(range(2,11)),
        index=1)

    max_age = int(np.max(corona_dead_data_by_date["Kor"]))

    if number_of_age_segments != "<select>":
        age_segments = []
        min_age = 0
        for age_segment_counter in range(number_of_age_segments-1):

            option = st.sidebar.selectbox(
                f'Age delimiter {age_segment_counter + 1}',
                list(range(5,max_age,5)),
                index=int((len(list(range(1,max_age,5)))//number_of_age_segments)*(age_segment_counter+1)))
            age_segments.append(option)

        is_valid_age_groups = list(sorted(age_segments)) == list(age_segments)

        st.sidebar.markdown(f"**Chart formatting options**")

        colormaps = ["spectral","darkred","darkmulti","lightmulti","goldgreen","plasma","viridis","blues","greens", "reds"]

        colormap = st.sidebar.selectbox("Colormap", colormaps)
        reverse_colormap = st.sidebar.checkbox(label="Reverse colors")
        chart_width = st.sidebar.slider("Chart widths", min_value=300, max_value=2000, value=1000)
        chart_height = st.sidebar.slider("Chart heights", min_value=100, max_value=1000, value=250)

        st.sidebar.write("© András Sárkány, 2021")
        st.sidebar.markdown("[andris.sarkany@gmail.com](mailto:andris.sarkany@gmail.com)")

        if is_valid_age_groups:

            st.markdown(f"**Moving average of coronavirus deaths in Hungary ({rolling_days} days)**")
            age_segments = [0] + age_segments + [max_age]
            rolling_counts = []
            for lower_age,upper_age in zip(age_segments[:-1],age_segments[1:]):
                filtered = corona_dead_data_by_date[
                                        (corona_dead_data_by_date["Kor"] >= lower_age) &
                                        (corona_dead_data_by_date["Kor"] < upper_age)]["Sorszam"]

                rolling_count = filtered.groupby(by="Datum").count().rolling(f"{rolling_days}D").sum()
                rolling_count.name = f"{lower_age} - {upper_age}"
                rolling_counts.append(rolling_count)

            rolling_cumsum = pd.concat(rolling_counts,axis=1).cumsum(axis=1)
            #st.line_chart(rolling_cumsum, width=1000, height=500, use_container_width=False)
            chart = alt.Chart(rolling_cumsum.reset_index().melt(id_vars="Datum")).mark_line(size=5).encode(
                    x="Datum",
                    y=alt.Y("value", title="Count"),
                    color=alt.Color("variable",title="Age group",scale=alt.Scale(scheme=colormap, reverse=reverse_colormap)),
                    order=alt.Order(
                        # Sort the segments of the bars by this field
                        'variable',
                        sort='ascending'),
                    tooltip=[alt.Tooltip('Datum:T', title="Date"),
                             alt.Tooltip('value:Q', title="Death"),
                             alt.Tooltip('variable:N', title="Age group")],

                ).configure_view(
                    strokeWidth=1.0,
                    height=chart_height,
                    width=chart_width
                ).interactive()

            st.altair_chart(chart)

            y1 = alt.Y("value", title="Count")
            y2 = alt.Y("value", title="Percentage", stack="normalize", axis=alt.Axis(format='%'))


            for yi, y in enumerate([y1,y2]):
                if yi == 0:
                    st.markdown(f"**Coronavirus deaths in Hungary, stacked age groups, summed for every {rolling_days} days**")
                elif yi == 1:
                    st.markdown(f"**Coronavirus death ratio between age groups in Hungary summed for every {rolling_days} days**")

                chart = alt.Chart(rolling_cumsum[::rolling_days].reset_index().melt(id_vars="Datum").fillna(0)).mark_bar(
                    size=10).transform_joinaggregate(
                        total="sum(value)",
                        groupby=["Datum"]).transform_calculate(
                        frac=alt.datum.value / alt.datum.total).encode(
                    x="Datum",
                    y=y,
                    color=alt.Color("variable",title="Age group",scale=alt.Scale(scheme=colormap, reverse=reverse_colormap)),
                    order=alt.Order(
                        # Sort the segments of the bars by this field
                        'variable',
                        sort='ascending'),
                    tooltip=[alt.Tooltip('Datum:T', title="Date"),
                             alt.Tooltip('value:Q', title="Death"),
                             alt.Tooltip('variable:N', title="Age group"),
                             alt.Tooltip('frac:Q', title="Percentage", format='.0%')],

                ).configure_view(
                    strokeWidth=1.0,
                    height=chart_height,
                    width=chart_width
                ).interactive()

                st.altair_chart(chart)

            #.encode(x="Datum",y="Sorszam")
            #
                #.configure_facet_cell(
                #    strokeWidth=1.0,
                #    height=500,
                #    width=1000)
        else:
            st.write("Invalid age groups")

    if st.checkbox('Show dataframe'):
        corona_dead_data_by_date

    if st.checkbox('Show rolling dataframe'):
        rolling_cumsum

    #hist_values = np.histogram(corona_dead_data_by_date["Kor"], bins=10)

    if st.checkbox('Show age histogram'):
        fig = plt.figure()
        plt.hist(corona_dead_data_by_date["Kor"], bins=30)
        st.write(fig)
        plt.close(fig)
    pass



