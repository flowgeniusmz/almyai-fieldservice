import streamlit as st
from simple_salesforce import Salesforce, SFType


# Function to connect to Salesforce using Streamlit secrets
def connect_to_salesforce():
    sf = Salesforce(
        username=st.secrets.salesforce.sfUsername,
        password=st.secrets.salesforce.sfPassword,
        security_token=st.secrets.salesforce.sfToken
    )
    return sf

# Function to execute the Salesforce query and return a DataFrame
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
        
    df = pd.DataFrame(query_result['records']).drop(columns='attributes')
    return df

# Function to update a case in Salesforce
def update_case(sf, case_id, update_fields):
    sf.Case.update(case_id, update_fields)
