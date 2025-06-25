document.addEventListener('DOMContentLoaded', function () {
    const itemsContainer = document.getElementById('items-container');
    const cartItems = document.getElementById('cart-items');
    const emptyCart = document.getElementById('empty-cart');
    const cartSummary = document.getElementById('cart-summary');
    const totalItems = document.getElementById('total-items');
    const totalWeight = document.getElementById('total-weight');
    const continueBtn = document.getElementById('continue-btn');

    let cart = [];

    // --- Physical QR Scanner Support (like cart.html) ---
    // Add a dedicated input for scanner
    let scanInput = document.getElementById('qr-input');
    if (!scanInput) {
        scanInput = document.createElement('input');
        scanInput.type = 'text';
        scanInput.id = 'scan-qr-input';
        scanInput.autocomplete = 'off';
        scanInput.style.position = 'absolute';
        scanInput.style.left = '-9999px';
        document.body.appendChild(scanInput);
    }

    function focusScanInput() {
        scanInput.focus();
    }

    // Ensure scanInput is focused on page load
    focusScanInput();
    document.body.addEventListener('click', focusScanInput);
    window.addEventListener('focus', focusScanInput);

    // Debounce for scanner input
    let scanTimeout = null;
    scanInput.addEventListener('input', (e) => {
        const value = e.target.value.trim();
        if (!value) return;
        if (scanTimeout) clearTimeout(scanTimeout);
        // Detect rapid input (likely from scanner)
        const isRapidInput = value.length > 5;
        if (isRapidInput) {
            scanTimeout = setTimeout(() => {
                if (scanInput.value.trim()) {
                    console.log('Scanned QR code:', scanInput.value.trim());
                    // Find item by QR code
                    const qrCode = scanInput.value.trim();
                    const item = window.CLOTHING_ITEMS.find(item => item.qr_code === qrCode);
                    if (item) {
                        // Add item to cart
                        cart.push(item);
                        renderCart();
                        // Remove from available items
                        const itemIndex = window.CLOTHING_ITEMS.findIndex(i => i.qr_code === qrCode);
                        if (itemIndex !== -1) {
                            window.CLOTHING_ITEMS.splice(itemIndex, 1);
                            renderItems();
                        }
                    }
                    scanInput.value = '';
                    focusScanInput();
                }
            }, 300);
        }
    });

    // Render available items
    function renderItems() {
        itemsContainer.innerHTML = '';
        window.CLOTHING_ITEMS.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'flex items-center justify-between bg-gray-50 rounded-lg p-4 border';
            itemDiv.innerHTML = `
                <div class="flex-1">
                    <h3 class="font-semibold text-black">${item.item_name}</h3>
                    <p class="text-gray-600 text-sm">${item.brand}</p>
                    <p class="text-gray-500 text-xs">${item.category} • ${item.weight_grams}g</p>
                </div>
                <button class="bg-green hover-green text-white px-4 py-2 rounded-lg transition-all duration-200 ml-4" data-qr="${item.qr_code}">
                    Add to Cart
                </button>
            `;
            itemDiv.querySelector('button').addEventListener('click', () => addToCart(item.qr_code));
            itemsContainer.appendChild(itemDiv);
        });
    }

    // Render cart
    function renderCart() {
        if (cart.length === 0) {
            emptyCart.style.display = 'block';
            cartItems.style.display = 'none';
            cartSummary.style.display = 'none';
            return;
        }

        emptyCart.style.display = 'none';
        cartItems.style.display = 'block';
        cartSummary.style.display = 'block';

        cartItems.innerHTML = '';
        cart.forEach((item, index) => {
            const cartItemDiv = document.createElement('div');
            cartItemDiv.className = 'flex items-center justify-between bg-gray-50 rounded-lg p-3 border';
            cartItemDiv.innerHTML = `
                <div class="flex-1">
                    <h4 class="font-medium text-black">${item.item_name}</h4>
                    <p class="text-gray-600 text-sm">${item.brand} • ${item.weight_grams}g</p>
                </div>
                <button class="text-red-500 hover:text-red-700 ml-3" data-index="${index}">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </button>
            `;
            cartItemDiv.querySelector('button').addEventListener('click', () => removeFromCart(index));
            cartItems.appendChild(cartItemDiv);
        });

        updateCartSummary();
    }

    // Update cart summary
    function updateCartSummary() {
        totalItems.textContent = cart.length;
        const totalWeightGrams = cart.reduce((sum, item) => sum + parseInt(item.weight_grams), 0);
        totalWeight.textContent = `${totalWeightGrams}g`;
    }

    // Add item to cart
    function addToCart(qrCode) {
        const itemIndex = window.CLOTHING_ITEMS.findIndex(i => i.qr_code === qrCode);
        if (itemIndex !== -1) {
            const item = window.CLOTHING_ITEMS[itemIndex];
            cart.push(item);
            // Remove from available items
            window.CLOTHING_ITEMS.splice(itemIndex, 1);
            renderItems();
            renderCart();
        }
    }

    // Remove item from cart
    function removeFromCart(index) {
        const removedItem = cart.splice(index, 1)[0];
        if (removedItem) {
            window.CLOTHING_ITEMS.push(removedItem);
            renderItems();
        }
        renderCart();
    }

    // Continue button functionality
    continueBtn.addEventListener('click', function() {
        if (cart.length > 0) {
            const user_id = window.location.pathname.split('/')[2];
            const formData = new FormData();
            formData.append('cart', JSON.stringify(cart));
            
            fetch(`/scan/${user_id}/submit`, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                window.location.href = `/factory/${user_id}`;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });



    // Initialize
    renderItems();
    renderCart();
}); 