import streamlit as st
import requests
from matplotlib.ticker import FuncFormatter
from opencage.geocoder import OpenCageGeocode
from streamlit_folium import folium_static
import folium
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="COVID-19 Report by Country",
    layout= "wide",
    menu_items = {
        'Get Help' : 'https://docs.streamlit.io/',
        'About' : '# Welcome to the Covid Tracker Page. Developed by Jeslyn Chacko'
    }
)
# Function to fetch COVID-19 data
def fetch_covid_data(country, is_code=False):
    if is_code:
        url = "https://covid-19-data.p.rapidapi.com/country/code"
        querystring = {"code": country, "date-format": "yyyy-mm-dd", "format": "json"}
    else:
        url = "https://covid-19-data.p.rapidapi.com/country"
        querystring = {"name": country, "format": "json"}
    headers = {
        "X-RapidAPI-Key": "4fae334dfcmsh32d4279bdd4553dp147d05jsn429234162e47",
        "X-RapidAPI-Host": "covid-19-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                "country": country,
                "deaths": data[0].get('deaths', 'Data not available'),
                "confirmed": data[0].get('confirmed', 'Data not available'),
                "recovered": data[0].get('recovered', 'Data not available'),
                "critical": data[0].get('critical', 'Data not available')
            }
        else:
            return {"error": "No data available"}
    else:
        return {"error": f"Failed to retrieve data: {response.status_code}"}


# Function to fetch the list of countries
@st.cache_data
def get_list_of_countries():
    url = "https://covid-19-data.p.rapidapi.com/help/countries?format=json"
    headers = {
        "X-RapidAPI-Key": "4fae334dfcmsh32d4279bdd4553dp147d05jsn429234162e47",
        "X-RapidAPI-Host": "covid-19-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    return response.json()

@st.cache_data
def map_creator(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=3)
    folium.Marker([latitude, longitude], popup="Location", tooltip="Location").add_to(m)
    return m

# Function to get coordinates using OpenCage
def get_coordinates(country, is_code=False):
    key = '4b2c9c34e0994a778bb384f4f24cc359'
    geocoder = OpenCageGeocode(key)
    if is_code:
        result = geocoder.geocode(country, no_annotations='1', countrycode=country)
    else:
        result = geocoder.geocode(country, no_annotations='1')
    if result and len(result):
        for res in result:
            if 'country' in res['components']:
                return res['geometry']['lat'], res['geometry']['lng']
    return None, None


# Streamlit app
st.title("COVID-19 Report by Country")
st.header("Streamlit and Covid Tracker API")

add_selectbox = st.sidebar.selectbox(
    "More Information",
    ["Homepage", "Search by Country", "Top 10 Chart"]
)
if add_selectbox == "Homepage":
    st.info(
        "Welcome to the COVID-19 Tracker website! Here you can see COVID data based on countries all over the world.")
    st.markdown("Here are some reminders to stay healthy and prevent COVID:")
    # checkbox widget
    show_tips = st.checkbox("Show Health Tips")

    if show_tips:
        st.markdown("""
            **Health Tips:**
            - **Wear Masks:** Always wear a mask in public spaces to reduce the risk of spreading the virus.
            - **Social Distancing:** Maintain a distance of at least 6 feet from others to avoid transmission.
            - **Hand Hygiene:** Wash your hands frequently with soap and water for at least 20 seconds.
            - **Avoid Crowded Places:** Avoid large gatherings and crowded places to minimize exposure.
            - **Stay Informed:** Keep up-to-date with the latest guidelines and recommendations from health authorities.
            """)

    video_url = "https://www.youtube.com/watch?v=mSADUWSqNqU"
    st.video(video_url)

if add_selectbox == "Search by Country":
    st.info("See the COVID stats on any Country.")

    category = st.selectbox("Choose a Category", ["Enter Country Code", "Select from Dropdown"])

    if category == "Enter Country Code":
        country = st.text_input("Enter the country code (Example: 'IT', 'USA', 'CA')")
        is_code = True
        data_options = st.multiselect("What results would you like to see?",
                                      ["Number of deaths", "Number of confirmed cases", "Number of recovered cases",
                                       "Number of critical cases"],
                                      ["Number of deaths", "Number of confirmed cases", "Number of recovered cases",
                                       "Number of critical cases"])
        if st.button("Get Report"):
            if country:
                result = fetch_covid_data(country, is_code)
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Success!")
                    st.subheader(f"COVID-19 Report for {country}:")

                    data_dict = {}
                    if "Number of deaths" in data_options:
                        data_dict["Number of deaths"] = [result['deaths']]
                    if "Number of confirmed cases" in data_options:
                        data_dict["Number of confirmed cases"] = [result['confirmed']]
                    if "Number of recovered cases" in data_options:
                        data_dict["Number of recovered cases"] = [result['recovered']]
                    if "Number of critical cases" in data_options:
                        data_dict["Number of critical cases"] = [result['critical']]

                    df = pd.DataFrame(data_dict)
                    st.dataframe(df)

                    latitude, longitude = get_coordinates(country, is_code)
                    if latitude and longitude:
                        map_ = map_creator(latitude, longitude)
                        folium_static(map_)
                    else:
                        st.error("Could not find the location.")
            else:
                st.error("Please enter or select a country.")


    if category == "Select from Dropdown":
        countries_dict = get_list_of_countries()
        if countries_dict:
            countries_list = [country['name'] for country in countries_dict]
            country = st.selectbox("Select a country", options=countries_list)
            is_code = False

            data_options = st.multiselect("What results would you like to see?",
                                          ["Number of deaths", "Number of confirmed cases", "Number of recovered cases",
                                           "Number of critical cases"],
                                          ["Number of deaths", "Number of confirmed cases", "Number of recovered cases",
                                           "Number of critical cases"])
            if st.button("Get Report"):
                if country:
                    result = fetch_covid_data(country, is_code)
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success("Success!")
                        st.subheader(f"COVID-19 Report for {country}:")

                        data_dict = {}
                        if "Number of deaths" in data_options:
                            data_dict["Number of deaths"] = [result['deaths']]
                        if "Number of confirmed cases" in data_options:
                            data_dict["Number of confirmed cases"] = [result['confirmed']]
                        if "Number of recovered cases" in data_options:
                            data_dict["Number of recovered cases"] = [result['recovered']]
                        if "Number of critical cases" in data_options:
                            data_dict["Number of critical cases"] = [result['critical']]

                        df = pd.DataFrame(data_dict)
                        st.dataframe(df)

                        latitude, longitude = get_coordinates(country, is_code)
                        if latitude and longitude:
                            map_ = map_creator(latitude, longitude)
                            folium_static(map_)
                        else:
                            st.error("Could not find the location.")
                else:
                    st.error("Please enter or select a country.")

if add_selectbox == "Top 10 Chart":
    data = pd.DataFrame({
        'Country': ['USA', 'India', 'Brazil', 'France', 'Germany', 'UK', 'Russia', 'Turkey', 'Italy', 'Spain'],
        'Cases': [111820082, 45035393, 38743918, 40138560, 38828995, 24910387, 24124215, 17232066, 26723249, 13914811]
    })



    top_10_countries = data.sort_values(by='Cases', ascending=False).head(10)

    chart_type = st.radio("Select Chart Type", ("Bar Graph", "Line Chart"))

    if chart_type == "Bar Graph":
        # Color picker
        bar_color = st.color_picker("Pick a color for the bar graph", "#ff0000")

        fig, ax = plt.subplots()
        bars = ax.bar(top_10_countries['Country'], top_10_countries['Cases'], color=bar_color)

        ax.set_xlabel('Country')
        ax.set_ylabel('Number of COVID-19 Cases')
        ax.set_title('Top 10 Countries by COVID-19 Cases')
        plt.xticks(rotation=45, ha='right')

        # Set the graph limits
        def format_yaxis(value, tick_number):
            if value >= 1_000_000:
                return f'{value / 1_000_000:.1f}M'
            elif value >= 1_000:
                return f'{value / 1_000:.1f}K'
            else:
                return value


        ax.yaxis.set_major_formatter(FuncFormatter(format_yaxis))

        ax.set_ylim(0, top_10_countries['Cases'].max() * 1.1)

        st.pyplot(fig)

    if chart_type == "Line Chart":
        line_chart_data = pd.DataFrame({
            'Cases': top_10_countries.set_index('Country')['Cases']
        })
        st.line_chart(line_chart_data)