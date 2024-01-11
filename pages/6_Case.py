import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
from functions import pagesetup as ps
from streamlit_modal import Modal

# Functions

## Function 1: Fetch Cases from Salesforce
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


def show_case_modal(case_id, sf):
    case_query = f"SELECT Id, Subject, Description FROM Case WHERE Id = '{case_id}'"
    case_details = sf.query(case_query)
    case_info = pd.DataFrame(case_details['records']).drop(columns='attributes')

    with modal.container():
        col1, col2 = st.columns(2)

        with col1:
            st.write(case_info.iloc[0])

        with col2:
            with st.form("update_form"):
                subject = st.text_input("Subject", case_info.iloc[0]['Subject'])
                description = st.text_area("Description", case_info.iloc[0]['Description'])
                comments = st.text_area("Comments")
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Submit")

                if submitted:
                    update_fields = {
                        'Subject': subject,
                        'Description': description
                        # 'Comments': comments, 'Notes': notes (if your Salesforce setup has these fields)
                    }
                    update_case(sf, case_id, update_fields)
                    st.success("Case updated successfully")
                    # Clear the selected case id from session state after updating
                    if 'selected_case_id' in st.session_state:
                        del st.session_state.selected_case_id
                    modal.close()

        if st.button("Exit"):
            # Clear the selected case id from session state and close the modal
            if 'selected_case_id' in st.session_state:
                del st.session_state.selected_case_id
            modal.close()


def main():
    ps.set_title("Field Service", "Salesforce")

    # Fetch cases from Salesforce
    cases_df = fetch_cases()

    # Display headers
    col_headers = st.columns(len(cases_df.columns) + 1)  # +1 for the Details button
    headers = list(cases_df.columns) + ['Details']
    for header, col in zip(headers, col_headers):
        col.write(header)

    # Display each row as a row of columns
    for index, case in cases_df.iterrows():
        cols = st.columns(len(case) + 1)  # +1 for the Details button

        # Display each field in a separate column
        for col, value in zip(cols[:-1], case):
            col.write(value)

        # Display the details button in the last column
        if cols[-1].button(f"Details", key=case['Id']):
            # If button is clicked, store the case_id in the session state
            st.session_state.selected_case_id = case['Id']
            # Trigger a rerun to refresh the page and open the modal
            st.rerun()

    # Check if a case_id is stored in session state to open the modal
    if 'selected_case_id' in st.session_state:
        show_case_modal(st.session_state.selected_case_id, sf)

if __name__ == "__main__":
    main()
