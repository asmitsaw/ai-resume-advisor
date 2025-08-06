// AI Resume Analyzer & Career Advisor - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // File input enhancement
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            const fileLabel = this.nextElementSibling;
            if (fileLabel && fileName) {
                fileLabel.textContent = fileName;
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (elementPosition < windowHeight - 50) {
                element.classList.add('fade-in');
            }
        });
    };
    
    // Run animation check on load and scroll
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
    
    // Resume analysis chart (if exists)
    const skillChartElement = document.getElementById('skillChart');
    if (skillChartElement) {
        const ctx = skillChartElement.getContext('2d');
        const skillLabels = JSON.parse(skillChartElement.dataset.labels || '[]');
        const skillValues = JSON.parse(skillChartElement.dataset.values || '[]');
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: [{
                    label: 'Skill Proficiency',
                    data: skillValues,
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(13, 110, 253, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10
                    }
                }
            }
        });
    }
    
    // Job match comparison chart (if exists)
    const matchChartElement = document.getElementById('matchComparisonChart');
    if (matchChartElement) {
        const ctx = matchChartElement.getContext('2d');
        const jobLabels = JSON.parse(matchChartElement.dataset.labels || '[]');
        const matchValues = JSON.parse(matchChartElement.dataset.values || '[]');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: jobLabels,
                datasets: [{
                    label: 'Match Percentage',
                    data: matchValues,
                    backgroundColor: matchValues.map(value => {
                        if (value >= 80) return 'rgba(40, 167, 69, 0.7)';
                        if (value >= 60) return 'rgba(13, 110, 253, 0.7)';
                        if (value >= 40) return 'rgba(255, 193, 7, 0.7)';
                        return 'rgba(220, 53, 69, 0.7)';
                    }),
                    borderColor: matchValues.map(value => {
                        if (value >= 80) return 'rgb(40, 167, 69)';
                        if (value >= 60) return 'rgb(13, 110, 253)';
                        if (value >= 40) return 'rgb(255, 193, 7)';
                        return 'rgb(220, 53, 69)';
                    }),
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Career path recommendation selection
    const careerPathCards = document.querySelectorAll('.career-path-card');
    careerPathCards.forEach(card => {
        card.addEventListener('click', function() {
            careerPathCards.forEach(c => c.classList.remove('border-primary'));
            this.classList.add('border-primary');
            
            // If there's a form to submit with the selected career path
            const pathId = this.dataset.pathId;
            if (pathId) {
                const hiddenInput = document.getElementById('selectedCareerPath');
                if (hiddenInput) {
                    hiddenInput.value = pathId;
                }
            }
        });
    });
    
    // Job description analyzer
    const analyzeJobButton = document.getElementById('analyzeJobButton');
    const jobDescriptionInput = document.getElementById('id_job_description');
    
    if (analyzeJobButton && jobDescriptionInput) {
        analyzeJobButton.addEventListener('click', function() {
            const jobDescription = jobDescriptionInput.value.trim();
            if (jobDescription.length < 50) {
                alert('Please enter a more detailed job description for better analysis.');
                return;
            }
            
            // Show loading state
            analyzeJobButton.disabled = true;
            analyzeJobButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
            
            // In a real app, this would be an AJAX call to the backend
            // For demo purposes, we'll simulate a delay
            setTimeout(() => {
                analyzeJobButton.disabled = false;
                analyzeJobButton.innerHTML = '<i class="fas fa-search me-2"></i>Analyze Job';
                
                // Submit the form to get real results
                const form = analyzeJobButton.closest('form');
                if (form) {
                    form.submit();
                }
            }, 1500);
        });
    }
    
    // Skill gap visualization
    const skillGapChartElement = document.getElementById('skillGapChart');
    if (skillGapChartElement) {
        const ctx = skillGapChartElement.getContext('2d');
        const skillLabels = JSON.parse(skillGapChartElement.dataset.labels || '[]');
        const userValues = JSON.parse(skillGapChartElement.dataset.userValues || '[]');
        const requiredValues = JSON.parse(skillGapChartElement.dataset.requiredValues || '[]');
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: [
                    {
                        label: 'Your Skills',
                        data: userValues,
                        backgroundColor: 'rgba(13, 110, 253, 0.2)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                        pointBorderColor: '#fff'
                    },
                    {
                        label: 'Required Skills',
                        data: requiredValues,
                        backgroundColor: 'rgba(220, 53, 69, 0.2)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(220, 53, 69, 1)',
                        pointBorderColor: '#fff'
                    }
                ]
            },
            options: {
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10
                    }
                }
            }
        });
    }
});