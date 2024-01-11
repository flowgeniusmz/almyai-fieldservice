# Importing required libraries
import streamlit as st
from simple_salesforce import Salesforce, SFType
import pandas as pd
from functions import pagesetup as ps

# Set page title
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

# Function to update a case in Salesforce
def update_case(sf, case_id, update_fields):
    case = SFType('Case', sf.session_id, sf.sf_instance)
    response = case.update(case_id, update_fields)
    return response

# Streamlit app main function
def main():
    st.title("Salesforce Case Manager")

    # Connect to Salesforce
    sf = connect_to_salesforce()

    # Fetch cases from Salesforce
    cases_df = fetch_cases(sf)
    cases_df['Details'] = cases_df['Id'].apply(lambda x: f"[Details]({x})")

    # Display cases in a table
    st.dataframe(cases_df)

    # Handling case detail view
    query_params = st.experimental_get_query_params()
    selected_case_id = query_params.get('case_id', [None])[0]

    if selected_case_id:
        # Fetch detailed case data
        detailed_case_query = f"SELECT Id, Subject, Description FROM Case WHERE Id = '{selected_case_id}'"
        detailed_case = sf.query(detailed_case_query)
        detailed_case_df = pd.DataFrame(detailed_case['records']).drop(columns='attributes')

        # Display editable fields
        with st.form("case_update_form"):
            subject = st.text_input("Subject", detailed_case_df.iloc[0]['Subject'])
            description = st.text_area("Description", detailed_case_df.iloc[0]['Description'])
            comments = st.text_area("Comments")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Submit")

            if submitted:
                # Update case in Salesforce
                update_fields = {
                    'Subject': subject,
                    'Description': description,
                    # Additional fields for comments and notes can be added if supported by Salesforce schema
                }
                update_response = update_case(sf, selected_case_id, update_fields)
                if update_response == 204:  # HTTP status code for successful update
                    st.success("Case updated successfully")
                    # Redirect back to the main page
                    st.experimental_set_query_params()

# Run the Streamlit app
if __name__ == "__main__":
    main()
