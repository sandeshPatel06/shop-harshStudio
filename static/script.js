
// Function to handle showing product details modal
function showProductDetails(name, imagePath, description, price) {
    // Set the product details in the modal
    var modalContent = `
        <img src="static/${imagePath}" alt="${name}">
        <h3>${name}</h3>
        <p><strong>Price:</strong> $${price}</p>
        <p>${description}</p>
        <p><strong>WhatsApp:</strong> <a href="https://wa.me/+919399613606?text=Name:${name}%0APrice:${price}%0ADetails:${description}" target="_blank">+919399613606</a></p>
    `;
    document.getElementById('productDetailsContent').innerHTML = modalContent;
    // Show the modal
    document.getElementById('productDetailsModal').style.display = "block";
}

// Function to close the modal
function closeModal() {
    document.getElementById('productDetailsModal').style.display = "none";
}
