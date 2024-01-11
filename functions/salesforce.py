import streamlit as st
from simple_salesforce import Salesforce, SFType


sfU = st.secrets.salesforce.sfUsername
sfP = st.secrets.salesforce.sfPassword
sfT = st.secrets.salesforce.sfToken
