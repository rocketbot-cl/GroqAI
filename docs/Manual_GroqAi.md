



# Groq AI
  
Module to interact with Groq AI models from Rocketbot.  

*Read this in other languages: [English](Manual_GroqAI.md), [Português](Manual_GroqAI.pr.md), [Español](Manual_GroqAI.es.md)*
  
![banner](imgs/Banner_GroqAI.jpg)
## How to install this module
  
To install the module in Rocketbot Studio, it can be done in two ways:
1. Manual: __Download__ the .zip file and unzip it in the modules folder. The folder name must be the same as the module and inside it must have the following files and folders: \__init__.py, package.json, docs, example and libs. If you have the application open, refresh your browser to be able to use the new module.
2. Automatic: When entering Rocketbot Studio on the right margin you will find the **Addons** section, select **Install Mods**, search for the desired module and press install.  

## How to use this module

To use this module, we need to obtain the API key from Groq. Follow these steps:

1. First, create a Groq account or log in at [console.groq.com](https://console.groq.com/keys).

2. Once on the API keys page, click the "Create API Key" button to create a new key.

3. A window will open where you need to:
   - Enter a reference name for the key (maximum 50 characters)
   - Complete the Cloudflare validation

4. Click the "Submit" button to generate the key.

5. The API key will be displayed on screen. Use the "Copy" button to copy it.

**Important**: Make sure to save the key in a secure place, as you won't be able to see it again after closing this window.
## Description of the commands

### Connect to Groq AI
  
Establish connection to Groq AI
|Parameters|Description|example|
| --- | --- | --- |
|API Key|Your Groq AI API key|gsk_abc123...|
|Assign to variable|Variable name to store the connection|GroqAiResult|

### Get Models
  
Retrieve available models from GroqAI
|Parameters|Description|example|
| --- | --- | --- |
|Assign to variable|Variable name to store the list of models|modelsResult|

### Generate Text
  
Generate text using GroqAI
|Parameters|Description|example|
| --- | --- | --- |
|Prompt|Input text to generate text|What is Rocketbot?|
|Model|ID of the model to use|compound-beta-mini|
|Temperature (optional)|Controls the randomness of text generation (0.0 a 2)|0.8|
|Maximum tokens (optional)|Maximum number of tokens to generate|100|
|Stop sequence (optional)|Optional sequence to stop text generation|RPA tool|
|Assign to variable|Variable name to store the generated text|textResult|

### OCR to Image
  
Process an image with GroqAI OCR
|Parameters|Description|example|
| --- | --- | --- |
|Model|Name of the OCR model to use|meta-llama/llama-4-scout-17b-16e-instruct|
|File or URL|Allows uploading a local file or entering a url to an online file|Path or URL of the file|
|Message (optional)|Custom instruction for the model about what to look for or extract from the image|Please describe what you see in this image.|
|Temperature (optional)|Value between 0 and 2. Lower values are more precise, higher values are more creative. Default 0.7|0.7|
|Assign to variable|Variable name to store the OCR result|ocrResult|

### Audio Transcription
  
Transcribe audio files using GroqAI Speech-to-Text
|Parameters|Description|example|
| --- | --- | --- |
|Model|Model ID to use (e.g. whisper-large-v3)|whisper-large-v3|
|File or URL|Audio file path or URL (formats flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm)|Select a file or paste a URL|
|Language (optional)|ISO-639-1 language code (e.g. en, es, pt, pr)|es, en, pt, pr|
|Temperature (optional)|Value between 0 and 1 (default 0)|0.2|
|Assign to variable|Variable name to store the transcription|transcription|
