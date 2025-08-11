const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let fastapiProcess = null;

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    backgroundColor: '#15181b', // dark background
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Load the React front-end (vite dev server)
  win.loadURL('http://localhost:3000');
}

function startFastAPIServer() {
  // Use Python executable from system env (assume uvicorn installed in venv)
  // Handles both Windows and Unix
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  fastapiProcess = spawn(
    pythonCmd,
    [
      '-m', 'uvicorn',
      'grey_hat_ai.api:app',
      '--host', 'localhost',
      '--port', '8000'
    ],
    {
      stdio: 'inherit',
      shell: true
    }
  );

  fastapiProcess.on('close', (code) => {
    console.log(`FastAPI server exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  startFastAPIServer();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    if (fastapiProcess) fastapiProcess.kill();
    app.quit();
  }
});