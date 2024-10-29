// Google app script to convert the sheets to Docs for creating automated README from Google forms provided by the Collaborators

function extractSpecificColumnsToGoogleDoc() {
  // Prompt the user for the row number to extract
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Enter the row number to extract (excluding the header):');
  
  if (response.getSelectedButton() == ui.Button.OK) {
    var rowNumber = parseInt(response.getResponseText());  // Get the row number from user input
    
    if (isNaN(rowNumber) || rowNumber < 2) {
      ui.alert('Invalid row number. Please enter a number greater than 1.');
      return;
    }

    // Get the active sheet and the specific row
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var range = sheet.getRange(rowNumber, 1, 1, sheet.getLastColumn());  // Get the entire row data
    var row = range.getValues()[0];  // Extract the row data as an array
    
    // Column headers you want to extract (manually defined) -- can remove or add more here
    var headers = [
      { name: "Timestamp", index: 0 },                          // Column A
      { name: "Email", index: 1 },                              // Column B
      { name: "Institution Name", index: 2 },                   // Column C
      { name: "Person Providing Dataset", index: 3 },           // Column D
      { name: "Title of Dataset", index: 4 },                   // Column E
      { name: "Summary", index: 5 },                            // Column F
      { name: "PI Name", index: 6 },                            // Column G
      { name: "Datasets Contact(s)", index: 7 },                // Column H
      { name: "Dates of Analysis", index: 8 },                  // Column I
      { name: "Recommended Citation(s) for the Analysis", index: 9 }, // Column J
      { name: "Any Other Information", index: 10 },             // Column K
      { name: "Samples Used for Analysis", index: 11 },         // Column L
      { name: "Analysis Performed", index: 12 },                // Column M
      { name: "Data Used as Input for Analysis", index: 13 },   // Column N
      { name: "Reference(s) Used for Analysis", index: 14 },    // Column O
      { name: "Analysis Tool(s) and Methods", index: 15 },      // Column P
      { name: "Short Description of Output Files", index: 16 }, // Column Q
      { name: "File List with md5s", index: 17 },               // Column R
      { name: "Other File Information", index: 18 },            // Column S
      { name: "Additional Information about Analysis", index: 19 }, // Column T
      { name: "Email Address", index: 20 },                     // Column U
      { name: "Location of Analysis Dataset", index: 21 }       // Column V
    ];
    
    // Create a new Google Doc
    var doc = DocumentApp.create("Extracted Dataset Row - Row " + rowNumber);
    var body = doc.getBody();

    // Add a title to the document
    body.appendParagraph("Dataset Name" ).setHeading(DocumentApp.ParagraphHeading.TITLE); //Add the dataset name or Title of the README
    
    // Function to handle empty or null values
    function safeGetValue(value) {
      return value != null ? value.toString() : "";
    }
    
    // Loop through the headers and corresponding row data
    headers.forEach(function(header) {
      body.appendParagraph(header.name).setHeading(DocumentApp.ParagraphHeading.HEADING2);
      body.appendParagraph(safeGetValue(row[header.index]));  // Append the corresponding data for each selected column
    });
    
    // Log the URL of the created document
    Logger.log("Document created: " + doc.getUrl());
    ui.alert('Document created successfully: ' + doc.getUrl());
  } else {
    ui.alert('No row selected.');
  }
}
