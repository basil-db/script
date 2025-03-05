# Basil Script

Please visit [the BASIL DB website](https://basil-db.github.io/info.html) for more information.

This repo gives some of the functionalities used for building the database.

Please adjust the API key in prompt_health_effects.py as well as the details for the MetaMap installation in NER.py.

To run MetaMap, please follow the instructions from the [MetaMap GitHub page](https://github.com/Bin-Chen-Lab/metamap): 

"MetaMap includes two major parts (its server including the knowledge-base and various internal algorithms, and its APIs used to call the server to finish your job).  You can install the server locally and use Java APIs (or the commands) to call the server.

### Install and start MetaMap

1)	Download MetaMap full version and extract into the directory called (public_mm)

2)	Install it locally. It will ask the directory you want install and the JAVA-HOME (/System/Library/Frameworks/JavaVM.framework/Versions/1.6.0)

  - 	cd public_mm
  - 	./bin/install.sh
  
3)	Start the server

  - 	./bin/skrmedpostctl start
  - 	./bin/wsdserverctl start
  - 	./bin/metamap12

### Call MetaMap and process the output. 

1)	python call_metamap.py input_file, output_file, tempt_file, meta_map path
```sh
python call_metamap.py ttd_dz.txt ttd_dz_out.txt test /Users/User/Downloads/public_mm/bin/metamap12
```
