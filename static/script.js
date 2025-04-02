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

// Functionality for "Buy Now" button
// function buyNow(productId, productName, productPrice) {
//   document.getElementById("orderSummaryContent").innerHTML = `
  
//        <div class="order-summary">
//     <h3>Order Summary</h3>
//     <p><strong>Product:</strong> ${productName}</p>
//     <p><strong>Price:</strong> $${productPrice}</p>
//     <p><strong>Quantity:</strong> <input type="number" id="quantity" value="1" min="1" /></p>
//     <p><strong>Total:</strong> $<span id="totalPrice">${productPrice}</span></p>
//     <h4>Shipping Address</h4>
//     <form id="paymentForm" action="https://formspree.io/f/mzzejdgo"
//   method="POST">
//         <label for="name">Name:</label>
//         <input type="text" id="name" name="name" required />
//         <label for="address">Address:</label>
//         <input type="text" id="address" name="address" required />
//         <label for="city">City:</label>
//         <input type="text" id="city" name="city" required />
//         <label for="state">State:</label>
//         <input type="text" id="state" name="state" required />
//         <label for="postalCode">Postal Code:</label>
//         <input type="text" id="postalCode" name="postalCode" required />
//         <input type="hidden" name="amount" id="amount" value="${productPrice}" />
//         <input type="hidden" name="productId" value="${productId}" />
//         <input type="hidden" name="productName" value="${productName}" />
//         <input type="hidden" name="quantity" id="quantityInput" value="1" />
//         <button type="submit">Proceed to Payment</button>
//     </form>
// </div>

    // `;
//   document.getElementById("orderSummaryModal").style.display = "block";

//   // Update total price and amount on quantity change
//   document.getElementById("quantity").addEventListener("input", function () {
//     const quantity = parseInt(this.value) || 1;
//     const total = (quantity * productPrice).toFixed(2);
//     document.getElementById("totalPrice").innerText = total;
//     document.getElementById("amount").value = total;
//     document.getElementById("quantityInput").value = quantity;
//   });
// }


// Function to redirect to the checkout page and store product details in session
function redirectToCheckout(productId, productName, productPrice) {
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
      }
  });
}

// Close the order summary modal
function closeOrderSummaryModal() {
  document.getElementById("orderSummaryModal").style.display = "none";
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
        <p><strong>WhatsApp:</strong> <a href="https://wa.me/+919399613606?text=Name:${product.name}%0APrice:${product.price}%0ADetails:${product.description}" target="_blank">+919399613606</a></p>
      `;
      document.getElementById("productDetailsContent").innerHTML = productDetailsContent;
      document.getElementById("productDetailsModal").style.display = "block";
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

//// Function to update the cart UI dynamically
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