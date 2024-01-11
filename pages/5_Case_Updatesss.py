import streamlit as st
from streamlit_modal import Modal
import pandas as pd
from simple_salesforce import Salesforce
from functions import pagesetup as ps

#Set Title
ps.set_title("Field Service", "Case Updates")

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
    row_data = {
            'caseid': record['Id'],
            'accountid': record['AccountId'],
            'accountname': record['Account']['Name'],
            'street': record['Account']['ShippingStreet'],
            'city': record['Account']['ShippingCity'],
            'state': record['Account']['ShippingState'],
            'zipcode': record['Account']['ShippingPostalCode'],
            'longitude': record['Account']['ShippingLongitude'],
            'latitude': record['Account']['ShippingLatitude']
        }
    data_new.append(row_data)
  df = pd.DataFrame(data_new)
  return df

# Function to update a case in Salesforce
def update_case(sf, case_id, update_fields):
    sf.Case.update(case_id, update_fields)


# Function to create modal
def create_modal(title, key, padding, width):
  new_modal = Modal(
    title=title,
    key=key,
    padding=20,
    max_width=744
  )
  return new_modal

# Function to show case details in a modal
def show_case_modal(case_data):
  modal = create_modal("View and Update Case", f"casemodal{case_data['Id']}", 20, 744) 
  with modal.container():
    mcontainer1 = st.container()
    with mcontainer1:
      cc = st.columns(2)
      with cc[0]:
        st.markdown(case_data)
      with cc[1]:
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
                    update_case(sf, case_data['caseid'], update_fields)
                    st.success("Case updated successfully")
                    # Clear the selected case id from session state after updating
                    del st.session_state.selected_case_id
                    del st.session_state.selected_case_data
                    st.rerun()
    mcontainer2 = st.container()
    with mcontainer2:
      if st.button("Exit"):
            # Clear the selected case id from session state and close the modal
            del st.session_state.selected_case_id
            del st.session_state.selected_case_data
            rerun()
      
# Main Streamlit app function
def main():
    

    # Fetch cases from Salesforce and display the DataFrame
    cases_df = fetch_cases()
    st.dataframe(cases_df)

    # Add a 'View Details' button for each case in the DataFrame
    for index, case in cases_df.iterrows():
        if st.button("View Details", key=case['Id']):
            st.session_state.selected_case_id = case['caseid']
            st.session_state.selected_case_data = case.to_dict()
            show_case_modal(st.session_state.selected_case_data)

    # Clear the session state if not viewing details
    if 'selected_case_id' not in st.session_state:
        st.session_state.selected_case_data = None

if __name__ == "__main__":
    main()
