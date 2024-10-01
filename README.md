## HG008_Data workflow_automation

This repo contains all the scripts that can be used to automate the post-QC steps such as generate a template README and also QC metrics sharing and filling out the metrics in the Manifest and the README. Multiple python scripts are available to use for automation of some of the Post-QC steps done after Mapping and QC data is generated

![Data_automation_workflow-2](https://github.com/user-attachments/assets/31d24711-d557-40b5-952b-2a348032db4f)



## Scripts file list 

--SheetstoDocs.py - This Google App script converts the Google sheets to a Google Docs that can be used to convert to markdown file format for a Template README for a FTP

--Rename_files.py - This python script renames all the files for the FTP staging and QC files sharing

--create_aMD_table.py - This python script creates a markdown table in .md by extracting the specific QC metrics from JSON for the FTP README or sharing purposes

--JSONtoCSV_manifestQC.py - This script exract the specific metrics from the JSON to the CSV format that also matches with column name of the HG008 data manifest. So metrics from the CSV can be copied to the Manifest directly.


## Notes : Email or message to Vaidehi P if you have any question regarding this scripts
