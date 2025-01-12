// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if using Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Practice functionality
window.startPractice = function(topic) {
    // Use the current path to build the practice URL
    const baseUrl = window.location.pathname.split('/')[0];  // Get the base URL
    window.location.href = `${baseUrl}/practice?topic=${topic}`;
};

// Study materials functionality
window.loadMaterial = function(materialId) {
    // For now, show an alert that this feature is coming soon
    alert('Study material content is being prepared. Check back soon!');
};

// Video functionality
window.loadVideo = function(seriesId) {
    // For now, show an alert that this feature is coming soon
    alert('Video content is being prepared. Check back soon!');
}; 