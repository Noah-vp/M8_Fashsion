// Initialize window management
function initWindowManagement() {
    let currentComponent = 'selection-popup';
    let sliderValue = 50;

    // Initialize slider value display
    updateSliderValue(sliderValue);

    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            goBack();
        }
    });

    // Add touch/swipe support
    let startX = 0, startY = 0;
    document.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });

    document.addEventListener('touchend', (e) => {
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX < 0) {
                goBack();
            }
        }
    });

    function goBack() {
        if (currentComponent === 'selection-popup') {
            return;
        }
        showComponent('selection-popup');
    }

    function showComponent(componentId) {
        const components = document.querySelectorAll('.component');
        components.forEach(component => {
            component.classList.remove('active');
        });

        const targetComponent = document.getElementById(componentId);
        if (targetComponent) {
            targetComponent.classList.add('active');
            currentComponent = componentId;
            
            setTimeout(() => {
                targetComponent.style.transform = 'translateY(0)';
                targetComponent.style.opacity = '1';
            }, 10);
        }

        window.location.hash = componentId;
    }

    function updateSliderValue(value) {
        sliderValue = parseInt(value);
        const elements = {
            valueDisplay: document.getElementById('slider-value'),
            sliderInput: document.getElementById('manual-slider-input'),
            impactFill: document.getElementById('impact-fill'),
            impactDescription: document.getElementById('impact-description')
        };
        
        if (elements.valueDisplay) {
            elements.valueDisplay.textContent = sliderValue;
        }
        
        if (elements.sliderInput) {
            elements.sliderInput.value = sliderValue;
            elements.sliderInput.style.background = `linear-gradient(to right, var(--green-500) 0%, var(--green-500) ${sliderValue}%, var(--gray-200) ${sliderValue}%, var(--gray-200) 100%)`;
        }

        if (elements.impactFill) {
            elements.impactFill.style.width = sliderValue + '%';
        }

        if (elements.impactDescription) {
            updateImpactDescription(elements.impactDescription, sliderValue);
        }
    }

    // Check URL hash on load
    if (window.location.hash) {
        const componentId = window.location.hash.substring(1);
        if (document.getElementById(componentId)) {
            showComponent(componentId);
        }
    }

    // Expose necessary functions globally
    window.showComponent = showComponent;
    window.updateSliderValue = updateSliderValue;
}

// Handle impact description updates
function updateImpactDescription(element, value) {
    let description, color;

    if (value < 25) {
        description = 'Warning! Very high environmental impact.';
        color = '#ef4444';
    } else if (value < 50) {
        description = 'Caution! High environmental impact.';
        color = '#f97316';
    } else if (value < 75) {
        description = 'Good. Moderate environmental impact.';
        color = '#eab308';
    } else {
        description = 'Excellent! Very low environmental impact.';
        color = '#22c55e';
    }

    element.textContent = description;
    element.style.color = color;
}


document.addEventListener('DOMContentLoaded', initWindowManagement);