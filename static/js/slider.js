// Global variables
let bluetoothDevice = null;
let bluetoothCharacteristic = null;

// Global function to update slider display
function updateSlider() {
    const slider = document.getElementById('impactSlider');
    if (!slider) return;
    
    const sliderValue = document.getElementById('sliderValue');
    const impactFill = document.getElementById('impactFill');
    const impactDescription = document.getElementById('impactDescription');
    const value = parseInt(slider.value);

    sliderValue.textContent = value;
    impactFill.style.width = value + '%';

    let description = '';
    let color = '';

    if (value < 25) {
        description = 'Warning! Very high environmental impact.';
        color = '#F44336'; // Red
    } else if (value < 50) {
        description = 'Caution! High environmental impact.';
        color = '#FF9800'; // Orange
    } else if (value < 75) {
        description = 'Good. Moderate environmental impact.';
        color = '#FFC107'; // Yellow/Amber
    } else {
        description = 'Excellent! Very low environmental impact.';
        color = '#4CAF50'; // Green
    }
    
    // Override for the initial state
    if (value === 0) {
        description = 'No impact detected. Waiting for data...';
        color = '#cccccc'; // A light grey for the initial state
    }

    impactDescription.textContent = description;
    impactDescription.style.color = color;
}

document.addEventListener('DOMContentLoaded', async () => {
    updateSlider();
    // Attempt to reconnect to a previously permitted device on page load
    await checkAndReconnect();
});

function setSliderValue(value) {
    const slider = document.getElementById('impactSlider');
    console.log('[setSliderValue] Called with value:', value);
    if (slider) {
        slider.value = value;
        updateSlider();
        console.log('[setSliderValue] Slider value set to:', slider.value);
    } else {
        console.warn('[setSliderValue] Slider element not found!');
    }
}

function updateConnectionUI(connected) {
    const prompt = document.getElementById('connectionPrompt');
    const interface = document.getElementById('sliderInterface');
    
    if (connected) {
        prompt.style.display = 'none';
        interface.style.display = 'block';
        const statusBadge = document.querySelector('#connectionStatus .badge');
        if (statusBadge) {
            statusBadge.textContent = 'Connected to ' + (bluetoothDevice.name || 'HM-10');
        }
    } else {
        prompt.style.display = 'flex';
        interface.style.display = 'none';
        bluetoothDevice = null;
        bluetoothCharacteristic = null;
    }
}

async function connectToDevice(device, onFailureCallback) {
    try {
        console.log('Connecting to GATT Server...');
        const server = await device.gatt.connect();
        
        console.log('Getting Service...');
        const service = await server.getPrimaryService(0xFFE0);
        
        console.log('Getting Characteristic...');
        bluetoothCharacteristic = await service.getCharacteristic(0xFFE1);

        console.log('Starting Notifications...');
        await bluetoothCharacteristic.startNotifications();
        
        bluetoothCharacteristic.addEventListener('characteristicvaluechanged', handleBluetoothData);
        device.addEventListener('gattserverdisconnected', handleDisconnection);
        
        bluetoothDevice = device;
        
        console.log('✅ Connection successful!');
        updateConnectionUI(true);
        showNotification('Successfully connected to ' + (bluetoothDevice.name || 'your device'), 'success');
        
    } catch (error) {
        console.error('⚠ Connection attempt failed:', error);
        if (onFailureCallback) {
            onFailureCallback(error);
        } else {
            // Default failure behavior if no callback is provided
            updateConnectionUI(false);
            if (error.name !== 'NotFoundError') {
                showNotification('Connection failed: ' + error.message, 'error');
            }
        }
    }
}

async function checkAndReconnect() {
    if (!navigator.bluetooth || typeof navigator.bluetooth.getDevices !== 'function') {
        console.log('Web Bluetooth or getDevices() not supported.');
        return;
    }

    try {
        console.log('Checking for previously permitted devices...');
        const devices = await navigator.bluetooth.getDevices();
        const hmDevice = devices.find(d => d.name && (d.name.includes('HM') || d.name.includes('HC')));

        if (hmDevice) {
            console.log('Found permitted device:', hmDevice.name);
            showNotification('Found previous device. Attempting to reconnect...', 'info');
            // On page load, failure should be silent and just leave the prompt open.
            await connectToDevice(hmDevice);
        } else {
            console.log('No previously permitted devices found.');
        }
    } catch (error) {
        console.error('Error during automatic reconnection check:', error);
    }
}

async function connectBluetooth() {
    try {
        if (!navigator.bluetooth) throw new Error('Web Bluetooth not supported in this browser.');
        
        console.log('Requesting Bluetooth device...');
        const device = await navigator.bluetooth.requestDevice({
            filters: [{ namePrefix: 'HM' }, { name: 'HM-10' }, { namePrefix: 'HC' }],
            optionalServices: [0xFFE0]
        });

        await connectToDevice(device);
        
    } catch (error) {
       // Errors from requestDevice (like user cancelling) are caught here.
       // Errors from connectToDevice are handled inside that function now.
       console.error('⚠ Bluetooth discovery error:', error.message);
    }
}

function handleBluetoothData(event) {
    try {
        const value = new TextDecoder().decode(event.target.value).trim();
        console.log('[handleBluetoothData] Raw value:', value);
        const match = value.match(/=>\s*(\d+)%/);
        if (match) {
            const percentage = parseInt(match[1]);
            console.log('[handleBluetoothData] Parsed percentage:', percentage);
            if (!isNaN(percentage) && percentage >= 0 && percentage <= 100) {
                setSliderValue(percentage);
            } else {
                console.warn('[handleBluetoothData] Ignored out-of-range value:', percentage);
            }
        } else {
            console.warn('[handleBluetoothData] No match for percentage in value:', value);
        }
    } catch (error) {
        console.error('Error processing Bluetooth data:', error);
    }
}

function handleDisconnection() {
    console.log('Bluetooth device disconnected.');
    showNotification('Bluetooth device has been disconnected.', 'warning');
    updateConnectionUI(false);
}

async function disconnectBluetooth() {
    if (bluetoothDevice && bluetoothDevice.gatt.connected) {
        await bluetoothDevice.gatt.disconnect();
    } else {
        handleDisconnection();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}
