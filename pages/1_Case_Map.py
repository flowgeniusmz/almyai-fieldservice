import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup  # Import the Popup class
import pandas as pd
from functions import pagesetup as ps
from simple_salesforce import Salesforce

# Set Title
ps.set_title("Field Service", "Case Map")

# Get Salesforce Data
sf = Salesforce(
 username = st.secrets.salesforce.sfUsername,
 password = st.secrets.salesforce.sfPassword,
 security_token = st.secrets.salesforce.sfToken
)

query = """
SELECT Id, AccountId, Account.Name, Account.ShippingStreet, Account.ShippingCity, Account.ShippingState, Account.ShippingPostalCode, Account.ShippingLongitude, Account.ShippingLatitude FROM Case Where Account.Subsidiary__c = 'Alma Lasers , Inc.'
"""

data = sf.query(query)
records = data['records']
data1 = []
for record in records:
  row_data = {
      'caseid': record['Id'],
      'accountid': record['AccountId'],
      'accountname': record['Account']['Name'],
      'street': record['Account']['ShippingStreet'],
      'city': record['Account']['ShippingCity'],
      'state': record['Account']['ShippingState'],
      'zipcode': record['Account']['ShippingPostalCode'],
      'longitude': record['Account']['ShippingLongitude'],
      'latitude': record['Account']['ShippingLatitude']
  }
  data1.append(row_data)

df = pd.DataFrame(data1)

container 1 = st.container()
with container1:
 us_center = (39.8283, -98.5795)
 map = folium.Map(lcoation=us_center, zoom_start = 4)
 for _, case in df.iterrows():
  location = case['latitude'], case['longitude']
  folium.Marker(
   location = location,
   popup=Popup("Case Data", parse_html=False),
   tooltip = f"Case at {location}",
  ).add_to(map)

st.header("Live Case Data")
out = st_folium(map, width=1000)
st.write("Popup:", out["last_object_clicked_popup"])
st.write("Tooltip:", out["last_object_clicked_tooltip"])
