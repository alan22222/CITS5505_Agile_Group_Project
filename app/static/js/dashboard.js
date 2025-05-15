document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    
    // Define the format options for the date
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    // Set the current date in the element with id 'current-date'
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
});