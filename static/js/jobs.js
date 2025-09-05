// Mock job data
const jobs = [
    { id: 1, title: "Senior Backend Developer", company: "TechCorp Nepal", location: "Kathmandu", salary: "NPR 60k–90k" },
    { id: 2, title: "Frontend Developer", company: "Digital Solutions", location: "Lalitpur", salary: "NPR 45k–70k" },
    { id: 3, title: "Full Stack Engineer", company: "StartupHub", location: "Pokhara", salary: "NPR 70k–100k" },
    { id: 4, title: "DevOps Engineer", company: "CloudNepal", location: "Kathmandu", salary: "NPR 80k–120k" },
    { id: 5, title: "Mobile App Developer (Flutter)", company: "AppVenture", location: "Lalitpur", salary: "NPR 50k–75k" },
    { id: 6, title: "Data Scientist", company: "InfoAnalytics", location: "Kathmandu", salary: "NPR 75k–110k" },
    { id: 7, title: "QA Automation Engineer", company: "QualityTech", location: "Bharatpur", salary: "NPR 40k–65k" },
    { id: 8, title: "UX/UI Designer", company: "CreativeMinds", location: "Kathmandu", salary: "NPR 45k–70k" },
    { id: 9, title: "Technical Project Manager", company: "NepalSoft", location: "Lalitpur", salary: "NPR 90k–130k" },
    { id: 10, title: "System Administrator", company: "NetLink Pvt. Ltd.", location: "Pokhara", salary: "NPR 35k–55k" },
    { id: 11, title: "React Native Developer", company: "InnoTech", location: "Kathmandu", salary: "NPR 60k–85k" },
    { id: 12, title: "Junior Software Engineer", company: "TechKarma", location: "Lalitpur", salary: "NPR 30k–45k" },
    { id: 13, title: "Product Manager", company: "NextGen Innovations", location: "Kathmandu", salary: "NPR 95k–140k" },
  ];
  
  let jobStack = [...jobs];
  
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
        <h3 class="text-xl font-bold mb-1">${job.title}</h3>
        <p class="text-gray-500 mb-1">${job.company} • ${job.location}</p>
        <p class="text-gray-500 mb-2">Salary: ${job.salary}</p>
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
  
    jobsCount.textContent = `${jobStack.length} jobs remaining`;
  }
  
  // Handle swipe action
  function handleSwipe(card, offsetX, offsetY, job) {
    const threshold = 100; // px
    if (offsetX > threshold) {
      card.style.transform = `translate(1000px, ${offsetY}px) rotate(20deg)`;
      showToast(`Interested in ${job.title}`, "success");
      removeTopJob();
    } else if (offsetX < -threshold) {
      card.style.transform = `translate(-1000px, ${offsetY}px) rotate(-20deg)`;
      showToast(`Rejected ${job.title}`, "error");
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
    removeTopJob();
  });
  document.getElementById("interested-btn").addEventListener("click", () => {
    if (!jobStack.length) return;
    showToast(`Interested in ${jobStack[0].title}`, "success");
    removeTopJob();
  });
  document.getElementById("save-btn").addEventListener("click", () => {
    if (!jobStack.length) return;
    showToast(`Saved ${jobStack[0].title}`, "info");
    removeTopJob();
  });
  
  // Initialize
  document.addEventListener("DOMContentLoaded", renderJobs);
  