function doPost(e) {
  try {
    var requestData = JSON.parse(e.postData.contents);
    var action = requestData.action || "generate_text";
    
    // アクションの分岐処理
    if (action === "generate_image") {
      return generateImage(requestData.prompt);
    } else if (action === "generate_text") {
      var apiKey = getSetting("GOOGLE_API_KEY") || "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg";
      return generateText(requestData.prompt, requestData.imageBase64, apiKey);
    } else if (action === "save_profile") {
      return saveProfile(requestData.user_id, requestData.profile);
    } else if (action === "get_profile") {
      return getProfile(requestData.user_id);
    } else if (action === "log_usage") {
      return logUsage(requestData);
    } else if (action === "get_profiles") {
      var masterApiKey = getSetting("GOOGLE_API_KEY") || "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg";
      return getProfiles(requestData.apiKey, masterApiKey);
    } else if (action === "get_logs") {
      var masterApiKey = getSetting("GOOGLE_API_KEY") || "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg";
      return getLogs(requestData.apiKey, masterApiKey);
    } else if (action === "save_settings") {
      return saveSettingsAction(requestData.settings);
    } else if (action === "get_voice_settings") {
      return getVoiceSettingsAction();
    } else {
      throw new Error("Unknown action: " + action);
    }
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      error: err.toString(),
      skipped: true
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// 1. スプレッドシート DB 自動検索・作成ヘルパー関数
function getOrCreateDatabase() {
  var dbName = "PetDailyAI_Database";
  var files = DriveApp.getFilesByName(dbName);
  var ss;
  
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else {
    // 新規スプレッドシート作成
    ss = SpreadsheetApp.create(dbName);
    
    // Profilesシートのセットアップ
    var profilesSheet = ss.getSheets()[0];
    profilesSheet.setName("Profiles");
    profilesSheet.appendRow(["registered_at", "user_id", "profile_json"]);
    
    // Logsシートの新規セットアップ
    var logsSheet = ss.insertSheet("Logs");
    logsSheet.appendRow(["timestamp", "user_id", "pet_name", "pet_type", "story_mode", "genre", "duration_ms", "status", "error_msg"]);
    
    // Settingsシートの新規セットアップ
    var settingsSheet = ss.insertSheet("Settings");
    settingsSheet.appendRow(["key", "value"]);
    settingsSheet.appendRow(["GOOGLE_API_KEY", "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg"]);
  }
  
  // 稼働途中のデータベースに Settings シートが不足している場合の自動追加
  if (!ss.getSheetByName("Settings")) {
    var settingsSheet = ss.insertSheet("Settings");
    settingsSheet.appendRow(["key", "value"]);
    settingsSheet.appendRow(["GOOGLE_API_KEY", "AIzaSyBhD-gFDBY4qg1cv7QE2HmZalBirWRRGNg"]);
  }
  
  return ss;
}

// 設定値の取得ヘルパー
function getSetting(key) {
  try {
    var ss = getOrCreateDatabase();
    var sheet = ss.getSheetByName("Settings");
    if (!sheet) return "";
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === key) {
        return data[i][1];
      }
    }
  } catch (e) {
    // 権限エラーなどのフォールバック
  }
  return "";
}

// 設定値の保存処理
function saveSettingsAction(settings) {
  if (!settings) {
    throw new Error("Missing settings object");
  }
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Settings");
  
  for (var key in settings) {
    var value = settings[key];
    var data = sheet.getDataRange().getValues();
    var foundRow = -1;
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === key) {
        foundRow = i + 1;
        break;
      }
    }
    if (foundRow !== -1) {
      sheet.getRange(foundRow, 2).setValue(value);
    } else {
      sheet.appendRow([key, value]);
    }
  }
  return ContentService.createTextOutput(JSON.stringify({ status: "settings_saved" }))
    .setMimeType(ContentService.MimeType.JSON);
}

// 2. プロフィールの Sheets DB 保存処理
function saveProfile(userId, profile) {
  if (!userId || !profile) {
    throw new Error("Missing user_id or profile data");
  }
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Profiles");
  var data = sheet.getDataRange().getValues();
  
  var now = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy-MM-dd HH:mm:ss");
  var profileJsonStr = JSON.stringify(profile);
  
  var foundRow = -1;
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === userId) {
      foundRow = i + 1;
      break;
    }
  }
  
  if (foundRow !== -1) {
    sheet.getRange(foundRow, 1).setValue(now);
    sheet.getRange(foundRow, 3).setValue(profileJsonStr);
  } else {
    sheet.appendRow([now, userId, profileJsonStr]);
  }
  
  return ContentService.createTextOutput(JSON.stringify({ status: "saved" }))
    .setMimeType(ContentService.MimeType.JSON);
}

// 3. プロフィールの Sheets DB 読み込み処理
function getProfile(userId) {
  if (!userId) {
    throw new Error("Missing user_id");
  }
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Profiles");
  var data = sheet.getDataRange().getValues();
  
  var profileStr = null;
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] === userId) {
      profileStr = data[i][2];
      break;
    }
  }
  
  if (!profileStr) {
    return ContentService.createTextOutput(JSON.stringify({ error: "Profile not found" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(profileStr)
    .setMimeType(ContentService.MimeType.JSON);
}

// 4. 利用ログの Sheets DB 追加処理
function logUsage(requestData) {
  var userId = requestData.user_id || "unknown";
  var petName = requestData.pet_name || "不明";
  var petType = requestData.pet_type || "不明";
  var storyMode = requestData.story_mode || "不明";
  var genre = requestData.genre || "不明";
  var durationMs = requestData.duration_ms || 0;
  var status = requestData.status || "SUCCESS";
  var errorMsg = requestData.error_msg || "";
  
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Logs");
  var now = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy-MM-dd HH:mm:ss");
  
  sheet.appendRow([now, userId, petName, petType, storyMode, genre, durationMs, status, errorMsg]);
  
  return ContentService.createTextOutput(JSON.stringify({ status: "logged" }))
    .setMimeType(ContentService.MimeType.JSON);
}

// 5. 開発者コンソール用：全プロフィール一括取得
function getProfiles(inputApiKey, masterApiKey) {
  if (!inputApiKey || inputApiKey !== masterApiKey) {
    return ContentService.createTextOutput(JSON.stringify({ error: "Unauthorized access" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Profiles");
  var data = sheet.getDataRange().getValues();
  
  var profiles = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    try {
      var profileData = JSON.parse(row[2]);
      profileData.user_id = row[1];
      profileData.registered_at = row[0];
      profiles.push(profileData);
    } catch (e) {
    }
  }
  
  return ContentService.createTextOutput(JSON.stringify(profiles))
    .setMimeType(ContentService.MimeType.JSON);
}

// 6. 開発者コンソール用：全ログ一括取得
function getLogs(inputApiKey, masterApiKey) {
  if (!inputApiKey || inputApiKey !== masterApiKey) {
    return ContentService.createTextOutput(JSON.stringify({ error: "Unauthorized access" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  var ss = getOrCreateDatabase();
  var sheet = ss.getSheetByName("Logs");
  var data = sheet.getDataRange().getValues();
  
  var logs = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    logs.push({
      timestamp: row[0],
      user_id: row[1],
      pet_name: row[2],
      pet_type: row[3],
      story_mode: row[4],
      genre: row[5],
      duration_ms: row[6],
      status: row[7],
      error_msg: row[8]
    });
  }
  
  return ContentService.createTextOutput(JSON.stringify(logs))
    .setMimeType(ContentService.MimeType.JSON);
}

// 7. テキスト・JSON生成処理
function generateText(promptText, imageBase64, apiKey) {
  try {
    var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=" + apiKey;
    
    var contents = [];
    var parts = [];
    
    if (imageBase64 && imageBase64.trim() !== "") {
      parts.push({
        inlineData: {
          mimeType: "image/jpeg",
          data: imageBase64
        }
      });
    }
    
    parts.push({
      text: promptText
    });
    
    contents.push({
      parts: parts
    });
    
    var payload = {
      contents: contents,
      generationConfig: {
        responseMimeType: "application/json"
      }
    };
    
    var options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    var response = UrlFetchApp.fetch(url, options);
    var responseText = response.getContentText();
    
    return ContentService.createTextOutput(responseText)
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      error: err.toString(),
      skipped: true
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// 8. 画像生成処理
function generateImage(promptText) {
  try {
    var enhancedPrompt = promptText + ", warm watercolor illustration, highly detailed, soft lighting, cute pet portrait, cozy and lovely, masterpiece";
    var url = "https://image.pollinations.ai/prompt/" + encodeURIComponent(enhancedPrompt) + "?width=1024&height=1024&nologo=true&private=true&enhance=false";
    
    var response = UrlFetchApp.fetch(url, {
      method: "get",
      muteHttpExceptions: true
    });
    
    var resCode = response.getResponseCode();
    if (resCode !== 200) {
      return ContentService.createTextOutput(JSON.stringify({
        error: "画像生成サーバー混雑 (Status " + resCode + ")",
        skipped: true
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    var blob = response.getBlob();
    var bytes = blob.getBytes();
    var base64Image = Utilities.base64Encode(bytes);
    
    return ContentService.createTextOutput(JSON.stringify({
      imageBase64: base64Image
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      error: err.toString(),
      skipped: true
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var redirectUrl = "https://possessive-brother.surge.sh/open.html";
  var html = '<!DOCTYPE html><html><head>' +
             '<meta http-equiv="refresh" content="0;URL=\'' + redirectUrl + '\'">' +
             '<script type="text/javascript">window.top.location.href = "' + redirectUrl + '";</script>' +
             '</head><body><p style="font-family:sans-serif; text-align:center; margin-top:50px;">アプリ起動ゲートへ転送中...🐾</p></body></html>';
  
  var evaluatedHtml = HtmlService.createHtmlOutput(html);
  evaluatedHtml.setTitle("うちのコ日常アルバム 起動ゲート🐾");
  evaluatedHtml.setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  evaluatedHtml.addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
  return evaluatedHtml;
}

// 9. VOICEVOXの接続設定取得処理
function getVoiceSettingsAction() {
  return ContentService.createTextOutput(JSON.stringify({
    voicevox_api_url: getSetting("VOICEVOX_API_URL"),
    voicevox_api_key: getSetting("VOICEVOX_API_KEY")
  })).setMimeType(ContentService.MimeType.JSON);
}
