document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
    
});