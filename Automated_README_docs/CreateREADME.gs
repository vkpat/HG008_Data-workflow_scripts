// This Google app script written in javascript helps to create an Automated README document by using a README template and replacing the placeholder in the template from Google Sheets, then creating a new filled README doc

function generateREADME() {
  const sheetId = "1ReRQ4OezLUBVJaPszVWYwEpd2WIqrftM_B6t_o8IObw"; // Replace with your actual Google Sheets ID, you dont need to replace this 
  const spreadsheet = SpreadsheetApp.openById(sheetId);
  const sheet = spreadsheet.getSheetByName("Form Responses 1"); // Replace with your actual sheet name

  if (!sheet) {
    Logger.log("Sheet not found.");
    return;
  }

  // Find the headers in the first row and get their column indices
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  if (!headers) {
    Logger.log("No headers found. Ensure the first row contains the column headers.");
    return;
  }

  const headerIndex = {};
  headers.forEach((header, index) => {
    headerIndex[header] = index + 1; // Save column index (1-based)
  });

  // Define the required headers from the sheets
  const requiredHeaders = [
    "Title of Dataset",
    "Submitter's name",
    "Measurement Institution", 
    "Dataset ID", 
    "Background", 
    "PI Name",
    "PI Institution",
    "PI email address",
    "Dataset contact(s)",
    "Dates of Data Collection",
    "Tumor-Normal GIAB ID(s)",
    "Tumor-Normal sample type",
    "Date sample(s) were received",
    "Internal sample ID(s)",
    "Sample QC performed", 
    "Institution sample(s) were received from",
    "Other sample information",
    "Recommend citations for the data",
    "File types",
    "File name convention",
    "Input into gDNA Isolation",
    "gDNA Isolation Method",
    "DNA Isolation Kit Information",
    "Isolated DNA Yield",
    "Isolated gDNA Size Distribution",
    "Are library prep methods either proprietary or R&D?",
    "Number of libraries",
    "gDNA mass into library prep",
    "Library preparation method",
    "Library prep kit information",
    "Library quality assurance",
    "Other library preparation information",
    "Are sequencing methods either proprietary or R&D?",
    "Measurement Platform",
    "Measurement platform software",
    "Sequencing method and chemistry",
    "Sequencing consumables",
    "Basecalling information",
    "How were libraries loaded?",
    "Other sequencing information",
    "Sequencing validation",
    "Alignment methods",
    "Reference genome used for alignment",
    "Coverage",
    "Alignment quality assurance",
    "name",
    "YYYY-MM-DD",
    "method e.g. google form, email, etc",
  ];

  // Check that all required headers are present
  for (let header of requiredHeaders) {
    if (!(header in headerIndex)) {
      Logger.log(`Header "${header}" not found in the sheet.`);
      return;
    }
  }

  // Retrieve data from Row # for the specified columns (only the second row)
  const data = {};
  requiredHeaders.forEach(header => {
    try {
      // Extract data from Row 4 (index 2 in Google Sheets is the second row)
      const value = sheet.getRange(4, headerIndex[header]).getValue(); // Get value from Row #, you have to change the row # here e.g. 4
      data[header] = (value === "" || value === null) ? "Not provided" : value;
      Logger.log(`Retrieved data for ${header}: ${data[header]}`);
    } catch (error) {
      Logger.log(`Error retrieving data for header "${header}": ${error.message}`);
      return;
    }
  });

  // Open the existing README template in Google Docs
  const templateDocId = "1uzxVwXJgFgW5IQ5YZFQH81NR7f9fVdt1nBLZPKIEilo"; // Do not need to Replace with your Google Doc ID, you can find the google Doc id from the browser link after /d/ 
  const templateDoc = DocumentApp.openById(templateDocId);
  const templateBody = templateDoc.getBody();

  if (!templateBody) {
    Logger.log("Error: Could not retrieve the body from the template document.");
    return;
  }

  // Create a new Google Doc for the generated README
  const newDoc = DocumentApp.create("UMD_Pacbio-revio_README"); // change the name of the new README file that you would like to use )
  const newBody = newDoc.getBody();

  // Copy each element from the template to the new document
  const numChildren = templateBody.getNumChildren();
  for (let i = 0; i < numChildren; i++) {
    const element = templateBody.getChild(i).copy();  // Copy each element
    const elementType = element.getType();

    // Append element based on its type
    switch (elementType) {
      case DocumentApp.ElementType.PARAGRAPH:
        newBody.appendParagraph(element);
        break;
      case DocumentApp.ElementType.LIST_ITEM:
        newBody.appendListItem(element);
        break;
      case DocumentApp.ElementType.TABLE:
        newBody.appendTable(element);
        break;
      case DocumentApp.ElementType.IMAGE:
        newBody.appendImage(element);
        break;
      default:
        Logger.log(`Unsupported element type: ${elementType}`);
        break;
    }
  }



  // Replace placeholders with data from the Google Sheet in the new document body
  newBody.replaceText("{“Title of Dataset”}", data["Title of Dataset"]);
  newBody.replaceText("{“Submitter's name”}", data["Submitter's name"]);
  newBody.replaceText("{“Measurement Institution”}", data["Measurement Institution"]);
  newBody.replaceText("{“DatasetID”}", data["Dataset ID"]);
  newBody.replaceText("{“Dataset contact”}", data["Dataset contact(s)"]);
  newBody.replaceText("{“Background”}", data["Background"]);
  newBody.replaceText("{“PI Name”}", data["PI Name"]);
  newBody.replaceText("{“PI Institution”}", data["PI Institution"]);
  newBody.replaceText("{“PI email address”}", data["PI email address"]);
  newBody.replaceText("{“Dates of Data Collection”}", data["Dates of Data Collection"]);
  newBody.replaceText("{“Tumor-Normal GIAB ID”}", data["Tumor-Normal GIAB ID(s)"]);
  newBody.replaceText("{“Tumor-Normal sample type”}", data["Tumor-Normal sample type"]);
  newBody.replaceText("{“Internal sample ID(s)”}", data["Internal sample ID(s)"]);
  newBody.replaceText("{“Data sample were received”}", data["Date sample(s) were received"]);
  newBody.replaceText("{“Other sample information”}", data["Other sample information"]);
  newBody.replaceText("{“Recommend citations for the data”}", data["Recommend citations for the data"]);
  newBody.replaceText("{“File types”}", data["File types"]);
  newBody.replaceText("{“File name convention”}", data["File name convention"]);
  newBody.replaceText("{“Input into gDNA Isolation”}", data["Input into gDNA Isolation"]);
  newBody.replaceText("{“gDNA Isolation Method”}", data["gDNA Isolation Method"]);
  newBody.replaceText("{“DNA Isolation Kit Information”}", data["DNA Isolation Kit Information"]);
  newBody.replaceText("{“Isolated gDNA Yield”}", data["Isolated DNA Yield"]);
  newBody.replaceText("{“Isolated gDNA Size Distribution”}", data["Isolated gDNA Size Distribution"]);
  newBody.replaceText("{“Are library prep methods either proprietary or R&D”}", data["Are library prep methods either proprietary or R&D?"]);
  newBody.replaceText("{“Number of libraries”}", data["Number of libraries"]);
  newBody.replaceText("{“gDNA mass into library prep”}", data["gDNA mass into library prep"]);
  newBody.replaceText("{“Library quality assurance”}", data["Library quality assurance"]);
  newBody.replaceText("{“Other library preparation information”}", data["Other library preparation information"]);
  newBody.replaceText("{“Measurement Platform”}", data["Measurement Platform"]);
  newBody.replaceText("{“Measurement platform software”}", data["Measurement platform software"]);
  newBody.replaceText("{“Sequencing method and chemistry”}", data["Sequencing method and chemistry"]);
  newBody.replaceText("{“Sequencing consumables”}", data["Sequencing consumables"]);
  newBody.replaceText("{“How were libraries loaded”}", data["How were libraries loaded?"]);
  newBody.replaceText("{“Basecalling information”}", data["Basecalling information"]);
  newBody.replaceText("{“Other sequencing information”}", data["Other sequencing information"]);
  newBody.replaceText("{“Sequencing validation”}", data["Sequencing validation"]);
  newBody.replaceText("{“Alignment methods”}", data["Alignment methods"]);
  newBody.replaceText("{“Reference genome used for alignment”}", data["Reference genome used for alignment"]);
  newBody.replaceText("{“Coverage”}", data["Coverage"]);
  newBody.replaceText("{“Alignment quality assurance”}", data["Alignment quality assurance"]);
  newBody.replaceText("{“Sample QC performed”}", data["Sample QC performed"]);
  newBody.replaceText("{“Library preparation method”}", data["Library preparation method"]);
  newBody.replaceText("{“Library prep kit information”}", data["Library prep kit information"]);
  newBody.replaceText("{“Institution sample were received from”}", data["Institution sample(s) were received from"]);
  newBody.replaceText("{“Are sequencing methods either proprietary or R&D”}", data["Are sequencing methods either proprietary or R&D?"]);
  newBody.replaceText("{“name”}", data["name"]);
  newBody.replaceText("{“YYYY-MM-DD”}", data["YYYY-MM-DD"]);
  newBody.replaceText("{“method e.g. google form, email, etc”}", data["method e.g. google form, email, etc"]);

  // Replace any remaining placeholders with "Not provided" if they were not filled in
  const placeholders = ["{“Title of Dataset”}", "{“Submitter's name”}", "{“Measurement Institution”}", "{“DatasetID”}", "{“Background”}", "{“PI Name”}", "{“PI Institution”}","{“PI email address”}","{“Dataset contact”}", "{“Dates of Data Collection”}","{“Tumor-Normal GIAB ID”}", "{“Tumor-Normal sample type”}","{“Institution sample were received from”}", "{“Internal sample ID(s)”}","{“Date sample were received”}","{“Other sample information”}","{“Recommend citations for the data”}","{“File types”}","{“File name convention”}","{“Input into gDNA Isolation”}","{“gDNA Isolation Method”}","{“DNA Isolation Kit Information”}","{“Isolated gDNA Yield”}","{“Isolated gDNA Size Distribution”}","{“Are library prep methods either proprietary or R&D”}","{“Number of libraries”}","{“gDNA mass into library prep”}","{“Library quality assurance”}","{“Other library preparation information”}","{“Are sequencing methods either proprietary or R&D”}","{“Measurement Platform”}","{“Measurement platform software”}","{“Sequencing method and chemistry”}","{“Sequencing consumables”}","{“How were libraries loaded?”}","{“Basecalling information”}","{“Other sequencing information”}","{“Sequencing validation”}","{“Alignment methods”}","{“Reference genome used for alignment”}","{“Coverage”}","{“Alignment quality assurance”}","{“Sample QC performed”}","{“Institution sample(s) were received from”}","{“Library preparation method”}","{“Library prep kit information”}",];
  placeholders.forEach(placeholder => {
    const placeholderPattern = new RegExp(placeholder, 'g'); // Regular expression for the placeholder
    newBody.replaceText(placeholderPattern, "Not provided");
  });


  // Save and close the new document
  newDoc.saveAndClose();

  Logger.log(`README created in new document: ${newDoc.getUrl()}`);
}


