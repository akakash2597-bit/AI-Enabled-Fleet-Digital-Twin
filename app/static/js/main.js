/**
 * Main application client script.
 * Handles mobile navigation toggle, top loader progress animation,
 * button submission spinners, and global UI listeners.
 */

// Global Top Progress Bar
function showTopLoader() {
    let bar = document.getElementById('topLoaderBar');
    if (!bar) {
        bar = document.createElement('div');
        bar.id = 'topLoaderBar';
        bar.className = 'top-loader-bar';
        document.body.appendChild(bar);
    }
    bar.style.opacity = '1';
    bar.style.width = '30%';
    setTimeout(() => { if (bar) bar.style.width = '75%'; }, 150);
}

function hideTopLoader() {
    const bar = document.getElementById('topLoaderBar');
    if (bar) {
        bar.style.width = '100%';
        setTimeout(() => {
            bar.style.opacity = '0';
            setTimeout(() => { bar.style.width = '0%'; }, 300);
        }, 200);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation drawer toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // Auto-dismiss flash alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 6000);
    }

    // Attach loading state to forms on submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('no-spin')) {
                showTopLoader();
                submitBtn.classList.add('btn-loading');
            }
        });
    });
});
