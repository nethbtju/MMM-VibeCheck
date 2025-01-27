const NodeHelper = require("node_helper");
const { exec } = require("child_process");

module.exports = NodeHelper.create({
  start: function() {
    console.log("MMM-ChatGPT helper started...");
  },

  socketNotificationReceived: function(notification, payload) {
    if (notification === "SEND_MESSAGE") {
      console.log("Message received, sending to Chat.py");
      this.processMessage(payload);
    }
  },

  processMessage: function(message) {
    exec(`python3 ~/MagicMirror/modules/MMM-ChatGPT/Chat.py "${message}"`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
      }
      if (stderr) {
        console.error(`Stderr: ${stderr}`);
      }

      const [errormgs, responseText, audioFilePath] = stdout.split(":::");
      this.sendSocketNotification("CHAT_RESPONSE", {
        text: responseText,
        audioFile: audioFilePath ? audioFilePath.trim() : null,
      });
    });
  },
});