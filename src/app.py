from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import subprocess
import threading
import queue
import signal
import sys
import platform
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

socketio = SocketIO(app, cors_allowed_origins="*")

# Store active sessions
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@socketio.on('start_terminal')
def handle_start_terminal():
    session_id = request.sid
    
    try:
        # Create a subprocess for the console app
        console_path = os.path.join(os.path.dirname(__file__), 'console_app.py')
        
        if platform.system() == "Windows":
            # Windows subprocess creation with unbuffered output
            process = subprocess.Popen(
                [sys.executable, '-u', console_path],  # -u for unbuffered
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Unix-like systems
            process = subprocess.Popen(
                [sys.executable, '-u', console_path],  # -u for unbuffered
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True
            )
        
        # Store session info
        sessions[session_id] = {
            'process': process,
            'output_queue': queue.Queue(),
            'running': True
        }
        
        # Start output reader thread
        threading.Thread(
            target=read_output,
            args=(session_id, process.stdout),
            daemon=True
        ).start()
        
        # Start output sender thread
        threading.Thread(
            target=send_output,
            args=(session_id,),
            daemon=True
        ).start()
        
        emit('terminal_ready', {'status': 'ready'})
        
    except Exception as e:
        emit('terminal_error', {'error': f'Failed to start terminal: {str(e)}'})

def read_output(session_id, stdout):
    """Read output from the subprocess and put it in the queue"""
    if session_id not in sessions:
        return
        
    try:
        while sessions[session_id]['running']:
            # Read character by character for better interactivity
            char = stdout.read(1)
            if char:
                # Convert \n to \r\n for proper terminal display
                if char == '\n':
                    sessions[session_id]['output_queue'].put('\r\n')
                else:
                    sessions[session_id]['output_queue'].put(char)
            elif sessions[session_id]['process'].poll() is not None:
                # Process has terminated
                sessions[session_id]['running'] = False
                sessions[session_id]['output_queue'].put('\r\n[Process terminated]\r\n')
                break
    except Exception as e:
        if session_id in sessions:
            sessions[session_id]['output_queue'].put(f'\r\n[Error reading output: {str(e)}]\r\n')
            sessions[session_id]['running'] = False

def send_output(session_id):
    """Send queued output to the client"""
    while session_id in sessions and sessions[session_id]['running']:
        try:
            # Get output from queue with timeout
            try:
                output = sessions[session_id]['output_queue'].get(timeout=0.1)
                socketio.emit('terminal_output', {'data': output}, room=session_id)
            except queue.Empty:
                continue
        except Exception as e:
            break
    
    # Send any remaining output
    while session_id in sessions:
        try:
            output = sessions[session_id]['output_queue'].get_nowait()
            socketio.emit('terminal_output', {'data': output}, room=session_id)
        except queue.Empty:
            break

@socketio.on('terminal_input')
def handle_terminal_input(data):
    session_id = request.sid
    if session_id in sessions and sessions[session_id]['running']:
        try:
            process = sessions[session_id]['process']
            if process.stdin and not process.stdin.closed:
                # Convert \r to \n for proper line endings
                input_data = data['input'].replace('\r', '\n')
                process.stdin.write(input_data)
                process.stdin.flush()
        except Exception as e:
            emit('terminal_error', {'error': f'Failed to send input: {str(e)}'})

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    cleanup_session(session_id)

def cleanup_session(session_id):
    if session_id in sessions:
        try:
            sessions[session_id]['running'] = False
            process = sessions[session_id]['process']
            
            if process.poll() is None:  # Process is still running
                if platform.system() == "Windows":
                    # On Windows, use taskkill to terminate the process tree
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                 capture_output=True)
                else:
                    # On Unix-like systems
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
        except Exception as e:
            print(f"Error cleaning up session {session_id}: {e}")
        finally:
            if session_id in sessions:
                del sessions[session_id]

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)