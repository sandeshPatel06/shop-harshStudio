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
function buyNow(productId, productName, productPrice) {
  document.getElementById("orderSummaryContent").innerHTML = `
        <h3>Order Summary</h3>
        <p><strong>Product:</strong> ${productName}</p>
        <p><strong>Price:</strong> $${productPrice}</p>
        <p><strong>Quantity:</strong> <input type="number" id="quantity" value="1" min="1" /></p>
        <p><strong>Total:</strong> $<span id="totalPrice">${productPrice}</span></p>
        <h4>Shipping Address</h4>
        <form id="paymentForm" action="/pay" method="POST">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required />
            <label for="address">Address:</label>
            <input type="text" id="address" name="address" required />
            <label for="city">City:</label>
            <input type="text" id="city" name="city" required />
            <label for="state">State:</label>
            <input type="text" id="state" name="state" required />
            <label for="postalCode">Postal Code:</label>
            <input type="text" id="postalCode" name="postalCode" required />
            <input type="hidden" name="amount" id="amount" value="${productPrice}" />
            <input type="hidden" name="productId" value="${productId}" />
            <input type="hidden" name="productName" value="${productName}" />
            <input type="hidden" name="quantity" id="quantityInput" value="1" />
            <button type="submit">Proceed to Payment</button>
        </form>
    `;
  document.getElementById("orderSummaryModal").style.display = "block";

  // Update total price and amount on quantity change
  document.getElementById("quantity").addEventListener("input", function () {
    const quantity = parseInt(this.value) || 1;
    const total = (quantity * productPrice).toFixed(2);
    document.getElementById("totalPrice").innerText = total;
    document.getElementById("amount").value = total;
    document.getElementById("quantityInput").value = quantity;
  });
}

// Close the order summary modal
function closeOrderSummaryModal() {
  document.getElementById("orderSummaryModal").style.display = "none";
}

// Function to view product details
function viewProductDetails(productId) {
  fetch(`/product/${productId}`)
    .then((response) => response.json())
    .then((product) => {
      const productDetailsContent = `
        <h2>${product.name}</h2>
        <img src="${product.image_url}" alt="${product.name}" />
        <p><strong>Price:</strong> $${product.price}</p>
        <p><strong>Description:</strong> ${product.description}</p>
        <p><strong>WhatsApp:</strong> <a href="https://wa.me/+919399613606?text=Name:${product.name}%0APrice:${product.price}%0ADetails:${product.description}" target="_blank">+919399613606</a></p>
      `;
      document.getElementById("productDetailsContent").innerHTML =
        productDetailsContent;
      document.getElementById("productDetailsModal").style.display = "block";
    })
    .catch((error) => {
      console.error("Error fetching product details:", error);
      alert("Could not load product details. Please try again later.");
    });
}
