import streamlit as st
from simple_salesforce import Salesforce
import pandas as pd
import streamlit_modal as modal

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

# Function to update a case in Salesforce
def update_case(sf, case_id, update_fields):
    sf.Case.update(case_id, update_fields)

# Function to show case details in a modal
def show_case_modal(case_data):
    with modal.container():
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write(case_data)

        with col2:
            with st.form("update_form"):
                subject = st.text_input("Subject", case_data.get('Subject', ''))
                description = st.text_area("Description", case_data.get('Description', ''))
                comments = st.text_area("Comments")
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Submit")

                if submitted:
                    update_fields = {
                        'Subject': subject,
                        'Description': description
                        # Include fields for comments and notes if they are to be updated in Salesforce
                    }
                    update_case(sf, case_data['Id'], update_fields)
                    st.success("Case updated successfully")
                    # Clear the selected case id from session state after updating
                    if 'selected_case_id' in st.session_state:
                        del st.session_state.selected_case_id
                    modal.close()

# Main Streamlit app function
def main():
    st.title("Salesforce Case Manager")

    # Connect to Salesforce
    sf = connect_to_salesforce()

    # Fetch cases from Salesforce
    cases_df = fetch_cases(sf)

    # Display cases in a table with a clickable "Details" button for each row
    for index, case in cases_df.iterrows():
        case_details = case.to_dict()
        case_details['Account'] = str(case_details['Account'])  # Convert Account detail to string for display
        cases_df.at[index, 'Details'] = 'View Details'
    
    # Create a button for each case and handle the click
    for i in range(len(cases_df)):
        if st.button('View Details', key=i):
            st.session_state.selected_case_data = cases_df.iloc[i].to_dict()
            st.session_state.selected_case_id = cases_df.iloc[i]['Id']
            show_case_modal(st.session_state.selected_case_data)

    # Clear the selected case data from session state if the modal is closed without submission
    if 'selected_case_id' in st.session_state and not modal.is_open():
        del st.session_state.selected_case_id
        del st.session_state.selected_case_data

if __name__ == "__main__":
    main()
