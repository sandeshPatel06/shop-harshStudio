// Function to close the product details modal
function closeModal() {
  document.getElementById("productDetailsModal").style.display = "none";
}

// Function to display messages in the message box
function showMessage(message, isError = false) {
  const messageBox = document.getElementById("messageBox");
  messageBox.style.display = "block";
  messageBox.innerHTML = message;
  messageBox.style.color = isError ? "red" : "green";
}

// Function to redirect to the checkout page and store product details in session
function buynow(productId, productName, productPrice) {
  // Store product details in the session via AJAX (POST request to Flask)
  fetch('/store_product_in_session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      id: productId,
      name: productName,
      price: productPrice
    })
  })
    .then(response => {
      if (response.ok) {
        // Redirect to the checkout page
        window.location.href = '/checkout';
      } else {
        console.error('Failed to store product details');
        alert('An error occurred while processing your request. Please try again.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred. Please try again later.');
    });
}

// Function to view product details
function viewProductDetails(productId) {
  fetch(`/product/${productId}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((product) => {
      const productDetailsContent = `
        <h2>${product.name}</h2>
        <img src="${product.image_url}" alt="${product.name}" />
        <p><strong>Price:</strong> $${product.price}</p>
        <p><strong>Description:</strong> ${product.description}</p>
        <p><strong>WhatsApp:</strong> 
          <a href="https://wa.me/+919399613606?text=Name:${product.name}%0APrice:${product.price}%0ADetails:${product.description}" target="_blank">+919399613606</a>
        </p>
      `;
      document.getElementById("productDetailsContent").innerHTML = productDetailsContent;
      document.getElementById("productDetailsModal").style.display = "block";

      // Store product details for use in the "Buy Now" button
      window.currentProduct = product;
    })
    .catch((error) => {
      console.error("Error fetching product details:", error);
      alert("Could not load product details. Please try again later.");
    });
}

// Function to add an item to the cart
function addToCart(productId) {
  fetch(`/add_to_cart/${productId}`, {
    method: "POST",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        updateCartCount(); // Update cart count dynamically
        showMessage("Item added to cart successfully!"); // Show success message
      } else {
        showMessage("Failed to add item to cart.", true); // Show error message
      }
    })
    .catch((error) => console.error("Error:", error));
}

// Function to update the cart UI dynamically
function updateCartDisplay(cart) {
  const cartContainer = document.getElementById("cartItems");
  cartContainer.innerHTML = ""; // Clear existing items

  let totalAmount = 0;

  for (const productId in cart) {
    const item = cart[productId];
    totalAmount += item.price * item.quantity;

    const cartItem = document.createElement("div");
    cartItem.classList.add("cart-item");
    cartItem.innerHTML = `
      <p><strong>${item.name}</strong> - $${item.price} x ${item.quantity}</p>
      <button onclick="removeFromCart('${productId}')">Remove</button>
    `;
    cartContainer.appendChild(cartItem);
  }

  document.getElementById("cartTotal").textContent = `Total: $${totalAmount.toFixed(2)}`;
}

function removeFromCart(productId) {
  fetch(`/remove_from_cart/${productId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        updateCartUI();
      }
    })
    .catch(error => console.error('Error:', error));
}

function clearCart() {
  fetch('/clear_cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        updateCartUI();
      }
    })
    .catch(error => console.error('Error:', error));
}

function updateCartUI() {
  fetch('/cart')
    .then(response => response.text())
    .then(html => {
      document.querySelector('.cart-container').innerHTML =
        new DOMParser().parseFromString(html, 'text/html')
          .querySelector('.cart-container').innerHTML;
    })
    .catch(error => console.error('Error:', error));
}

// Function to update the cart count dynamically
function updateCartCount() {
  fetch("/cart_count")
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((data) => {
      document.getElementById("cart-count").textContent = `(${data.count})`;
    })
    .catch((error) => console.error("Error:", error));
}

// Run on page load
document.addEventListener("DOMContentLoaded", updateCartCount);

// Add event listeners for all "Buy Now" buttons dynamically
document.querySelectorAll('.buy-now').forEach(button => {
  button.addEventListener('click', (event) => {
    const productId = event.target.getAttribute('data-product-id');
    const productName = event.target.getAttribute('data-product-name');
    const productPrice = event.target.getAttribute('data-product-price');
    buynow(productId, productName, productPrice);
  });
});
