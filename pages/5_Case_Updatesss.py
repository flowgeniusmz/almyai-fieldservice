import streamlit as st
from streamlit_modal import Modal
import pandas as pd
from simple_salesforce import Salesforce
from functions import pagesetup as ps

# Fetch Data
@st.cache
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
        # Ensure 'Id' is present in the record
        if 'Id' in record:
            row_data = {
                'caseid': record['Id'],
                'accountid': record['AccountId'],
                'accountname': record.get('Account', {}).get('Name', ''),
                'street': record.get('Account', {}).get('ShippingStreet', ''),
                'city': record.get('Account', {}).get('ShippingCity', ''),
                'state': record.get('Account', {}).get('ShippingState', ''),
                'zipcode': record.get('Account', {}).get('ShippingPostalCode', ''),
                'longitude': record.get('Account', {}).get('ShippingLongitude', ''),
                'latitude': record.get('Account', {}).get('ShippingLatitude', '')
            }
            data_new.append(row_data)
    return pd.DataFrame(data_new)

def main():
    # Set Title
    ps.set_title("Field Service", "Case Updates")

    df = fetch_cases()
    containerdf = st.container()
    with containerdf:
        # Use a conditional check to ensure 'Id' is a column in the DataFrame
        if 'Id' in df.columns:
            edited_df = st.data_editor(df, key="casedf_edited", num_rows="dynamic")
        else:
            st.error("Error: 'Id' column is missing in the data")

    containerdf2 = st.container()
    with containerdf2:
        exp = st.expander("View changes made", expanded=False)
        with exp:
            st.write(st.session_state.get('casedf_edited', 'No changes made'))

if __name__ == "__main__":
    main()
