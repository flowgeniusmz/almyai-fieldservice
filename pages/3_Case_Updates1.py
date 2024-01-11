# Importing required libraries
import streamlit as st
from simple_salesforce import Salesforce
import pandas as pd
import streamlit_modal as modal
from functions import pagesetup as ps

ps.set_title("Field Service", "Case Updates")

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
    query_result = sf.query(query)
    df = pd.DataFrame(query_result['records']).drop(columns='attributes')
    return df

# Function to show case details in a modal
def show_case_modal(case_id, sf):
    case_query = f"SELECT Id, Subject, Description FROM Case WHERE Id = '{case_id}'"
    case_details = sf.query(case_query)
    case_info = pd.DataFrame(case_details['records']).drop(columns='attributes')

    with modal.container():
        col1, col2 = st.columns([2, 3])

        with col1:
            st.write(case_info)

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
                        'Description': description,
                        # Additional fields for comments and notes can be handled here
                    }
                    sf.Case.update(case_id, update_fields)
                    st.success("Case updated successfully")
                    modal.close()

# Main Streamlit app function
def main():
    st.title("Salesforce Case Manager")

    # Connect to Salesforce
    sf = connect_to_salesforce()

    # Fetch cases from Salesforce
    cases_df = fetch_cases(sf)
    # Convert complex nested JSON to string for display purposes
    cases_df['Account'] = cases_df['Account'].apply(lambda x: str(x))

    # Display cases in a table with a clickable "Details" button
    for index, case in cases_df.iterrows():
        # Create a button for each case
        if st.button(f"Details for {case['Id']}", key=case['Id']):
            # If button is clicked, store the case_id in the session state
            st.session_state.selected_case_id = case['Id']
            # Trigger a rerun to refresh the page and open the modal
            st.rerun()

    # Check if a case_id is stored in session state to open the modal
    if 'selected_case_id' in st.session_state:
        # Call the function to show the modal with case details and form
        show_case_modal(st.session_state.selected_case_id, sf)

# Run the Streamlit app
if __name__ == "__main__":
    main()
