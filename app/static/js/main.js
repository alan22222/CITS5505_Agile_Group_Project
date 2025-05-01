document.getElementById('fileUpload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const alertBox = document.getElementById('alertBox');
    const textInput = document.getElementById('textInput');
    const csvPreview = document.getElementById('csvPreview');
    const previewContainer = document.querySelector('.csv-preview-container');

    // Reset UI
    alertBox.classList.remove('alert-danger', 'alert-warning', 'alert-success');
    alertBox.classList.add('d-none');
    csvPreview.innerHTML = '';
    previewContainer.style.display = 'none';
    textInput.style.display = 'block';
    textInput.value = '';

    // If the file is a valid CSV
    if (file && file.name.endsWith('.csv')) { 
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            if (!content.trim()) {
                // Show empty file error
                alertBox.classList.add('alert-danger');
                alertBox.textContent = 'The file is empty.';
                event.target.value = '';
                alertBox.classList.remove('d-none');
                return;
            }
            
            // Keep original textarea functionality
            const rows = content.split('\n').slice(0, 20);
            textInput.value = rows.join('\n');
            
            // Add table display functionality
            previewContainer.style.display = 'block';
            textInput.style.display = 'none';
            
            // Create all rows as regular data rows (td elements)
            rows.forEach((row) => {
                const tr = document.createElement('tr');
                const cells = row.split(',');
                
                cells.forEach(cell => {
                    const td = document.createElement('td'); // Always use td, not th
                    td.textContent = cell.trim();
                    tr.appendChild(td);
                });
                
                csvPreview.appendChild(tr);
            });
            
            alertBox.classList.add('alert-success');
            alertBox.textContent = 'The file content preview is as below.';
            alertBox.classList.remove('d-none');
        };
        reader.readAsText(file);
    } else if (file) {
        // If not a valid CSV
        alertBox.classList.add('alert-warning');
        alertBox.textContent = 'Please upload a valid CSV file.';
        event.target.value = '';
        alertBox.classList.remove('d-none');
    }
});