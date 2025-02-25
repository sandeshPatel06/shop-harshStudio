// Function to handle showing product details modal
function showProductDetails(name, imagePath, description, price, id) {
    var modalContent = `
        <img src="/static/${imagePath}" alt="${name}">
        <h3>${name}</h3>
        <p><strong>Price:</strong> ₹${price}</p>
        <p>${description}</p>
        <p><strong>WhatsApp:</strong> 
            <a href="https://wa.me/+919399613606?text=Name:${encodeURIComponent(name)}%0APrice:${price}%0ADetails:${encodeURIComponent(description)}" target="_blank">
                +919399613606
            </a>
        </p>
    `;
    document.getElementById('productDetailsContent').innerHTML = modalContent;
    document.getElementById('productDetailsModal').style.display = "block";

    // Update Add to Cart button in modal
    let addToCartBtn = document.getElementById("modalAddToCartBtn");
    addToCartBtn.onclick = function () {
        addToCart(id);
    };
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
                updateCartCount(Object.keys(data.cart).length);
            } else {
                showMessage("Error adding product to cart.", true);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showMessage("Something went wrong!", true);
        });
}

// Function to update cart count dynamically
function updateCartCount(count) {
    document.querySelector('.cart-count').innerText = count;
}

// Function to remove an item from the cart
function removeFromCart(productId) {
    fetch(`/remove_from_cart/${productId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.cart) {
                showMessage("Product removed from cart.");
                updateCartCount(Object.keys(data.cart).length);
            } else {
                showMessage("Product not found in cart.", true);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showMessage("Something went wrong!", true);
        });
}

// Function to clear the entire cart
function clearCart() {
    fetch(`/clear_cart`, { method: 'POST' })
        .then(response => response.text())
        .then(() => {
            showMessage("Cart cleared.");
            updateCartCount(0);
        })
        .catch(error => {
            console.error("Error:", error);
            showMessage("Something went wrong!", true);
        });
}

// Function to display messages
function showMessage(message, isError = false) {
    const messageBox = document.getElementById('messageBox');
    messageBox.style.display = 'block';
    messageBox.innerHTML = message;
    messageBox.style.color = isError ? 'red' : 'green';

    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 3000);
}

// Theme toggle functionality
document.getElementById('theme-toggle').addEventListener('click', function () {
    document.body.classList.toggle('dark-theme');
});

// "Buy Now" button functionality
function buyNow(productId, productName, productPrice) {
    document.getElementById('orderSummaryContent').innerHTML = `
        <p><strong>Product:</strong> ${productName}</p>
        <p><strong>Price:</strong> ₹${productPrice}</p>
        <p><strong>Quantity:</strong> 1</p>
        <p><strong>Total:</strong> ₹${productPrice}</p>
    `;
    document.getElementById('orderSummaryModal').style.display = 'block';
}

// Function to close the order summary modal
function closeOrderSummaryModal() {
    document.getElementById('orderSummaryModal').style.display = 'none';
}

// Function to proceed to payment
function proceedToPayment() {
    alert('Proceeding to payment...');
    // Implement payment gateway integration here
}
