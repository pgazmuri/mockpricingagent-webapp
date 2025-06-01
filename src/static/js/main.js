// This file contains JavaScript code for client-side functionality, such as handling user interactions and making API calls.

document.addEventListener('DOMContentLoaded', function() {
    // Example: Handle form submission
    const form = document.getElementById('exampleForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            fetch('/api/submit', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                // Handle success (e.g., update UI)
            })
            .catch((error) => {
                console.error('Error:', error);
                // Handle error (e.g., show error message)
            });
        });
    }

    // Example: Fetch data on page load
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            console.log('Data fetched:', data);
            // Update UI with fetched data
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
});