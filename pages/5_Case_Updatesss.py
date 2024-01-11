import streamlit as st
from streamlit_modal import Modal
import pandas as pd
from simple_salesforce import Salesforce
from functions import pagesetup as ps



# Fetch Data
@st.cache_data
def fetch_cases():
  sf = Salesforce(username=st.secrets.salesforce.sfUsername, password=st.secrets.salesforce.sfPassword, security_token=st.secrets.salesforce.sfToken)
  query = """
    SELECT Id, AccountId, Account.Name, Account.ShippingStreet, Account.ShippingCity,
    Account.ShippingState, Account.ShippingPostalCode, Account.ShippingLongitude,
    Account.ShippingLatitude FROM Case Where Account.Subsidiary__c = 'Alma Lasers , Inc.' Limit 200
    """
  data = sf.query(query)
  records = data['records']
  data_new = []
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
    data_new.append(row_data)
  df = pd.DataFrame(data_new)
  return df

# Function to update a case in Salesforce
def update_case(sf, case_id, update_fields):
    sf.Case.update(case_id, update_fields)


# Function to create modal
def create_modal(title, key, padding, width):
  new_modal = Modal(
    title=title,
    key=key,
    padding=20,
    max_width=744
  )
  return new_modal

def main():
  #Set Title
  ps.set_title("Field Service", "Case Updates")

  df = fetch_cases()
  containerdf = st.container()
  with containerdf:
    edited_df = st.data_editor(df, key="casedf_edited", num_rows = "dynamic")

containerdf2 = st.container()
with containerdf2:
  exp = st.expander("View changes made", expanded = False)
  with exp:
    st.write(st.session_state.casedf_edited)
    
  
  
  
if __name__ == "__main__":
    main()
