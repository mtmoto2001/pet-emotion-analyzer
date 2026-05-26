function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var prompt = data.prompt;
    var imageBase64 = data.imageBase64;
    
    if (!prompt || !imageBase64) {
      return ContentService.createTextOutput(JSON.stringify({ error: "Missing prompt or imageBase64🐾" }))
                           .setMimeType(ContentService.MimeType.JSON);
    }
    
    var apiKey = "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg";
    var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + apiKey;
    
    var payload = {
      "contents": [
        {
          "parts": [
            { "text": prompt },
            {
              "inlineData": {
                "mimeType": "image/jpeg",
                "data": imageBase64
              }
            }
          ]
        }
      ],
      "generationConfig": {
        "responseMimeType": "application/json"
      }
    };
    
    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    };
    
    var response = UrlFetchApp.fetch(url, options);
    var responseText = response.getContentText();
    var responseCode = response.getResponseCode();
    
    if (responseCode !== 200) {
      return ContentService.createTextOutput(JSON.stringify({ error: "Gemini API Error (" + responseCode + "): " + responseText }))
                           .setMimeType(ContentService.MimeType.JSON);
    }
    
    return ContentService.createTextOutput(responseText)
                         .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ error: "Internal Proxy Error: " + error.toString() }))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var html = HtmlService.createHtmlOutputFromFile('open');
  html.setTitle("うちのコ日常アルバム 起動ゲート🐾");
  html.setXFrameOptionsMode(HtmlService.SandboxMode.IFRAME);
  return html;
}
