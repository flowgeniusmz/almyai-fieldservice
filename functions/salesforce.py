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
