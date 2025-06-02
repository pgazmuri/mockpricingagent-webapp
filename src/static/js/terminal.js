document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const term = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Cascadia Code, Cascadia Mono, Consolas, Courier New, monospace',
        theme: {
            background: '#1e1e1e',
            foreground: '#ffffff',
            cursor: '#ffffff',
            black: '#1e1e1e',
            red: '#f44747',
            green: '#619955',
            yellow: '#ffaf00',
            blue: '#0a7aca',
            magenta: '#b4009e',
            cyan: '#00b7c3',
            white: '#d4d4d4',
            brightBlack: '#666666',
            brightRed: '#f44747',
            brightGreen: '#b5cea8',
            brightYellow: '#ffef8b',
            brightBlue: '#569cd6',
            brightMagenta: '#d670d6',
            brightCyan: '#9cdcfe',
            brightWhite: '#ffffff'
        },
        allowProposedApi: true,
        unicode11: true,
        letterSpacing: 0,
        lineHeight: 1.2,
        rendererType: 'canvas',  // Use canvas renderer for better Unicode support
        fontWeight: 'normal',
        fontWeightBold: 'bold',
        cols: 80,
        rows: 24
    });
    
    const fitAddon = new FitAddon.FitAddon();
    const unicode11Addon = new window.Unicode11Addon.Unicode11Addon();
    term.loadAddon(fitAddon);
    term.loadAddon(unicode11Addon);
    term.unicode.activeVersion = '11';
    
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
    });      // Send input to server
    term.onData(function(data) {
        // Send to server - PTY will handle echoing
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
