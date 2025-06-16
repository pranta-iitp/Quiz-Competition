class Registration {
    constructor() {
        this.form = document.getElementById('registration_form');
        this.init();
    }

    init() {
        if (this.form) {
            console.log('Form found, adding event listener');
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        } else {
            console.error('Form with ID "author_register_form" not found!');
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        console.log('Form submitted');
        
        try {
            this.setLoadingState(true);
            const formData = this.collectFormData();
            console.log('Collected form data:', formData);
            const response = await this.sendRegistrationData(formData);
            this.handleResponse(response);
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('An error occurred during registration. Please try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    collectFormData() {
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const userRole = document.getElementById('userRole');
    
    let roleValue = ''; // Declare the variable properly
    
    if (!username || !email || !password || !userRole) { // Check userRole too
        throw new Error('Form elements not found');
    }
    
    if (userRole.value === 'author') {
        roleValue = 'author';
    } else if (userRole.value === 'participant') { // Fix: use 'else if'
        roleValue = 'participant';
    } else {
        roleValue = 'author'; // Default fallback
    }
    
    return {
        username: username.value.trim(),
        email: email.value.trim(),
        password: password.value,
        role: roleValue
    };
}

async sendRegistrationData(formData) {
    console.log('Sending data:', formData);
    
    let response; // Declare response variable outside the if/else blocks
    
    if (formData.role === 'author') {
        response = await fetch('/register_author', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });
    } else {
        console.log('formData.role',formData.role)
        response = await fetch('/register_participant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });
    }

    console.log('Response status:', response.status);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Response data:', data);
    return data;
}

    handleResponse(data) {
        console.log('Handling response:', data);
        if (data && data.success) {
            this.showSuccessModal(data.message || 'Registration successful!');
        } else {
            this.showError(data.message || 'Registration failed');
        }
    }

    showSuccessModal(message) {
        console.log('Showing success modal:', message);
        
        // Update modal body with custom message if needed
        const modalBody = document.querySelector('#successModal .modal-body');
        if (modalBody && message !== 'You have registered successfully!') {
            modalBody.textContent = message;
        }
        
        // Show the modal using Bootstrap's modal API
        const successModal = new bootstrap.Modal(document.getElementById('successModal'));
        successModal.show();
        
        // Hide any error messages
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    showError(message) {
        console.log('Showing error modal:', message);
        
        // Update modal body with custom message if needed
        const modalBody = document.querySelector('#successModal .modal-body');
        const modalTitle = document.querySelector('#successModalLabel');
        if (modalBody && message !== 'You have registered successfully!') {
            modalBody.textContent = message;
            modalTitle.textContent = 'Registration unseccessful!';
        }
        
        // Show the modal using Bootstrap's modal API
        const successModal = new bootstrap.Modal(document.getElementById('successModal'));
        successModal.show();
        
    }

    setLoadingState(isLoading) {
        const submitButton = this.form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = isLoading;
            submitButton.textContent = isLoading ? 'Registering...' : 'Register';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing AuthorRegistration');
    new Registration();
});
