// Enhanced product functionality JavaScript

// Function to close the product details modal
function closeModal() {
  document.getElementById("productDetailsModal").style.display = "none";
  // Re-enable scrolling
  document.body.style.overflow = "auto";
}

// Function to close order summary modal if needed
function closeOrderSummaryModal() {
  const modal = document.getElementById("orderSummaryModal");
  if (modal) {
    modal.style.display = "none";
    // Re-enable scrolling
    document.body.style.overflow = "auto";
  }
}

// Function to display messages in the message box
function showMessage(message, isError = false) {
  const messageBox = document.getElementById("messageBox");
  if (!messageBox) return;
  
  messageBox.style.display = "block";
  messageBox.innerHTML = message;
  messageBox.className = isError ? "message-box error" : "message-box success";
  
  // Auto hide after 3 seconds
  setTimeout(() => {
    messageBox.style.display = "none";
  }, 3000);
}

// Function to redirect to the checkout page and store product details in session
function buynow(productId, productName, productPrice) {
  // Prevent event bubbling if this is called from inside a card
  if (event) {
    event.stopPropagation();
  }
  
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
        // Close product details modal if open
        const modal = document.getElementById("productDetailsModal");
        if (modal && modal.style.display === "block") {
          closeModal();
        }
        
        // Redirect to the checkout page
        window.location.href = '/checkout';
      } else {
        console.error('Failed to store product details');
        showMessage('An error occurred while processing your request. Please try again.', true);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage('An error occurred. Please try again later.', true);
    });
}

// Function to view product details
function viewProductDetails(productId) {
  // Prevent duplicate function call if called from a button inside a card
  if (event && event.target.classList.contains('view-details')) {
    event.stopPropagation();
  }
  
  fetch(`/product/${productId}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((product) => {
      // Format price if needed
      const formattedPrice = product.price.toString().includes('₹') ? 
        product.price : 
        `₹ ${product.price}`;
      
      // Use image_path or image_url based on what's available
      const imageSrc = product.image_path || product.image_url;
      const imageUrl = imageSrc.startsWith('/') ? 
        imageSrc : 
        `/static/${imageSrc}`;
      
      const productDetailsContent = `
        <h2>${product.name}</h2>
        <img src="${imageUrl}" alt="${product.name}" />
        <p><strong>Price:</strong> ${formattedPrice}</p>
        <p><strong>Description:</strong> ${product.description || 'No description available'}</p>
        <p><strong>WhatsApp:</strong> 
          <a href="https://wa.me/+919399613606?text=Name:${product.name}%0APrice:${formattedPrice}%0ADetails:${product.description || 'No details available'}" target="_blank">+919399613606</a>
        </p>
      `;
      
      document.getElementById("productDetailsContent").innerHTML = productDetailsContent;
      
      // Update buttons in modal to use current product
      const modal = document.getElementById("productDetailsModal");
      const addToCartBtn = modal.querySelector('.add-to-cart');
      const buyNowBtn = modal.querySelector('.buy-now');
      
      if (addToCartBtn) {
        addToCartBtn.onclick = () => addToCart(productId);
      }
      
      if (buyNowBtn) {
        buyNowBtn.onclick = () => buynow(productId, product.name, product.price);
      }
      
      // Show modal
      modal.style.display = "block";
      
      // Disable scrolling on the body
      document.body.style.overflow = "hidden";
      
      // Store product details for use in buttons
      window.currentProduct = product;
    })
    .catch((error) => {
      console.error("Error fetching product details:", error);
      showMessage("Could not load product details. Please try again later.", true);
    });
}

// Function to add an item to the cart
function addToCart(productId) {
  // Stop event propagation to prevent card click
  if (event) {
    event.stopPropagation();
  }
  
  // Determine the correct endpoint format
  const endpoint = productId.toString().includes('/') ? 
    `/add_to_cart/${productId}` : 
    `/add_to_cart/${productId}`;
  
  fetch(endpoint, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
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
        showMessage(data.message || "Failed to add item to cart.", true); // Show error message
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showMessage("An error occurred. Please try again.", true);
    });
}

// Function to update the cart UI dynamically
function updateCartDisplay(cart) {
  const cartContainer = document.getElementById("cartItems");
  if (!cartContainer) return;
  
  cartContainer.innerHTML = ""; // Clear existing items
  
  let totalAmount = 0;
  
  for (const productId in cart) {
    const item = cart[productId];
    totalAmount += item.price * item.quantity;
    
    const cartItem = document.createElement("div");
    cartItem.classList.add("cart-item");
    cartItem.innerHTML = `
      <p><strong>${item.name}</strong> - ${item.price} x ${item.quantity}</p>
      <button onclick="removeFromCart('${productId}')">Remove</button>
    `;
    cartContainer.appendChild(cartItem);
  }
  
  const totalElem = document.getElementById("cartTotal");
  if (totalElem) {
    totalElem.textContent = `Total: ${totalAmount.toFixed(2)}`;
  }
}

// Function to remove an item from the cart
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
        updateCartCount();
        showMessage("Item removed from cart");
      } else {
        showMessage("Failed to remove item", true);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage("An error occurred", true);
    });
}

// Function to clear the cart
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
        updateCartCount();
        showMessage("Cart cleared successfully");
      } else {
        showMessage("Failed to clear cart", true);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage("An error occurred", true);
    });
}

// Function to update the cart UI with fresh content
function updateCartUI() {
  fetch('/cart')
    .then(response => response.text())
    .then(html => {
      const cartContainer = document.querySelector('.cart-container');
      if (cartContainer) {
        cartContainer.innerHTML =
          new DOMParser().parseFromString(html, 'text/html')
            .querySelector('.cart-container').innerHTML;
      }
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
      const cartCountElem = document.getElementById("cart-count");
      if (cartCountElem) {
        cartCountElem.textContent = `(${data.count})`;
      }
    })
    .catch((error) => console.error("Error:", error));
}

// Function for proceeding to payment (if needed)
function proceedToPayment() {
  // If this is needed in your implementation
  window.location.href = '/checkout';
}

// Close modal when clicking outside
window.onclick = function(event) {
  const productModal = document.getElementById('productDetailsModal');
  const orderModal = document.getElementById('orderSummaryModal');
  
  if (event.target === productModal) {
    closeModal();
  }
  
  if (orderModal && event.target === orderModal) {
    closeOrderSummaryModal();
  }
};

// ESC key to close modals
document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') {
    const productModal = document.getElementById('productDetailsModal');
    if (productModal && productModal.style.display === 'block') {
      closeModal();
    }
    
    const orderModal = document.getElementById('orderSummaryModal');
    if (orderModal && orderModal.style.display === 'block') {
      closeOrderSummaryModal();
    }
  }
});

// Run on page load
document.addEventListener("DOMContentLoaded", function() {
  // Update cart count
  updateCartCount();
  
  // Add event listeners for all "Buy Now" buttons dynamically
  document.querySelectorAll('.buy-now').forEach(button => {
    button.addEventListener('click', (event) => {
      event.stopPropagation(); // Prevent card click
      const productId = event.target.getAttribute('data-product-id');
      const productName = event.target.getAttribute('data-product-name');
      const productPrice = event.target.getAttribute('data-product-price');
      buynow(productId, productName, productPrice);
    });
  });
});