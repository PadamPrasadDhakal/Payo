class JobsDashboard {
  constructor() {
    this.jobs = [];
    this.currentJobIndex = 0;
    this.userTokens = 0;
    this.isLoading = false;
    this.currentTab = 'new-jobs';
    this.savedJobs = [];
    
    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadUserTokens();
    await this.loadJobs();
    await this.loadSavedJobs();
    this.checkTokenNotification();
  }

  setupEventListeners() {
    // Tab switching
    document.getElementById('new-jobs-tab').addEventListener('click', () => this.switchTab('new-jobs'));
    document.getElementById('saved-jobs-tab').addEventListener('click', () => this.switchTab('saved-jobs'));

    // Action buttons
    document.getElementById('reject-btn').addEventListener('click', () => this.rejectJob());
    document.getElementById('save-btn').addEventListener('click', () => this.saveJob());
    document.getElementById('apply-btn').addEventListener('click', () => this.showApplyConfirmation());

    // Modal controls
    document.getElementById('confirm-cancel').addEventListener('click', () => this.hideModal('confirm-modal'));
    document.getElementById('confirm-apply').addEventListener('click', () => this.applyToJob());
    document.getElementById('details-btn').addEventListener('click', () => this.showJobDetails());
    document.getElementById('close-details').addEventListener('click', () => this.hideModal('details-modal'));

    // Refresh button
    document.getElementById('refresh-jobs').addEventListener('click', () => this.refreshJobs());

    // Notification controls
    document.getElementById('view-jobs-btn')?.addEventListener('click', () => {
      this.hideTokenNotification();
      this.switchTab('new-jobs');
    });
    document.getElementById('dismiss-notification')?.addEventListener('click', () => this.hideTokenNotification());

    // Touch/swipe events for job cards
    this.setupSwipeEvents();

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));
  }

  setupSwipeEvents() {
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isDragging = false;

    const jobCardsContainer = document.getElementById('job-cards');

    jobCardsContainer.addEventListener('touchstart', (e) => {
      if (this.jobs.length === 0) return;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      isDragging = true;
    });

    jobCardsContainer.addEventListener('touchmove', (e) => {
      if (!isDragging || this.jobs.length === 0) return;
      e.preventDefault();
      currentX = e.touches[0].clientX;
      currentY = e.touches[0].clientY;

      const deltaX = currentX - startX;
      const deltaY = currentY - startY;

      const card = jobCardsContainer.querySelector('.job-card:last-child');
      if (card) {
        card.style.transform = `translate(${deltaX}px, ${deltaY}px) rotate(${deltaX * 0.1}deg)`;
        card.style.opacity = Math.max(0.3, 1 - Math.abs(deltaX) / 200);
      }
    });

    jobCardsContainer.addEventListener('touchend', (e) => {
      if (!isDragging || this.jobs.length === 0) return;
      isDragging = false;

      const deltaX = currentX - startX;
      const deltaY = currentY - startY;
      const card = jobCardsContainer.querySelector('.job-card:last-child');

      if (card) {
        card.style.transform = '';
        card.style.opacity = '';

        if (Math.abs(deltaX) > 100) {
          if (deltaX > 0) {
            this.showApplyConfirmation();
          } else {
            this.rejectJob();
          }
        } else if (deltaY < -100) {
          this.saveJob();
        }
      }
    });

    // Mouse events for desktop
    jobCardsContainer.addEventListener('mousedown', (e) => {
      if (this.jobs.length === 0) return;
      startX = e.clientX;
      startY = e.clientY;
      isDragging = true;
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging || this.jobs.length === 0) return;
      currentX = e.clientX;
      currentY = e.clientY;

      const deltaX = currentX - startX;
      const deltaY = currentY - startY;

      const card = jobCardsContainer.querySelector('.job-card:last-child');
      if (card) {
        card.style.transform = `translate(${deltaX}px, ${deltaY}px) rotate(${deltaX * 0.1}deg)`;
        card.style.opacity = Math.max(0.3, 1 - Math.abs(deltaX) / 200);
      }
    });

    document.addEventListener('mouseup', (e) => {
      if (!isDragging || this.jobs.length === 0) return;
      isDragging = false;

      const deltaX = currentX - startX;
      const deltaY = currentY - startY;
      const card = jobCardsContainer.querySelector('.job-card:last-child');

      if (card) {
        card.style.transform = '';
        card.style.opacity = '';

        if (Math.abs(deltaX) > 100) {
          if (deltaX > 0) {
            this.showApplyConfirmation();
          } else {
            this.rejectJob();
          }
        } else if (deltaY < -100) {
          this.saveJob();
        }
      }
    });
  }

  handleKeyboard(e) {
    if (this.currentTab !== 'new-jobs' || this.jobs.length === 0) return;

    switch(e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        this.rejectJob();
        break;
      case 'ArrowRight':
        e.preventDefault();
        this.showApplyConfirmation();
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.saveJob();
        break;
      case 'Enter':
        e.preventDefault();
        this.showJobDetails();
        break;
    }
  }

  async loadUserTokens() {
    try {
      const response = await fetch('/api/user/tokens/');
      const data = await response.json();
      this.userTokens = data.tokens_left;
      this.updateTokenDisplay();
    } catch (error) {
      console.error('Error loading user tokens:', error);
      this.showToast('Error loading token information', 'error');
    }
  }

  async loadJobs() {
    if (this.isLoading) return;
    this.isLoading = true;

    try {
      const response = await fetch('/api/jobs/');
      const data = await response.json();
      this.jobs = data.jobs || [];
      this.currentJobIndex = 0;
      this.renderJobCards();
      this.updateJobsCount();
    } catch (error) {
      console.error('Error loading jobs:', error);
      this.showToast('Error loading jobs', 'error');
    } finally {
      this.isLoading = false;
    }
  }

  async loadSavedJobs() {
    try {
      const response = await fetch('/api/user/saved_jobs/');
      const data = await response.json();
      this.savedJobs = data.saved_jobs || [];
      this.renderSavedJobs();
    } catch (error) {
      console.error('Error loading saved jobs:', error);
      this.showToast('Error loading saved jobs', 'error');
    }
  }

  renderJobCards() {
    const container = document.getElementById('job-cards');
    const emptyState = document.getElementById('empty-state');
    const actionButtons = document.getElementById('action-buttons');

    if (this.jobs.length === 0) {
      container.innerHTML = '';
      emptyState.classList.remove('hidden');
      actionButtons.style.opacity = '0.5';
      this.disableActionButtons(true);
      return;
    }

    emptyState.classList.add('hidden');
    actionButtons.style.opacity = '1';
    this.disableActionButtons(false);

    // Show current job and next job (if available)
    container.innerHTML = '';
    
    for (let i = Math.max(0, this.currentJobIndex - 1); i <= Math.min(this.jobs.length - 1, this.currentJobIndex + 1); i++) {
      const job = this.jobs[i];
      const jobCard = this.createJobCard(job, i === this.currentJobIndex);
      
      if (i < this.currentJobIndex) {
        jobCard.classList.add('minimized');
      }
      
      container.appendChild(jobCard);
    }
  }

  createJobCard(job, isCurrent) {
    const card = document.createElement('div');
    card.className = `job-card absolute w-full h-80 bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg border border-gray-200 p-6 cursor-pointer ${isCurrent ? 'z-10' : 'z-0'}`;
    
    card.innerHTML = `
      <div class="h-full flex flex-col">
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-900 mb-2 line-clamp-2">${job.title}</h3>
            <p class="text-gray-600 font-medium">${job.company}</p>
          </div>
          <div class="ml-4 text-right">
            <span class="text-sm text-gray-500">${job.job_type}</span>
            <div class="text-lg font-bold text-blue-600">Rs. ${job.salary}</div>
          </div>
        </div>
        
        <div class="mb-4">
          <div class="flex items-center text-sm text-gray-600 mb-2">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            ${job.location}
          </div>
          <div class="flex items-center text-sm text-gray-600">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Posted ${this.getTimeAgo(job.created_at)}
          </div>
        </div>
        
        <div class="flex-1">
          <p class="text-gray-700 text-sm leading-relaxed line-clamp-6">${job.description}</p>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
          <div class="flex flex-wrap gap-2">
            ${job.skills ? job.skills.split(',').slice(0, 3).map(skill => 
              `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">${skill.trim()}</span>`
            ).join('') : ''}
          </div>
        </div>
      </div>
    `;

    return card;
  }

  renderSavedJobs() {
    const container = document.getElementById('saved-jobs-list');
    const emptyState = document.getElementById('saved-jobs-empty');

    if (this.savedJobs.length === 0) {
      container.innerHTML = '';
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');
    container.innerHTML = this.savedJobs.map(savedJob => {
      const job = savedJob.job;
      return `
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 mb-1">${job.title}</h4>
              <p class="text-sm text-gray-600 mb-2">${job.company}</p>
              <div class="flex items-center text-xs text-gray-500">
                <span>${job.location}</span>
                <span class="mx-2">•</span>
                <span>Rs. ${job.salary}</span>
              </div>
            </div>
            <div class="flex gap-2 ml-4">
              <button onclick="dashboard.applyToSavedJob(${job.id})" class="text-blue-500 hover:text-blue-600 text-sm font-medium">
                Apply
              </button>
              <button onclick="dashboard.removeSavedJob(${savedJob.id})" class="text-red-500 hover:text-red-600 text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H8a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  switchTab(tab) {
    this.currentTab = tab;
    
    const newJobsTab = document.getElementById('new-jobs-tab');
    const savedJobsTab = document.getElementById('saved-jobs-tab');
    const newJobsSection = document.getElementById('new-jobs-section');
    const savedJobsSection = document.getElementById('saved-jobs-section');

    if (tab === 'new-jobs') {
      newJobsTab.classList.add('tab-active');
      newJobsTab.classList.remove('tab-inactive');
      savedJobsTab.classList.add('tab-inactive');
      savedJobsTab.classList.remove('tab-active');
      newJobsSection.classList.remove('hidden');
      savedJobsSection.classList.add('hidden');
    } else {
      savedJobsTab.classList.add('tab-active');
      savedJobsTab.classList.remove('tab-inactive');
      newJobsTab.classList.add('tab-inactive');
      newJobsTab.classList.remove('tab-active');
      savedJobsSection.classList.remove('hidden');
      newJobsSection.classList.add('hidden');
    }
  }

  async rejectJob() {
    if (this.jobs.length === 0) return;
    
    this.moveToNextJob();
  }

  async saveJob() {
    if (this.jobs.length === 0) return;
    
    const currentJob = this.jobs[this.currentJobIndex];
    
    try {
      const response = await fetch('/api/user/saved_jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({ job_id: currentJob.id })
      });

      const data = await response.json();
      
      if (data.success) {
        this.showToast('Job saved successfully!', 'success');
        await this.loadSavedJobs();
        this.moveToNextJob();
      } else {
        this.showToast(data.message || 'Error saving job', 'error');
      }
    } catch (error) {
      console.error('Error saving job:', error);
      this.showToast('Error saving job', 'error');
    }
  }

  showApplyConfirmation() {
    if (this.jobs.length === 0) return;
    
    if (this.userTokens <= 0) {
      this.showToast('You have no application tokens left for today', 'error');
      return;
    }
    
    this.showModal('confirm-modal');
  }

  async applyToJob() {
    if (this.jobs.length === 0) return;
    
    const currentJob = this.jobs[this.currentJobIndex];
    
    try {
      const response = await fetch('/api/user/apply/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({ job_id: currentJob.id })
      });

      const data = await response.json();
      
      if (data.success) {
        this.userTokens = data.tokens_left;
        this.updateTokenDisplay();
        this.showToast('Application submitted successfully!', 'success');
        this.hideModal('confirm-modal');
        this.moveToNextJob();
      } else {
        this.showToast(data.message || 'Error applying to job', 'error');
      }
    } catch (error) {
      console.error('Error applying to job:', error);
      this.showToast('Error applying to job', 'error');
    }
  }

  async applyToSavedJob(jobId) {
    if (this.userTokens <= 0) {
      this.showToast('You have no application tokens left for today', 'error');
      return;
    }

    try {
      const response = await fetch('/api/user/apply/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({ job_id: jobId })
      });

      const data = await response.json();
      
      if (data.success) {
        this.userTokens = data.tokens_left;
        this.updateTokenDisplay();
        this.showToast('Application submitted successfully!', 'success');
        // Remove from saved jobs
        const savedJob = this.savedJobs.find(sj => sj.job.id === jobId);
        if (savedJob) {
          await this.removeSavedJob(savedJob.id);
        }
      } else {
        this.showToast(data.message || 'Error applying to job', 'error');
      }
    } catch (error) {
      console.error('Error applying to job:', error);
      this.showToast('Error applying to job', 'error');
    }
  }

  async removeSavedJob(savedJobId) {
    try {
      const response = await fetch(`/api/user/saved_jobs/${savedJobId}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      const data = await response.json();
      
      if (data.success) {
        this.showToast('Job removed from saved list', 'success');
        await this.loadSavedJobs();
      } else {
        this.showToast(data.message || 'Error removing saved job', 'error');
      }
    } catch (error) {
      console.error('Error removing saved job:', error);
      this.showToast('Error removing saved job', 'error');
    }
  }

  showJobDetails() {
    if (this.jobs.length === 0) return;
    
    const currentJob = this.jobs[this.currentJobIndex];
    const detailsContent = document.getElementById('details-content');
    
    detailsContent.innerHTML = `
      <div class="space-y-4">
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Job Title</h4>
          <p class="text-gray-700">${currentJob.title}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Company</h4>
          <p class="text-gray-700">${currentJob.company}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Location</h4>
          <p class="text-gray-700">${currentJob.location}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Salary</h4>
          <p class="text-gray-700">Rs. ${currentJob.salary}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Job Type</h4>
          <p class="text-gray-700">${currentJob.job_type}</p>
        </div>
        ${currentJob.skills ? `
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Required Skills</h4>
          <div class="flex flex-wrap gap-2">
            ${currentJob.skills.split(',').map(skill => 
              `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">${skill.trim()}</span>`
            ).join('')}
          </div>
        </div>
        ` : ''}
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Description</h4>
          <p class="text-gray-700 leading-relaxed">${currentJob.description}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Posted</h4>
          <p class="text-gray-700">${this.getTimeAgo(currentJob.created_at)}</p>
        </div>
      </div>
    `;
    
    this.showModal('details-modal');
  }

  moveToNextJob() {
    this.currentJobIndex++;
    this.renderJobCards();
    this.updateJobsCount();
  }

  updateTokenDisplay() {
    const tokensDisplay = document.getElementById('tokens-display');
    if (tokensDisplay) {
      tokensDisplay.textContent = `${this.userTokens} / 7`;
      tokensDisplay.className = `text-2xl font-bold ${this.userTokens > 0 ? 'text-blue-600' : 'text-red-500'}`;
    }
  }

  updateJobsCount() {
    const jobsCount = document.getElementById('jobs-count');
    const remaining = Math.max(0, this.jobs.length - this.currentJobIndex);
    if (jobsCount) {
      jobsCount.textContent = `${remaining} jobs remaining`;
    }
  }

  disableActionButtons(disabled) {
    const buttons = ['reject-btn', 'save-btn', 'apply-btn'];
    buttons.forEach(id => {
      const button = document.getElementById(id);
      if (button) {
        button.disabled = disabled;
        button.classList.toggle('opacity-50', disabled);
        button.classList.toggle('cursor-not-allowed', disabled);
      }
    });
  }

  async refreshJobs() {
    await this.loadJobs();
    this.showToast('Jobs refreshed', 'success');
  }

  async checkTokenNotification() {
    try {
      const response = await fetch('/api/user/tokens/');
      const data = await response.json();
      
      if (data.tokens_restored) {
        this.showTokenNotification();
        // Acknowledge the notification
        await fetch('/api/user/ack_tokens_restored/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': this.getCSRFToken()
          }
        });
      }
    } catch (error) {
      console.error('Error checking token notification:', error);
    }
  }

  showTokenNotification() {
    const notification = document.getElementById('tokens-notification');
    if (notification) {
      notification.classList.remove('hidden');
      notification.classList.add('animate-slide-down');
      
      // Auto-hide after 12 seconds (increased for better readability)
      setTimeout(() => {
        this.hideTokenNotification();
      }, 12000);
    }
  }

  hideTokenNotification() {
    const notification = document.getElementById('tokens-notification');
    if (notification) {
      notification.style.animation = 'slide-down 0.4s ease-in-out reverse';
      setTimeout(() => {
        notification.classList.add('hidden');
        notification.classList.remove('animate-slide-down');
        notification.style.animation = '';
      }, 400);
    }
  }

  showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
  }

  hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `min-w-80 w-full max-w-md bg-white shadow-xl rounded-xl pointer-events-auto overflow-hidden transform transition-all duration-300 translate-x-full border border-gray-200`;
    
    const iconColor = type === 'success' ? 'text-green-500' : type === 'error' ? 'text-red-500' : 'text-blue-500';
    const borderColor = type === 'success' ? 'border-green-500' : type === 'error' ? 'border-red-500' : 'border-blue-500';
    const bgColor = type === 'success' ? 'bg-green-50' : type === 'error' ? 'bg-red-50' : 'bg-blue-50';
    
    const icon = type === 'success' 
      ? `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`
      : type === 'error'
      ? `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`
      : `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    
    toast.innerHTML = `
      <div class="p-5 ${bgColor} border-l-4 ${borderColor}">
        <div class="flex items-start">
          <div class="flex-shrink-0 ${iconColor}">
            ${icon}
          </div>
          <div class="ml-4 w-0 flex-1">
            <p class="text-base font-semibold text-gray-900 leading-relaxed">${message}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button class="bg-white rounded-lg inline-flex text-gray-400 hover:text-gray-600 p-1 shadow-sm transition-colors" onclick="this.closest('.min-w-80').remove()">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;

    container.appendChild(toast);

    // Animate in with enhanced animation
    setTimeout(() => {
      toast.classList.remove('translate-x-full');
      toast.classList.add('toast-enter-active');
    }, 100);

    // Auto-remove after 6 seconds (increased from 5)
    setTimeout(() => {
      toast.classList.add('toast-exit-active');
      toast.classList.remove('toast-enter-active');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 6000);
  }

  getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'today';
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  }

  getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    return '';
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new JobsDashboard();
});