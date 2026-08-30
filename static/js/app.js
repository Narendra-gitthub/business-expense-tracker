// App Frontend Management & Utilities

// Toast Notification Manager
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `p-4 rounded-2xl shadow-xl border text-xs font-bold flex items-center gap-3 transition-all duration-300 transform translate-y-2 pointer-events-auto ${
        type === 'success' ? 'bg-emerald-600 text-white border-emerald-500' :
        type === 'error' ? 'bg-rose-600 text-white border-rose-500' :
        'bg-slate-900 text-white border-slate-800'
    }`;

    const icon = type === 'success' ? 'fa-circle-check' :
                 type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info';

    toast.innerHTML = `
        <i class="fa-solid ${icon} text-base"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => toast.classList.remove('translate-y-2'), 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Modal Management
function openAddExpenseModal() {
    const modal = document.getElementById('addExpenseModal');
    if (!modal) return;
    
    const dateInput = document.getElementById('add_date');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    modal.classList.remove('hidden');
}

function closeAddExpenseModal() {
    const modal = document.getElementById('addExpenseModal');
    if (modal) modal.classList.add('hidden');
}

function openEditModalFromData(id, date, category, description, amount, paymentMethod, status) {
    document.getElementById('edit_id').value = id;
    document.getElementById('edit_id_display').value = '#' + id;
    document.getElementById('edit_date').value = date;
    document.getElementById('edit_category').value = category;
    document.getElementById('edit_description').value = description;
    document.getElementById('edit_amount').value = amount;
    document.getElementById('edit_payment_method').value = paymentMethod;
    document.getElementById('edit_status').value = status;

    const modal = document.getElementById('editExpenseModal');
    if (modal) modal.classList.remove('hidden');
}

function closeEditExpenseModal() {
    const modal = document.getElementById('editExpenseModal');
    if (modal) modal.classList.add('hidden');
}

let activeDeleteId = null;

function openDeleteModal(id) {
    activeDeleteId = id;
    const display = document.getElementById('deleteExpenseIdDisplay');
    if (display) display.textContent = '#' + id;
    const modal = document.getElementById('deleteExpenseModal');
    if (modal) modal.classList.remove('hidden');
}

function closeDeleteModal() {
    activeDeleteId = null;
    const modal = document.getElementById('deleteExpenseModal');
    if (modal) modal.classList.add('hidden');
}

function confirmDeleteExpense() {
    if (!activeDeleteId) return;

    fetch(`/api/expenses/${activeDeleteId}`, {
        method: 'DELETE'
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast('Expense deleted successfully', 'success');
            const row = document.getElementById(`row-${activeDeleteId}`);
            if (row) row.remove();
            closeDeleteModal();
            setTimeout(() => window.location.reload(), 400);
        } else {
            showToast(data.message || 'Error deleting expense', 'error');
        }
    })
    .catch(err => {
        showToast('Network error while deleting', 'error');
    });
}

function openImportModal() {
    const modal = document.getElementById('importModal');
    if (modal) modal.classList.remove('hidden');
}

function closeImportModal() {
    const modal = document.getElementById('importModal');
    if (modal) modal.classList.add('hidden');
}

// Add Expense Handler
function handleAddExpenseSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch('/api/expenses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            showToast('Expense added successfully!', 'success');
            closeAddExpenseModal();
            form.reset();
            setTimeout(() => window.location.reload(), 500);
        } else {
            showToast(res.message || 'Failed to add expense', 'error');
        }
    })
    .catch(err => showToast('Error submitting expense', 'error'));
}

// Edit Expense Handler
function handleEditExpenseSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = data.id;

    fetch(`/api/expenses/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            showToast('Expense updated successfully!', 'success');
            closeEditExpenseModal();
            setTimeout(() => window.location.reload(), 500);
        } else {
            showToast(res.message || 'Failed to update expense', 'error');
        }
    })
    .catch(err => showToast('Error updating expense', 'error'));
}

// Quick Status Toggle Dropdown
function toggleStatusDropdown(id) {
    const menu = document.getElementById(`status-menu-${id}`);
    if (!menu) return;
    
    document.querySelectorAll('[id^="status-menu-"]').forEach(el => {
        if (el.id !== `status-menu-${id}`) el.classList.add('hidden');
    });

    menu.classList.toggle('hidden');
}

function quickUpdateStatus(id, newStatus) {
    fetch(`/api/expenses/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(`Status updated to ${newStatus}`, 'success');
            setTimeout(() => window.location.reload(), 400);
        } else {
            showToast(data.message || 'Failed to update status', 'error');
        }
    })
    .catch(err => showToast('Error updating status', 'error'));
}

// Import Handler
function handleImportSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch('/api/import', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            closeImportModal();
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast(data.message || 'Import failed', 'error');
        }
    })
    .catch(err => showToast('Error importing file', 'error'));
}

// Month Selector Redirect
function changeDashboardMonth(m) {
    window.location.href = `/?month=${m}`;
}

// Table Sorting Utility
function sortTable(colIndex) {
    const table = document.getElementById('expensesTable');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAsc = table.getAttribute('data-sort-asc') === 'true';
    table.setAttribute('data-sort-asc', !isAsc);

    rows.sort((a, b) => {
        const cellA = a.children[colIndex].innerText.replace('₹', '').replace(/,/g, '').trim();
        const cellB = b.children[colIndex].innerText.replace('₹', '').replace(/,/g, '').trim();

        const numA = parseFloat(cellA);
        const numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return isAsc ? numA - numB : numB - numA;
        }
        return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });

    rows.forEach(r => tbody.appendChild(r));
}

// Close status dropdowns when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('[id^="status-menu-"]') && !e.target.closest('button[onclick^="toggleStatusDropdown"]')) {
        document.querySelectorAll('[id^="status-menu-"]').forEach(el => el.classList.add('hidden'));
    }
});

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });
    }
});
