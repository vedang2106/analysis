/**
 * Script to start Flask backend server
 * This script activates the virtual environment and starts the Flask API
 * The .env file will be automatically loaded by api.py
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get the project root directory (one level up from frontend)
const projectRoot = path.resolve(__dirname, '..');
const apiPath = path.join(projectRoot, 'api.py');

// Check if we're on Windows
const isWindows = process.platform === 'win32';

// Determine Python path based on OS
let pythonCmd;
if (isWindows) {
  pythonCmd = path.join(projectRoot, '.venv', 'Scripts', 'python.exe');
} else {
  pythonCmd = path.join(projectRoot, '.venv', 'bin', 'python');
}

// Check if venv python exists, fallback to system python
if (!fs.existsSync(pythonCmd)) {
  console.warn(`⚠️  Virtual environment Python not found at ${pythonCmd}`);
  console.warn('⚠️  Falling back to system Python. Make sure python-dotenv is installed.');
  pythonCmd = 'python';
}

console.log('🚀 Starting Flask Backend Server...');
console.log(`📁 Project Root: ${projectRoot}`);
console.log(`🐍 Python: ${pythonCmd}`);
console.log(`📄 API File: ${apiPath}`);
console.log(`🔑 Loading environment variables from .env file...`);

// Start the Flask backend
const backend = spawn(pythonCmd, [apiPath], {
  cwd: projectRoot,
  stdio: 'inherit',
  shell: isWindows
});

backend.on('error', (err) => {
  console.error('❌ Failed to start backend:', err);
  console.error('💡 Tip: Make sure Python and virtual environment are set up correctly.');
  process.exit(1);
});

backend.on('exit', (code) => {
  if (code !== 0) {
    console.error(`❌ Backend exited with code ${code}`);
    process.exit(code);
  }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n🛑 Stopping backend server...');
  backend.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Stopping backend server...');
  backend.kill();
  process.exit(0);
});

