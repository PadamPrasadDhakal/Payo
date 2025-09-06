// Use jobs from Django backend
const jobs = window.djangoJobs || [];
  
  let jobStack = [...jobs];
  let tokens = 10;
  let job_feedback = [];
  
  const jobCardsContainer = document.getElementById("job-cards");
  const jobsCount = document.getElementById("jobs-count");
  
  // Toast notifications
  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `fixed top-10 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded shadow-lg text-white z-50 
      ${type === "success" ? "bg-green-500" : type === "error" ? "bg-red-500" : "bg-blue-500"}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }
  
  // Render job cards
  function renderJobs() {
    jobCardsContainer.innerHTML = "";
    jobStack.slice().reverse().forEach((job, index) => {
      const card = document.createElement("div");
      card.className = `absolute w-full h-[400px] bg-white rounded-2xl shadow-xl p-6 top-0 left-0 cursor-grab transition-transform duration-300`;
      card.style.zIndex = index;

      card.innerHTML = `
        <h3 class="text-xl font-bold mb-1">${job.title || ''}</h3>
        <p class="text-gray-500 mb-1">Organization: ${job.org || ''}</p>
        <p class="text-gray-500 mb-1">Location: ${job.location || ''}</p>
        <p class="text-gray-500 mb-1">Salary: ${job.salary || ''}</p>
        <p class="text-gray-500 mb-1">No. of Positions: ${job.positions || ''}</p>
      `;
  
      // Dragging variables
      let offsetX = 0, offsetY = 0, startX = 0, startY = 0;
  
      // Mouse events for desktop
      card.addEventListener("mousedown", (e) => {
        startX = e.clientX;
        startY = e.clientY;
  
        function onMouseMove(eMove) {
          offsetX = eMove.clientX - startX;
          offsetY = eMove.clientY - startY;
          card.style.transform = `translate(${offsetX}px, ${offsetY}px) rotate(${offsetX * 0.05}deg)`;
        }
  
        function onMouseUp() {
          document.removeEventListener("mousemove", onMouseMove);
          document.removeEventListener("mouseup", onMouseUp);
          handleSwipe(card, offsetX, offsetY, job);
        }
  
        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
      });
  
      // Touch events for mobile
      card.addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      });
  
      card.addEventListener("touchmove", (e) => {
        offsetX = e.touches[0].clientX - startX;
        offsetY = e.touches[0].clientY - startY;
        card.style.transform = `translate(${offsetX}px, ${offsetY}px) rotate(${offsetX * 0.05}deg)`;
      });
  
      card.addEventListener("touchend", () => handleSwipe(card, offsetX, offsetY, job));
  
      jobCardsContainer.appendChild(card);
    });
  
  jobsCount.textContent = `${tokens} token available`;
  }
  
  // Handle swipe action
  function handleSwipe(card, offsetX, offsetY, job) {
    const threshold = 100; // px
    if (offsetX > threshold) {
      card.style.transform = `translate(1000px, ${offsetY}px) rotate(20deg)`;
      showToast(`Applied for ${job.title}`, "success");
      job_feedback.push(1);
      tokens = Math.max(0, tokens - 1);
      // Send user/job data to backend for organization dashboard
      fetch('/users/apply_job/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ job_id: job.id })
      });
      removeTopJob();
    } else if (offsetX < -threshold) {
      card.style.transform = `translate(-1000px, ${offsetY}px) rotate(-20deg)`;
      showToast(`Rejected ${job.title}`, "error");
      job_feedback.push(0);
      removeTopJob();
    } else if (offsetY < -threshold) {
      card.style.transform = `translate(${offsetX}px, -1000px) rotate(0deg)`;
      showToast(`Saved ${job.title}`, "info");
      removeTopJob();
    } else {
      card.style.transform = `translate(0px, 0px) rotate(0deg)`; // reset
    }
  }
  
  // Remove the top job after swipe
  function removeTopJob() {
    jobStack.shift();
    setTimeout(renderJobs, 300);
  }
  
  // Button actions
  document.getElementById("reject-btn").addEventListener("click", () => {
    if (!jobStack.length) return;
    showToast(`Rejected ${jobStack[0].title}`, "error");
    job_feedback.push(0);
    removeTopJob();
  });
  document.getElementById("interested-btn").addEventListener("click", () => {
    if (!jobStack.length) return;
    showToast(`Applied for ${jobStack[0].title}`, "success");
    job_feedback.push(1);
    // Send user/job data to backend for organization dashboard
    fetch('/users/apply_job/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      body: JSON.stringify({ job_id: jobStack[0].id })
    });
    removeTopJob();
  });
// Helper to get CSRF token from cookies
function getCSRFToken() {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, 10) === ('csrftoken=')) {
        cookieValue = decodeURIComponent(cookie.substring(10));
        break;
      }
    }
  }
  return cookieValue;
}
  document.getElementById("save-btn").addEventListener("click", () => {
    if (!jobStack.length) return;
    showToast(`Saved ${jobStack[0].title}`, "info");
    removeTopJob();
  });
  
  // Initialize
  document.addEventListener("DOMContentLoaded", renderJobs);
  