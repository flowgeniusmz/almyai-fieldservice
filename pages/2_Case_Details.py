import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
import uuid

# Function to fetch cases from Salesforce
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
            'accountname': record.get('Account', {}).get('Name', ''),
            # Add other fields as needed
        }
        data_new.append(row_data)
    return pd.DataFrame(data_new)

# Initialize session state for rows
if "rows" not in st.session_state:
    st.session_state["rows"] = []

def remove_row(row_id):
    st.session_state["rows"].remove(str(row_id))

def generate_row(row_id, case):
    row_container = st.empty()
    row_columns = row_container.columns((2, 2, 1))
    row_columns[0].write(case['accountname'])
    row_columns[1].write(case['accountid'])
    row_columns[2].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])

def main():
    st.title("Salesforce Case Manager")

    cases_df = fetch_cases()

    # Sync the cases with session state
    if len(st.session_state["rows"]) == 0:
        for _, case in cases_df.iterrows():
            st.session_state["rows"].append((str(uuid.uuid4()), case))

    for row_id, case in st.session_state["rows"]:
        generate_row(row_id, case)

    # Display the cases
    if len(st.session_state["rows"]) > 0:
        st.subheader("Case Data")
        display = st.columns(1)
        data = pd.DataFrame([case for _, case in st.session_state["rows"]])
        display[0].dataframe(data=data, use_container_width=True)

if __name__ == "__main__":
    main()
