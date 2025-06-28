// Bug Tracker Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeTableSorting();
    initializeSearchFilters();
    initializeCommentSystem();
    initializeLoadingStates();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Real-time validation feedback
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

// Validate individual form field
function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Show/hide custom error messages
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv && !isValid) {
        errorDiv.style.display = 'block';
    }
}

// Table sorting functionality
function initializeTableSorting() {
    const tables = document.querySelectorAll('.sortable-table');
    
    tables.forEach(function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
            
            header.addEventListener('click', function() {
                sortTable(table, this.dataset.sort, this);
            });
        });
    });
}

// Sort table by column
function sortTable(table, column, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = !header.classList.contains('sort-asc');
    
    // Remove sort classes from all headers
    table.querySelectorAll('th').forEach(h => {
        h.classList.remove('sort-asc', 'sort-desc');
        const icon = h.querySelector('i');
        if (icon) icon.className = 'fas fa-sort text-muted';
    });
    
    // Add sort class to current header
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    const icon = header.querySelector('i');
    if (icon) {
        icon.className = isAscending ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
    }
    
    // Sort rows
    rows.sort(function(a, b) {
        const aVal = a.querySelector(`[data-${column}]`)?.dataset[column] || 
                    a.cells[header.cellIndex]?.textContent.trim() || '';
        const bVal = b.querySelector(`[data-${column}]`)?.dataset[column] || 
                    b.cells[header.cellIndex]?.textContent.trim() || '';
        
        if (isAscending) {
            return aVal.localeCompare(bVal, undefined, {numeric: true});
        } else {
            return bVal.localeCompare(aVal, undefined, {numeric: true});
        }
    });
    
    // Reorder table rows
    rows.forEach(row => tbody.appendChild(row));
}

// Search and filter functionality
function initializeSearchFilters() {
    const searchInput = document.querySelector('#bug-search');
    const filterSelects = document.querySelectorAll('.filter-select');
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterBugs();
            }, 300);
        });
    }
    
    filterSelects.forEach(function(select) {
        select.addEventListener('change', filterBugs);
    });
}

// Filter bugs based on search and filters
function filterBugs() {
    const searchTerm = document.querySelector('#bug-search')?.value.toLowerCase() || '';
    const statusFilter = document.querySelector('#status-filter')?.value || '';
    const priorityFilter = document.querySelector('#priority-filter')?.value || '';
    
    const rows = document.querySelectorAll('.bug-row');
    let visibleCount = 0;
    
    rows.forEach(function(row) {
        const title = row.querySelector('.bug-title')?.textContent.toLowerCase() || '';
        const description = row.querySelector('.bug-description')?.textContent.toLowerCase() || '';
        const status = row.dataset.status || '';
        const priority = row.dataset.priority || '';
        
        const matchesSearch = !searchTerm || title.includes(searchTerm) || description.includes(searchTerm);
        const matchesStatus = !statusFilter || status === statusFilter;
        const matchesPriority = !priorityFilter || priority === priorityFilter;
        
        const isVisible = matchesSearch && matchesStatus && matchesPriority;
        row.style.display = isVisible ? '' : 'none';
        
        if (isVisible) visibleCount++;
    });
    
    // Update results count
    const resultsCount = document.querySelector('#results-count');
    if (resultsCount) {
        resultsCount.textContent = `${visibleCount} bug${visibleCount !== 1 ? 's' : ''} found`;
    }
}

// Comment system enhancements
function initializeCommentSystem() {
    const commentForm = document.querySelector('#comment-form');
    const commentTextarea = document.querySelector('#comment-textarea');
    
    if (commentTextarea) {
        // Auto-resize textarea
        commentTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Character counter
        const maxLength = commentTextarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'form-text text-end';
            counter.id = 'char-counter';
            commentTextarea.parentNode.appendChild(counter);
            
            function updateCounter() {
                const remaining = maxLength - commentTextarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                counter.className = remaining < 50 ? 'form-text text-end text-warning' : 'form-text text-end';
            }
            
            commentTextarea.addEventListener('input', updateCounter);
            updateCounter();
        }
    }
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';
            }
        });
    }
}

// Loading states for forms and buttons
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.textContent || submitBtn.value;
                submitBtn.disabled = true;
                
                if (submitBtn.tagName === 'BUTTON') {
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                } else {
                    submitBtn.value = 'Processing...';
                }
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    if (submitBtn.tagName === 'BUTTON') {
                        submitBtn.textContent = originalText;
                    } else {
                        submitBtn.value = originalText;
                    }
                }, 10000);
            }
        });
    });
}

// Utility functions
const BugTracker = {
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },
    
    // Confirm action
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    
    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy to clipboard', 'error');
        });
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#bug-search, input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) modal.hide();
        }
    }
});

// Export for global access
window.BugTracker = BugTracker;
