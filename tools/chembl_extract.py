# Load ChEMBL information for bioactives
from chembl_webresource_client.new_client import new_client


def get_chembl_attributes(name):
    #takes molecule name and returns all chembl information

    molecule = new_client.molecule
    drug_indication = new_client.drug_indication

    mols = molecule.filter(pref_name__iexact=name)
    if len(mols) == 0:
        return {'drug_indications':[]}
    moldic = list(mols)[0]
    chembl_id = moldic.get('molecule_chembl_id')
    drug_in = drug_indication.filter(molecule_chembl_id=chembl_id) #returns list of all diseases drug has been tested for

    diseases = []
    for ind in list(drug_in):
        diseases.append(ind.get('efo_term'))

    moldic['drug_indications'] = diseases
    return moldic

print(get_chembl_attributes('Phenylpropanolamine')['natural_product'])