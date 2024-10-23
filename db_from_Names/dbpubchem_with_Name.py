import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to find the CID for a given compound name
def findCID(compound_name):
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/XML'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')  # Parse as XML

        # Find the CID in the XML structure
        cid_tag = soup.find('PC-CompoundType_id_cid')
        if cid_tag:
            cid = cid_tag.text.strip()
            print(f"CID found: {cid} for compound {compound_name}")
            return cid
        else:
            print(f"No CID found for compound {compound_name}")
    else:
        print(f"Error fetching CID for {compound_name}: {response.status_code}")

    return None  # Return None if CID not found

# Function to find the SMILES for a given CID
# Function to find the first SMILES for a given CID

def findSMILE(cid):
    # This function retrieves the SMILES for a given CID
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/XML/?response_type=display"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')  # Parse as XML

        # Find the SMILES section
        smiles_section = soup.find('TOCHeading', string='SMILES')
        if smiles_section:
            # Locate the parent <Section> of the SMILES heading
            section = smiles_section.find_parent('Section')
            if section:
                # Find the <Value> containing the SMILES
                value = section.find('Value')
                if value:
                    smiles_string = value.find('String').text.strip()
                    print(f"SMILES found: {smiles_string} for CID {cid}")
                    return smiles_string
                else:
                    print(f"No Value found in SMILES section for CID {cid}")
        else:
            print(f"No SMILES section found for CID {cid}")
    else:
        print(f"Error fetching data for CID {cid}: {response.status_code}")

    return 'N/A'  # Return 'N/A' if not found


def findMW(cid):
    # This function retrieves the molecular weight for a given CID
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/XML/?response_type=display"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')  # Parse as XML

        # Find the Molecular Weight section
        mw_section = soup.find('TOCHeading', string='Molecular Weight')
        if mw_section:
            # Locate the parent <Section> of the Molecular Weight heading
            section = mw_section.find_parent('Section')
            if section:
                # Find the <Value> containing the Molecular Weight
                value = section.find('Value')
                if value:
                    mw_string = value.find('String').text.strip()
                    print(f"Molecular Weight found: {mw_string} for CID {cid}")
                    return mw_string
                else:
                    print(f"No Value found in Molecular Weight section for CID {cid}")
        else:
            print(f"No Molecular Weight section found for CID {cid}")
    else:
        print(f"Error fetching data for CID {cid}: {response.status_code}")

    return 'N/A'  # Return 'N/A' if not found


# Read compound names from a file and return as a list
def read_compound_names_from_file(filename):
    with open(filename, 'r') as file:
        names = [line.strip() for line in file if line.strip()]
    return names

def main():
    compound_names = read_compound_names_from_file('input_names.txt')  # Read names from input_names.txt
    compounds_data = []

    for compound_name in compound_names:
        # Find the CID for the compound name
        cid = findCID(compound_name)

        if cid:
            url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Debug: Print the title of the page
                page_title = soup.title.string

                # Extract relevant information
                title_parts = page_title.split(" | ")
                compound_name = title_parts[0] if len(title_parts) >= 2 else 'N/A'
                chemical_formula = title_parts[1] if len(title_parts) >= 2 else 'N/A'
                smiles = findSMILE(cid)
                molecular_weight = findMW(cid)  # Call the function to find Molecular Weight

                # Append compound data to the list
                compounds_data.append({
                    'Name': compound_name,
                    'ID': cid,
                    'Formula': chemical_formula,
                    'Molecular Weight': molecular_weight,
                    'SMILES': smiles
                })
            else:
                print(f"Error fetching data for CID {cid}: {response.status_code}")

    # Create a DataFrame to display the data in tabular format
    df = pd.DataFrame(compounds_data)

    # Save the DataFrame to a CSV file
    df.to_csv('output_with_Name.csv', index=False)

    # Print the DataFrame
    print(df)

if __name__ == "__main__":
    main()
