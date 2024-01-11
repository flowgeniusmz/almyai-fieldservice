import streamlit as st
from simple_salesforce import Salesforce, SFType
import pandas as pd

# Function to connect to Salesforce using Streamlit secrets
def connect_to_salesforce():
    sf = Salesforce(
        username=st.secrets.salesforce.sfUsername,
        password=st.secrets.salesforce.sfPassword,
        security_token=st.secrets.salesforce.sfToken
    )
    return sf

# Function to execute the Salesforce query and return a DataFrame
@st.cache_data
def fetch_cases(sf):
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
