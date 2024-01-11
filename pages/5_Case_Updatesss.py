import streamlit as st
from streamlit_modal import Modal
import pandas as pd
from simple_salesforce import Salesforce
from functions import pagesetup as ps

#Set Title
ps.set_title("Field Service", "Case Updates")

# Fetch Data
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
    

