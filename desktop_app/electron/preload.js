const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  exec: (cmd) => ipcRenderer.invoke('pty:exec', cmd),
  onData: (cb) => {
    ipcRenderer.removeAllListeners('pty:data');
    ipcRenderer.on('pty:data', (event, data) => cb(data));
  },
  send: (input) => ipcRenderer.send('pty:input', input),
  list: (dir) => ipcRenderer.invoke('fs:list', dir)
});