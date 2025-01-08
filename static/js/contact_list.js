document.addEventListener('DOMContentLoaded', function() {
    const contactList = document.getElementById('contact-list');
    const searchInput = document.getElementById('contact-search');

    // Inline editing
    contactList.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-contact')) {
            const row = e.target.closest('tr');
            const cells = row.querySelectorAll('.editable');
            cells.forEach(cell => {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = cell.textContent;
                input.dataset.originalValue = cell.textContent;
                cell.textContent = '';
                cell.appendChild(input);
            });
            e.target.textContent = 'Save';
            e.target.classList.remove('edit-contact');
            e.target.classList.add('save-contact');
        } else if (e.target.classList.contains('save-contact')) {
            const row = e.target.closest('tr');
            const cells = row.querySelectorAll('.editable');
            const data = {};
            cells.forEach(cell => {
                const input = cell.querySelector('input');
                data[cell.dataset.field] = input.value;
                cell.textContent = input.value;
            });
            updateContact(row.dataset.id, data);
            e.target.textContent = 'Edit';
            e.target.classList.remove('save-contact');
            e.target.classList.add('edit-contact');
        } else if (e.target.classList.contains('delete-contact')) {
            const row = e.target.closest('tr');
            if (confirm('Are you sure you want to delete this contact?')) {
                deleteContact(row.dataset.id);
            }
        }
    });

    // Real-time search
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = contactList.querySelectorAll('tr');
        rows.forEach(row => {
            const email = row.querySelector('td[data-field="email"]').textContent.toLowerCase();
            const name = row.querySelector('td[data-field="name"]').textContent.toLowerCase();
            if (email.includes(searchTerm) || name.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

    function updateContact(id, data) {
        fetch(`/campaigns/contacts/${id}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Contact updated successfully');
            } else {
                console.error('Error updating contact');
            }
        });
    }

    function deleteContact(id) {
        fetch(`/campaigns/contacts/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`tr[data-id="${id}"]`);
                row.remove();
            } else {
                console.error('Error deleting contact');
            }
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});