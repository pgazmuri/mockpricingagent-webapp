document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const term = new Terminal({
        cursorBlink: true,
        fontFamily: '"Courier New", Consolas, Monaco, monospace',
        fontSize: 14,
        fontWeight: 'normal',
        fontWeightBold: 'bold',
        lineHeight: 1.2,
        letterSpacing: 0,
        theme: {
            background: '#1a1a1a',
            foreground: '#ffffff',
            cursor: '#ffffff',
            cursorAccent: '#000000',
            selection: '#ffffff40'
        },
        cols: 80,
        rows: 24
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    
    term.open(document.getElementById('terminal'));
    fitAddon.fit();
    
    // Handle terminal output
    socket.on('terminal_output', function(data) {
        term.write(data.data);
    });
    
    // Handle terminal ready
    socket.on('terminal_ready', function(data) {
        term.focus();
    });
    
    // Handle terminal errors
    socket.on('terminal_error', function(data) {
        term.write('\r\n\x1b[31mError: ' + data.error + '\x1b[0m\r\n');
    });
      // Send input to server
    term.onData(function(data) {
        // Echo the input locally for immediate feedback
        if (data === '\r') {
            // Handle Enter key
            term.write('\r\n');
        } else if (data === '\u007f') {
            // Handle Backspace
            term.write('\b \b');
        } else if (data >= ' ' || data === '\t') {
            // Handle printable characters and tab
            term.write(data);
        }
        
        // Send to server
        socket.emit('terminal_input', {input: data});
    });
    
    // Handle resize
    window.addEventListener('resize', function() {
        fitAddon.fit();
        socket.emit('resize', {
            cols: term.cols,
            rows: term.rows
        });
    });
    
    // Start terminal session
    socket.emit('start_terminal');
    
    // Handle connection status
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('disconnect', function() {
        term.write('\r\n\x1b[31mConnection lost\x1b[0m\r\n');
    });
});
