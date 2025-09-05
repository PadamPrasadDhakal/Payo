
<script>
const jobs = [
    { id: 1, title: "Senior Backend Developer", company: "TechCorp Nepal", location: "Kathmandu, Nepal", salary: "NPR 60k–90k", skills: ["Python", "Django", "REST"], match: "95%" },
    { id: 2, title: "Frontend Developer", company: "Digital Solutions", location: "Lalitpur, Nepal", salary: "NPR 45k–70k", skills: ["React", "Tailwind", "UI/UX"], match: "90%" },
];

let jobStack = [...jobs];
const jobCardsContainer = document.getElementById("job-cards");

function renderJobs() {
    jobCardsContainer.innerHTML = "";
    jobStack.slice().reverse().forEach((job, index) => {
        const card = document.createElement("div");
        card.className = "absolute w-full bg-white rounded-2xl shadow-xl p-6 top-0 left-0 cursor-grab transition-transform duration-300";
        card.style.zIndex = index;

        const skillsHTML = job.skills.map(skill => `<span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">${skill}</span>`).join(" ");

        card.innerHTML = `
            <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-gray-500">${job.company}</span>
                <span class="bg-green-100 text-green-700 text-sm px-2 py-1 rounded-full">${job.match} match</span>
            </div>
            <h3 class="text-xl font-bold mb-1">${job.title}</h3>
            <p class="text-gray-500 mb-2">${job.salary} • ${job.location}</p>
            <div class="flex gap-2 mb-4">${skillsHTML}</div>
            <div class="w-full h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center">
                <img id="preview-${job.id}" class="max-h-28 object-contain hidden"/>
                <input type="file" id="file-${job.id}" accept="image/*" class="hidden"/>
                <label for="file-${job.id}" class="text-gray-500 text-sm cursor-pointer flex flex-col items-center">
                    <svg class="w-10 h-10 text-gray-400 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v4h16v-4M4 12l8-8 8 8"></path>
                    </svg>
                    Click to upload
                </label>
            </div>
        `;

        // Upload Preview
        const fileInput = card.querySelector(`#file-${job.id}`);
        const previewImg = card.querySelector(`#preview-${job.id}`);
        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    previewImg.src = ev.target.result;
                    previewImg.classList.remove("hidden");
                };
                reader.readAsDataURL(file);
            }
        });

        jobCardsContainer.appendChild(card);
    });
}

document.addEventListener("DOMContentLoaded", renderJobs);
</script>
{% endblock %}