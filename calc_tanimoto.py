from chembl_webresource_client.new_client import new_client
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
import itertools


# Initialize ChEMBL client
molecule = new_client.molecule

# List of compound names for which you want to fetch SMILES
compound_names = ["Curcumin", "Resveratrol"] #,...

# Fetch SMILES strings from ChEMBL
def get_smiles(compound_names):
    smiles_dict = {}
    for name in compound_names:
        results = molecule.search(name)
        if results:
            try:
                smiles_dict[name] = results[0]['molecule_structures']['canonical_smiles']
            except:
                print(name, " no data")
    return smiles_dict

smiles_dict = get_smiles(compound_names)

# Generate fingerprints
fingerprints = {}
for name, smiles in smiles_dict.items():
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
        fingerprints[name] = fp

# Calculate Tanimoto similarity between all pairs of compounds
def calculate_similarities(fingerprints):
    similarity_results = []
    for (name1, fp1), (name2, fp2) in itertools.combinations(fingerprints.items(), 2):
        similarity = DataStructs.FingerprintSimilarity(fp1, fp2)
        similarity_results.append([name1,name2,similarity])
    return similarity_results

similarity_results = calculate_similarities(fingerprints)

for i in similarity_results:
    print(i)