// Chicken Health Detector Demo - Main JavaScript

class ChickenHealthDetector {
    constructor() {
        this.isAnalyzing = false;
        this.analysisResults = this.loadStoredResults();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.loadAnalysisHistory();
    }

    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Upload area click
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.addEventListener('click', () => {
                if (fileInput) fileInput.click();
            });
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.startAnalysis());
        }

        // Navigation
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Delete buttons
        const deleteButtons = document.querySelectorAll('.delete-btn');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteAnalysis(e));
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // Validate file
        if (!this.validateFile(file)) return;

        // Show preview
        this.showImagePreview(file);
        
        // Enable analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('btn-secondary');
            analyzeBtn.classList.add('btn-success');
        }
    }

    validateFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!validTypes.includes(file.type)) {
            this.showAlert('Please select a valid image file (JPG, JPEG, PNG)', 'danger');
            return false;
        }

        if (file.size > maxSize) {
            this.showAlert('File size too large. Please select an image smaller than 5MB.', 'danger');
            return false;
        }

        return true;
    }

    showImagePreview(file) {
        const preview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        
        if (preview && previewImg) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                preview.style.display = 'block';
                preview.classList.add('fade-in-up');
            };
            reader.readAsDataURL(file);
        }
    }

    async startAnalysis() {
        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        const analyzeBtn = document.getElementById('analyzeBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        // Update button state
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
        }

        // Show progress
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        // Simulate analysis process
        const steps = [
            'Uploading image...',
            'Preprocessing image data...',
            'Running AI analysis...',
            'Identifying patterns...',
            'Generating diagnosis...',
            'Preparing recommendations...',
            'Finalizing results...'
        ];

        let currentStep = 0;
        const stepInterval = setInterval(() => {
            if (currentStep < steps.length) {
                if (progressText) progressText.textContent = steps[currentStep];
                const progress = ((currentStep + 1) / steps.length) * 100;
                if (progressBar) progressBar.style.width = progress + '%';
                currentStep++;
            } else {
                clearInterval(stepInterval);
                this.completeAnalysis();
            }
        }, 800);
    }

    completeAnalysis() {
        // Generate random analysis result
        const diseases = ['Healthy', 'Coccidiosis', 'Newcastle Disease', 'Salmonella'];
        const confidences = [94.2, 87.6, 91.3, 79.8, 96.7, 83.1];
        
        const diagnosis = diseases[Math.floor(Math.random() * diseases.length)];
        const confidence = confidences[Math.floor(Math.random() * confidences.length)];
        
        const analysisId = this.generateId();
        const result = {
            id: analysisId,
            date: new Date().toISOString(),
            diagnosis: diagnosis,
            confidence: confidence,
            image: document.getElementById('previewImg')?.src || '',
            recommendations: this.generateRecommendations(diagnosis)
        };

        // Store result
        this.analysisResults.unshift(result);
        this.saveResults();

        // Redirect to results page
        setTimeout(() => {
            window.location.href = `result.html?id=${analysisId}`;
        }, 1000);
    }

    generateRecommendations(diagnosis) {
        const recommendations = {
            'Healthy': [
                'Continue current feeding and housing practices',
                'Maintain regular health monitoring',
                'Ensure clean water supply',
                'Keep good biosecurity measures'
            ],
            'Coccidiosis': [
                'Isolate affected birds immediately',
                'Contact veterinarian for treatment',
                'Provide clean water with electrolytes',
                'Deep clean and disinfect housing',
                'Monitor closely for 1-2 weeks'
            ],
            'Newcastle Disease': [
                'URGENT: Contact veterinarian immediately',
                'Quarantine all birds',
                'Report to local authorities',
                'Implement strict biosecurity',
                'Consider vaccination program'
            ],
            'Salmonella': [
                'Isolate affected birds',
                'Implement strict hygiene protocols',
                'Test water and feed sources',
                'Consult veterinarian for treatment',
                'Monitor flock health daily'
            ]
        };

        return recommendations[diagnosis] || recommendations['Healthy'];
    }

    generateId() {
        return 'analysis_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    loadStoredResults() {
        const stored = localStorage.getItem('chickenAnalysisResults');
        if (stored) {
            return JSON.parse(stored);
        }

        // Default sample data
        return [
            {
                id: 'sample_1',
                date: '2025-06-29T14:30:00Z',
                diagnosis: 'Healthy',
                confidence: 94.2,
                image: 'images/salmo.592.jpg',
                recommendations: ['Continue current practices', 'Maintain monitoring']
            },
            {
                id: 'sample_2',
                date: '2025-06-29T16:45:00Z',
                diagnosis: 'Coccidiosis',
                confidence: 87.6,
                image: 'images/salmo.855.jpg',
                recommendations: ['Isolate birds', 'Contact veterinarian']
            },
            {
                id: 'sample_3',
                date: '2025-06-30T09:15:00Z',
                diagnosis: 'Newcastle Disease',
                confidence: 91.3,
                image: 'images/salmo.969.jpg',
                recommendations: ['URGENT vet contact', 'Quarantine all birds']
            },
            {
                id: 'sample_4',
                date: '2025-06-30T11:22:00Z',
                diagnosis: 'Salmonella',
                confidence: 79.8,
                image: 'images/salmo.997.jpg',
                recommendations: ['Isolate birds', 'Hygiene protocols']
            },
            {
                id: 'sample_5',
                date: '2025-06-30T13:05:00Z',
                diagnosis: 'Healthy',
                confidence: 96.7,
                image: 'images/salmo_FgtaloI.855.jpg',
                recommendations: ['Continue monitoring', 'Good practices']
            }
        ];
    }

    saveResults() {
        localStorage.setItem('chickenAnalysisResults', JSON.stringify(this.analysisResults));
    }

    loadAnalysisHistory() {
        const historyContainer = document.getElementById('historyContainer');
        if (!historyContainer) return;

        const historyHTML = this.analysisResults.map(result => this.createHistoryCard(result)).join('');
        historyContainer.innerHTML = historyHTML;

        // Reattach event listeners for delete buttons
        this.attachDeleteListeners();
    }

    createHistoryCard(result) {
        const date = new Date(result.date);
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const badgeClass = this.getDiagnosisBadgeClass(result.diagnosis);
        const progressBarClass = result.confidence >= 80 ? 'bg-success' : 
                                result.confidence >= 60 ? 'bg-warning' : 'bg-danger';

        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 analysis-card fade-in-up">
                    <div class="card-img-top position-relative" style="height: 200px; overflow: hidden;">
                        <img src="${result.image}" alt="Analysis ${result.id}" 
                             class="analysis-image">
                        <div class="status-badge">
                            <span class="badge ${badgeClass}">${result.diagnosis}</span>
                        </div>
                    </div>
                    
                    <div class="card-body d-flex flex-column">
                        <div class="mb-auto">
                            <h6 class="card-title">
                                Analysis #${result.id.substring(0, 12)}...
                            </h6>
                            
                            <div class="small text-muted mb-2">
                                <i class="fas fa-calendar"></i> ${formattedDate}
                            </div>
                            
                            <div class="mb-2">
                                <strong>Diagnosis:</strong> ${result.diagnosis}
                            </div>
                            
                            <div class="mb-2">
                                <strong>Confidence:</strong> 
                                <span class="badge bg-info">${result.confidence}%</span>
                            </div>
                            
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar ${progressBarClass}" 
                                    role="progressbar" 
                                    style="width: ${result.confidence}%">
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <div class="btn-group w-100" role="group">
                                <a href="result.html?id=${result.id}" class="btn btn-primary btn-sm">
                                    <i class="fas fa-eye"></i> View
                                </a>
                                <button type="button" class="btn btn-danger btn-sm delete-btn" 
                                        data-id="${result.id}">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getDiagnosisBadgeClass(diagnosis) {
        const classes = {
            'Healthy': 'badge-healthy',
            'Coccidiosis': 'badge-coccidiosis',
            'Newcastle Disease': 'badge-newcastle',
            'Salmonella': 'badge-salmonella'
        };
        return classes[diagnosis] || 'bg-secondary';
    }

    attachDeleteListeners() {
        const deleteButtons = document.querySelectorAll('.delete-btn');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteAnalysis(e));
        });
    }

    deleteAnalysis(event) {
        const id = event.target.closest('.delete-btn').dataset.id;
        if (confirm('Are you sure you want to delete this analysis?')) {
            this.analysisResults = this.analysisResults.filter(result => result.id !== id);
            this.saveResults();
            this.loadAnalysisHistory();
            this.showAlert('Analysis deleted successfully', 'success');
        }
    }

    handleNavigation(event) {
        event.preventDefault();
        const href = event.target.getAttribute('href');
        if (href) {
            window.location.href = href;
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        alertContainer.innerHTML = alertHTML;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    // Get analysis result by ID
    getAnalysisById(id) {
        return this.analysisResults.find(result => result.id === id);
    }

    // Get URL parameter
    getUrlParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chickenDetector = new ChickenHealthDetector();
    
    // Add some UI enhancements
    addUIEnhancements();
});

function addUIEnhancements() {
    // Add loading state to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 100);
    });

    // Add pulse animation to important elements
    const importantElements = document.querySelectorAll('.alert-success, .badge-healthy');
    importantElements.forEach(element => {
        element.classList.add('pulse');
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getConfidenceColor(confidence) {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'danger';
}
