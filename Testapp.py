import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title = "Lager Beholdning", layout = "wide")

#Google sheets api
def setupApi():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("LagerBeholdning").sheet1
    data = client.open
    #gets data from sheets and turns it into a pandas dataframe
    data = sheet.get_all_records()
    return pd.DataFrame(data)
 
@st.cache #cacheing it to only run computations again if the datafram changes
def cachable(dataframe):
    #gets values in dataframe for easier computation
    valuesInDataframe = dataframe.to_numpy()
    #Adds column displaying Storage Status
    storageStatus = []
    for item in valuesInDataframe:
        if item[1] - item[2] > 0:
            storageStatus.append("Ønsket mengde")
        elif item[1] > 0:
            storageStatus.append("Lite på lager")
        else:
            storageStatus.append("Ikke på lager")
    
    #adds storage status as new column to dataframe
    dataframe["Lagerstatus"] = storageStatus
    
    #creates a list with the items not in stock
    notInStock = dataframe[dataframe["Lagerstatus"] == "Ikke på lager"]
    notInStock = notInStock["Navn"].to_list()
    return dataframe, notInStock

#gets the data from the cached function
dataframe, notInStock = cachable(setupApi().replace(r'^\s*$', np.nan, regex=True))#converts empty spaces to NaN to avoid error

#sidebar
with st.sidebar:
    #adds a search option in the sidebar
    st.title("Valg muligheter:")    
    search = st.text_input("Søk etter navn her:")
    storageStatus = st.sidebar.multiselect( #creates a multiselect to filter the dataframe
                                           "Hvilke varer som vises:",
                                           options=["Ønsket mengde", "Lite på lager", "Ikke på lager"],
                                           default=["Ønsket mengde", "Lite på lager"])

#filters the dataframe based on choises in the multiselect
dataframe = dataframe.query("Lagerstatus == @storageStatus") 
#filters the dataframe based on search
dataframe = dataframe[dataframe["Navn"].str.contains(search, case = False)] 

mainCol, rightCol = st.columns([2, 1])
#Main column
with mainCol:
    st.title("Lager Beholdning") 
    st.dataframe(dataframe)
   
#Right column
with rightCol:
    st.subheader("Ting vi er tomme for:")
    for item in notInStock:
        st.write("-",item)





