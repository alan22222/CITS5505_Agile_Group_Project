$(document).ready(function() {
    $('#uploadForm').submit(function(e) {
        e.preventDefault(); // For safety

        const formData = new FormData(this);

        // validate whether user has chose a file
        if (!formData.get('file')) {
            showAlert('danger', '请选择CSV文件');
            return;
        }

        // AJAX request
        $.ajax({
            url: $(this).attr('action'), 
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            beforeSend: function() {
                $('#alertBox').addClass('d-none');
                $('.btn').prop('disabled', true);
            },
            success: function(response) {
                showAlert('success', response.message);
                $('#uploadName').val('');
                $('#fileUpload').val('');
                $('#textInput').val('');
            },
            error: function(xhr, status, error) {
                const err = JSON.parse(xhr.responseText);
                showAlert('danger', err.error || '上传失败');
            },
            complete: function() {
                $('.btn').prop('disabled', false);
            }
        });
    });

    function showAlert(type, message) {
        const alertBox = $('#alertBox');
        alertBox.removeClass('alert-success alert-danger');
        alertBox.addClass('alert-' + type);
        alertBox.text(message);
        alertBox.removeClass('d-none');
    }
});
