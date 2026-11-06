ClassPilot Local Setup Guide
ClassPilot can be run locally on Windows using the included startup file. The course editor and classroom player work without an API key. An API key is required only for the AI assistant functions.
Requirements
Before starting ClassPilot, install:
- Windows 10 or Windows 11
- Node.js version 18 or later
- A modern browser such as Chrome or Microsoft Edge
Start ClassPilot on Windows
1. Download and extract the ClassPilot repository.
2. Open the extracted project folder.
3. Double-click:
start-classpilot.bat
4. The startup script will install the required dependencies and start the local server.
5. ClassPilot should open automatically in the default browser. If it does not, visit:
http://localhost:5173/
Always start ClassPilot with start-classpilot.bat. Opening the HTML file directly may prevent file uploads and AI functions from working correctly.
Configure the API Key
ClassPilot uses ChatAnywhere to access the supported AI models. A single ChatAnywhere API key can be used for DeepSeek, ChatGPT, Claude, and Kimi.
1. Locate the environment file
The first time start-classpilot.bat is run, it automatically creates a .env file in the project folder from .env.example.
If the file is not created automatically, make a copy of .env.example and rename the copy to:
.env
2. Add the API key
Open .env with a text editor and locate:
CHATANYWHERE_API_KEY=
Enter the ChatAnywhere API key after the equals sign:
CHATANYWHERE_API_KEY=your_api_key_here
Do not add quotation marks or spaces around the key.
3. Restart ClassPilot
After saving .env:
1. Close the ClassPilot command window.
2. Double-click start-classpilot.bat again.
3. Open http://localhost:5173/.
4. The AI assistant functions should now be available.
Optional Model Configuration
The model identifiers can also be configured in .env:
CHATANYWHERE_API_KEY=your_api_key_here

CHATANYWHERE_DEEPSEEK_CHAT_MODEL=deepseek-chat
CHATANYWHERE_DEEPSEEK_REASONER_MODEL=deepseek-v3.2-thinking
CHATANYWHERE_OPENAI_MODEL=gpt-5.6-sol
CHATANYWHERE_CLAUDE_MODEL=claude-sonnet-4-6
CHATANYWHERE_KIMI_MODEL=kimi-k2.5
The model identifiers must be supported by the connected ChatAnywhere account.
Protect the API Key
The .env file is excluded from Git and should remain on the local computer. Do not place an API key in:
- .env.example
- Frontend HTML or JavaScript files
- GitHub repositories
- Public deployment files
- Shared review archives
Each teacher, school, or teaching team should configure its own API key in its local .env file.