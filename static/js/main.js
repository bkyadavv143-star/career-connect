// CAREER CONNECT — Modern SaaS Frontend Utilities

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Auto-dismiss Django success / info alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // 3. Demo Role Switcher Toggle
    const demoTrigger = document.getElementById('demoWidgetTrigger');
    const demoPanel = document.getElementById('demoWidgetPanel');
    const demoClose = document.getElementById('demoWidgetClose');

    if (demoTrigger && demoPanel) {
        demoTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            demoPanel.classList.toggle('show');
        });

        if (demoClose) {
            demoClose.addEventListener('click', function(e) {
                e.stopPropagation();
                demoPanel.classList.remove('show');
            });
        }

        // Close on clicking outside
        document.addEventListener('click', function(e) {
            if (!demoPanel.contains(e.target) && !demoTrigger.contains(e.target)) {
                demoPanel.classList.remove('show');
            }
        });
    }
});

// Helper function to get CSRF token
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

// Mark Notification Read via AJAX
function markNotificationRead(notifId, targetUrl) {
    fetch(`/notifications/${notifId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => {
        if (targetUrl && targetUrl !== 'None' && targetUrl !== '') {
            window.location.href = targetUrl;
        } else {
            window.location.reload();
        }
    }).catch(err => {
        if (targetUrl && targetUrl !== 'None' && targetUrl !== '') {
            window.location.href = targetUrl;
        }
    });
}

// Copy Job Share Link Helper
function copyJobShareLink(url, element) {
    navigator.clipboard.writeText(url).then(function() {
        const originalText = element.innerHTML;
        element.innerHTML = '<i class="bi bi-check2 text-success me-1"></i>Copied!';
        setTimeout(function() {
            element.innerHTML = originalText;
        }, 2000);
    }).catch(function() {
        alert('Job link copied: ' + url);
    });
}
