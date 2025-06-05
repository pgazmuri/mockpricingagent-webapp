from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import sys
import platform
import queue
import threading
from terminal_backend import PTYProcess

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
        console_path = os.path.join(os.path.dirname(__file__), 'multi_agent', 'multi_agent_app.py')
        argv = [sys.executable, '-u', console_path]
        ptyproc = PTYProcess(argv, cols=80, rows=24)
        sessions[session_id] = {
            'proc': ptyproc,
            'output_queue': queue.Queue(),
            'input_queue': queue.Queue(),  # Add input queue
            'running': True
        }
        threading.Thread(
            target=read_output,
            args=(session_id,),
            daemon=True
        ).start()
        threading.Thread(
            target=send_output,
            args=(session_id,),
            daemon=True
        ).start()
        # Add dedicated input writer thread
        threading.Thread(
            target=write_input,
            args=(session_id,),
            daemon=True
        ).start()
        emit('terminal_ready', {'status': 'ready'})
    except Exception as e:
        emit('terminal_error', {'error': f'Failed to start terminal: {str(e)}'})

def read_output(session_id):
    if session_id not in sessions:
        return
    ptyproc = sessions[session_id]['proc']
    try:
        import io, fcntl, time
        fd = ptyproc.fileno()   # master PTY fd
        
        # Make the file descriptor non-blocking
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        stream = io.TextIOWrapper(os.fdopen(fd, 'rb', 0),
                                  encoding='utf-8',
                                  errors='replace',
                                  newline='',          # keep \n
                                  line_buffering=False,
                                  write_through=True)
        while sessions[session_id]['running'] and ptyproc.alive():
            try:
                # Read smaller chunks to avoid blocking
                text = stream.read(1)      # read one character at a time
                if text:
                    sessions[session_id]['output_queue'].put(text.replace('\n', '\r\n'))
                else:
                    # No data available, sleep briefly before checking again
                    time.sleep(0.001)  # shorter sleep for more responsiveness
            except (BlockingIOError, OSError):
                # No data available right now, that's fine
                time.sleep(0.001)
        sessions[session_id]['running'] = False
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
            # Queue the input instead of writing directly
            sessions[session_id]['input_queue'].put(data['input'])
        except Exception as e:
            emit('terminal_error', {'error': f'Failed to queue input: {str(e)}'})

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    cleanup_session(session_id)

def cleanup_session(session_id):
    if session_id in sessions:
        try:
            sessions[session_id]['running'] = False
            ptyproc = sessions[session_id]['proc']
            if ptyproc.alive():
                ptyproc.terminate()
        except Exception as e:
            print(f"Error cleaning up session {session_id}: {e}")
        finally:
            if session_id in sessions:
                del sessions[session_id]

def write_input(session_id):
    """Dedicated thread to handle input writing to PTY"""
    if session_id not in sessions:
        return
    
    ptyproc = sessions[session_id]['proc']
    
    while session_id in sessions and sessions[session_id]['running']:
        try:
            # Get input from queue with timeout
            try:
                input_data = sessions[session_id]['input_queue'].get(timeout=0.1)
                ptyproc.write(input_data.encode())
            except queue.Empty:
                continue
        except Exception as e:
            print(f"Error writing input for session {session_id}: {e}")
            break

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)