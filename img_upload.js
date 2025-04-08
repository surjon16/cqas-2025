const formData = new FormData();
formData.append('receipt', fileInput.files[0]);

fetch('/payments/{payment_id}/upload_receipt', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Success:', data);
})
.catch(error => {
    console.error('Error:', error);
});
