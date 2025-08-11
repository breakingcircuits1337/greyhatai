const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

// Terminal support
const pty = require('node-pty');

let fastapiProcess = null;
let ptyProcess = null;

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    backgroundColor: '#15181b',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  win.loadURL('http://localhost:3000');
}

// PTY and FS IPC
ipcMain.handle('pty:exec', (event, cmd) => {
  if (ptyProcess) {
    ptyProcess.kill();
    ptyProcess = null;
  }
  ptyProcess = pty.spawn(os.platform() === 'win32' ? 'cmd.exe' : 'bash', [], {
    name: 'xterm-color',
    cols: 80,
    rows: 30,
    cwd: process.cwd(),
    env: process.env
  });
  ptyProcess.write(cmd + '\r');
  ptyProcess.onData(data => {
    event.sender.send('pty:data', data);
  });
  return true;
});
ipcMain.on('pty:input', (event, input) => {
  if (ptyProcess) ptyProcess.write(input);
});
ipcMain.handle('fs:list', async (event, dir) => {
  try {
    const files = await fs.promises.readdir(dir, { withFileTypes: true });
    return files.map(f => ({
      name: f.name,
      isDir: f.isDirectory(),
      isFile: f.isFile(),
      path: path.join(dir, f.name)
    }));
  } catch (e) {
    return [];
  }
});

// Read a file for preview (text or image, small files only)
ipcMain.handle('fs:readFile', async (event, filePath) => {
  try {
    // Guess type by extension for images
    const ext = (filePath.split('.').pop() || '').toLowerCase();
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp'].includes(ext)) {
      const buf = await fs.promises.readFile(filePath);
      const mime = ext === 'svg' ? 'image/svg+xml' : `image/${ext === 'jpg' ? 'jpeg' : ext}`;
      return { dataUrl: `data:${mime};base64,${buf.toString('base64')}` };
    } else {
      const text = await fs.promises.readFile(filePath, 'utf8');
      return { text };
    }
  } catch (e) {
    return { error: e.message };
  }
});

// Open a file or dir in system default app
ipcMain.handle('shell:openPath', async (event, filePath) => {
  try {
    await shell.openPath(filePath);
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
});

function startFastAPIServer() {
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
    if (ptyProcess) ptyProcess.kill();
    app.quit();
  }
});

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