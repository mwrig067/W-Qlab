import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

# Set your AirVisual API key here
api_key = "36ef961e-db9c-486f-9aad-1a19875f449c"

# Streamlit application layout
st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

# Function to create a map centered at a specified location
@st.cache_data
def map_creator(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Selected", tooltip="Station").add_to(m)
    print("Map Created")  # Add this line
    return m

# Function to fetch a list of countries from the AirVisual API
@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    return countries_dict

# Function to fetch a list of states for a selected country
@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    return states_dict

# Function to fetch a list of cities for a selected state and country
@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    return cities_dict

# Location selection method
category = st.sidebar.selectbox("Choose a category", ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"])

if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [country["country"] for country in countries_dict["data"]]
        countries_list.insert(0, "")

        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [state["state"] for state in states_dict["data"]]
                states_list.insert(0, "")

                state_selected = st.selectbox("Select a state", options=states_list)
                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [city["city"] for city in cities_dict["data"]]
                        cities_list.insert(0, "")

                        city_selected = st.selectbox("Select a city", options=cities_list)
                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()

                            if aqi_data_dict["status"] == "success":
                                # Parse and display weather and air quality data
                                st.subheader("Weather and Air Quality Information")
                                st.write(f"Temperature: {aqi_data_dict['data']['current']['weather']['tp']}°C")
                                st.write(f"Humidity: {aqi_data_dict['data']['current']['weather']['hu']}%")
                                st.write(f"Air Quality Index (AQI): {aqi_data_dict['data']['current']['pollution']['aqius']}")

                                # Display map
                            # Display map
                            st.subheader("Location Map")
                            location_data = aqi_data_dict.get('data', {}).get('location', {})
                            print("Location Data:", location_data)  # Add this line

                            if location_data:
                                coordinates_list = location_data.get('coordinates', [{}])
                                print("Coordinates List:", coordinates_list)  # Add this line
                                if coordinates_list:
                                    coordinates = coordinates_list[0]
                                    print("Coordinates:", coordinates)  # Add this line
                                    longitude = coordinates.get('longitude')
                                    latitude = coordinates.get('latitude')

                                    if latitude is not None and longitude is not None:
                                        my_map = map_creator(latitude, longitude)
                                        folium_static(my_map)
                                    else:
                                        st.warning("Invalid latitude or longitude. Coordinates must be numeric.")
                                else:
                                    st.warning("Coordinates list is empty.")
                            else:
                                st.warning("No data available for this location.")


elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        # Parse and display weather and air quality data
        st.subheader("Weather and Air Quality Information")
        st.write(f"Temperature: {aqi_data_dict['data']['current']['weather']['tp']}°C")
        st.write(f"Humidity: {aqi_data_dict['data']['current']['weather']['hu']}%")
        st.write(f"Air Quality Index (AQI): {aqi_data_dict['data']['current']['pollution']['aqius']}")

        # Display map
    st.subheader("Location Map")
    location_data = aqi_data_dict.get('data', {}).get('location', {})
    if location_data:
        latitude = location_data.get('coordinates', {}).get('latitude')
        longitude = location_data.get('coordinates', {}).get('longitude')

        if latitude is not None and longitude is not None:
            map_creator(latitude, longitude)
        else:
            st.warning("Latitude or longitude information not available.")
    else:
        st.warning("Location data not available.")

   # else:
       # st.warning("No data available for the nearest city.")

elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter Latitude:")
    longitude = st.text_input("Enter Longitude:")
    if st.button("Submit"):
      if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            st.warning("Invalid latitude or longitude. Please enter valid numeric values.")
        else:
            url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
            aqi_data_dict = requests.get(url).json()

            if aqi_data_dict["status"] == "success":
                # Parse and display weather and air quality data
                st.subheader("Weather and Air Quality Information")
                st.write(f"Temperature: {aqi_data_dict['data']['current']['weather']['tp']}°C")
                st.write(f"Humidity: {aqi_data_dict['data']['current']['weather']['hu']}%")
                st.write(f"Air Quality Index (AQI): {aqi_data_dict['data']['current']['pollution']['aqius']}")

                # Display map
                st.subheader("Location Map")
                map_creator(latitude, longitude)
            else:
                st.warning("No data available for this location.")
