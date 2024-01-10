import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup  # Import the Popup class
import pandas as pd
from functions import pagesetup as ps

ps.set_title("Field Service", "Case Map")

 container1 = st.container()
    with container1:
        
        dfSensors = get_dataframe(get_data_sensors())
        US_center = (39.8283, -98.5795)
        map = folium.Map(location=US_center, zoom_start=4)
        for _, sensor in dfSensors.iterrows():
            location = sensor['latitude'], sensor['longitude']
            folium.Marker(
                location=location,
                popup=Popup("Sensor Data", parse_html=False),
                tooltip=f"Sensor at {location}",
            ).add_to(map)
    
        st.header("Live read Sensor data")
        out = st_folium(map, width=1000)  # Capture the output into 'out'
        st.write("Popup:", out["last_object_clicked_popup"])
        st.write("Tooltip:", out["last_object_clicked_tooltip"])
