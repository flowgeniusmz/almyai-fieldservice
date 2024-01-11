import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
import uuid
import streamlit_modal as modal

@st.cache_data  # Corrected cache decorator
def fetch_cases():
    sf = Salesforce(username=st.secrets.salesforce.sfUsername, password=st.secrets.salesforce.sfPassword, security_token=st.secrets.salesforce.sfToken)
    query = """
        SELECT Id, Status, Type, Queues__c, Owner.Name, AccountId, Account.Name, Account.ShippingStreet, Account.ShippingCity,
        Account.ShippingState, Account.ShippingPostalCode, Account.ShippingLongitude,
        Account.ShippingLatitude FROM Case Where Account.Subsidiary__c = 'Alma Lasers , Inc.' AND Status = 'In Process' AND Type = 'Technical Support' AND Queues__c = 'Client Relations'
        ORDER BY Created_Date_Custom__c DESC
        Limit 200
        """
    data = sf.query(query)
    records = data['records']
    data_new = []
    for record in records:
        row_data = {
            'caseid': record['Id'],
            'status': record['Status'],
            'type': record['Type'],
            'queue': record['Queues__c'],
            'owner_name': record['Owner']['Name'],
            'accountid': record['AccountId'],
            'accountname': record.get('Account', {}).get('Name', ''),
            'shippingstreet': record.get('Account', {}).get('ShippingStreet', ''),
            'shippingcity': record.get('Account', {}).get('ShippingCity', ''),
            'shippingstate': record.get('Account', {}).get('ShippingState', ''),
            'shippingpostalcode': record.get('Account', {}).get('ShippingPostalCode', ''),
            'shippinglongitude': record.get('Account', {}).get('ShippingLongitude', ''),
            'shippinglatitude': record.get('Account', {}).get('ShippingLatitude', ''),
            # Add other fields as needed
        }
        data_new.append(row_data)
    return pd.DataFrame(data_new)

def show_case_modal(case):
    with modal.container():
        # Create a larger container and then use columns to center the actual content
        outer_col1, modal_container, outer_col2 = st.columns([1, 2, 1])  # Adjust the ratio as needed

        with modal_container:
            # Modal content goes here
            col1, col2 = st.columns(2)

            with col1:
                st.write("Case Details")
                st.text(f"Case ID: {case['caseid']}")
                st.text(f"Account ID: {case['accountid']}")
                st.text(f"Account Name: {case['accountname']}")
                st.text(f"Status: {case['status']}")
                st.text(f"Type: {case['type']}")
                st.text(f"Queue: {case['queue']}")
                # Add other case details as needed

            with col2:
                with st.form("update_form"):
                    subject = st.text_input("Subject", value="")
                    description = st.text_area("Description", value="")
                    # Add other form fields as needed
                    submitted = st.form_submit_button("Submit")

                    if submitted:
                        # Logic to handle form submission
                        st.success("Form submitted!")
                        # You can add logic to update Salesforce here

            if st.button("Exit"):
                modal.close()

def generate_row(row_id, case):
    row_container = st.empty()
    row_columns = row_container.columns((2, 2, 2, 2, 2, 1))
    row_columns[0].write(case['accountname'])
    row_columns[1].write(case['accountid'])
    row_columns[2].write(case['status'])
    row_columns[3].write(case['type'])
    row_columns[4].write(case['queue'])

    if row_columns[5].button("Details", key=f"btn_{row_id}"):
        show_case_modal(case)

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
