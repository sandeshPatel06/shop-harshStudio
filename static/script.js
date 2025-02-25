// Function to handle showing product details modal
function showProductDetails(name, imagePath, description, price, id) {
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

    // Update modal Add to Cart button with the correct product ID
    let addToCartBtn = document.getElementById("modalAddToCartBtn");
    addToCartBtn.setAttribute("onclick", `addToCart(${id})`);
}

// Function to close the modal
function closeModal() {
    document.getElementById('productDetailsModal').style.display = "none";
}

// Function to add an item to the cart
function addToCart(productId) {
    fetch(`/add_to_cart/${productId}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.cart) {
            alert(data.message);
            document.querySelector('.cart-count').innerText = Object.keys(data.cart).length;
        } else {
            alert("Error adding product to cart.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong!");
    });
}

// Function to remove an item from the cart
function removeFromCart(productId) {
    fetch(`/remove_from_cart/${productId}`, { method: 'POST' })
    .then(() => {
        location.reload(); // Refresh the page to update the cart UI
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong!");
    });
}

// Function to display messages in the message box
function showMessage(message, isError = false) {
    const messageBox = document.getElementById('messageBox');
    messageBox.style.display = 'block';
    messageBox.innerHTML = message;
    messageBox.style.color = isError ? 'red' : 'green';
}

// Function to handle showing product details modal
function showProductDetails(name, imagePath, description, price, id) {
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

    // Update modal Add to Cart button with the correct product ID
    let addToCartBtn = document.getElementById("modalAddToCartBtn");
    addToCartBtn.setAttribute("onclick", `addToCart(${id})`);
}

// Function to close the modal
function closeModal() {
    document.getElementById('productDetailsModal').style.display = "none";
}

// Function to add an item to the cart
function addToCart(productId) {
    fetch(`/add_to_cart/${productId}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.cart) {
            showMessage(data.message);
            document.querySelector('.cart-count').innerText = Object.keys(data.cart).length;
        } else {
            showMessage("Error adding product to cart.", true);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        showMessage("Something went wrong!", true);
    });
}

// Function to remove an item from the cart
function removeFromCart(productId) {
    fetch(`/remove_from_cart/${productId}`, { method: 'POST' })
    .then(() => {
        location.reload(); // Refresh the page to update the cart UI
    })
    .catch(error => {
        console.error("Error:", error);
        showMessage("Something went wrong!", true);
    });
}
// JavaScript for theme toggle
        document.getElementById('theme-toggle').addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
        });

        // Functionality for "Buy Now" button
        function buyNow(productId, productName, productPrice) {
            // Display order summary modal with product details
            document.getElementById('orderSummaryContent').innerHTML = `
                <p><strong>Product:</strong> ${productName}</p>
                <p><strong>Price:</strong> $${productPrice}</p>
                <p><strong>Quantity:</strong> 1</p>
                <p><strong>Total:</strong> $${productPrice}</p>
            `;
            document.getElementById('orderSummaryModal').style.display = 'block';
        }

        // Close the order summary modal
        function closeOrderSummaryModal() {
            document.getElementById('orderSummaryModal').style.display = 'none';
        }

        // Proceed to payment function
        function proceedToPayment() {
            alert('Proceeding to payment...');
            // Add your payment logic here
        }