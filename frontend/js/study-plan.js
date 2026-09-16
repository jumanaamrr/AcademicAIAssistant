const API_BASE_URL = "http://localhost:8001";

const subjectInput = document.getElementById("subject");
const examDateInput = document.getElementById("examDate");
const difficultyInput = document.getElementById("difficulty");
const hoursInput = document.getElementById("hours");
const startDateInput = document.getElementById("startDate");
const generateButton = document.getElementById("generateButton");
const scheduleResult = document.getElementById("scheduleResult");

// Array to store multiple subjects
let subjects = [];

// Add subject to list
function addSubject() {
    const subject = subjectInput.value.trim();
    const examDate = examDateInput.value;
    const difficulty = difficultyInput.value;
    
    if (subject === "") {
        alert("Please enter the subject.");
        return;
    }
    
    if (examDate === "") {
        alert("Please select the exam date.");
        return;
    }
    
    if (difficulty === "") {
        alert("Please select the difficulty.");
        return;
    }
    
    subjects.push({ name: subject, exam_date: examDate, difficulty: difficulty });
    
    // Clear inputs
    subjectInput.value = "";
    examDateInput.value = "";
    difficultyInput.value = "";
    
    // Update display
    displaySubjects();
    alert(`Added "${subject}" to the list.`);
}

function displaySubjects() {
    console.log("Current subjects:", subjects);
}

generateButton.addEventListener("click", async function () {
    const hours = Number(hoursInput.value);
    const startDate = startDateInput.value;
    
    if (subjects.length === 0) {
        alert("Please add at least one subject.");
        return;
    }
    
    if (!hours || hours <= 0) {
        alert("Please enter your available study hours.");
        return;
    }
    
    if (startDate === "") {
        alert("Please select the start date.");
        return;
    }
    
    // Generate schedule via API
    try {
        scheduleResult.innerHTML = "<p style='text-align:center;'>Generating schedule...</p>";
        
        const response = await fetch(`${API_BASE_URL}/study-schedule/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                subjects: subjects,
                available_hours_per_day: hours,
                start_date: startDate
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySchedule(data);
        } else {
            scheduleResult.innerHTML = `<p style='color:red;'>Error: ${data.detail || "Failed to generate schedule"}</p>`;
        }
    } catch (error) {
        scheduleResult.innerHTML = `<p style='color:red;'>Error: ${error.message}</p>`;
    }
});

function displaySchedule(data) {
    scheduleResult.innerHTML = "";
    
    // Summary
    const heading = document.createElement("div");
    heading.className = "schedule-summary";
    heading.innerHTML = `
        <h3>Study Schedule</h3>
        <p>Total days: ${data.total_days}</p>
        <p>Subjects: ${subjects.map(s => s.name).join(", ")}</p>
    `;
    scheduleResult.appendChild(heading);
    
    // Schedule list
    const scheduleList = document.createElement("div");
    scheduleList.className = "schedule-list";
    
    data.schedule.forEach(function(day) {
        const item = document.createElement("div");
        item.className = "schedule-item";
        
        let sessionsHTML = "";
        day.sessions.forEach(function(session) {
            sessionsHTML += `
                <p style="margin: 4px 0; font-size: 14px;">
                    ${session.subject} (${session.difficulty}) - ${session.hours} hours
                </p>
            `;
        });
        
        item.innerHTML = `
            <div>
                <strong>${formatDate(day.date)}</strong>
                <p>Total: ${day.total_hours} hours</p>
                ${sessionsHTML}
            </div>
        `;
        
        scheduleList.appendChild(item);
    });
    
    scheduleResult.appendChild(scheduleList);
    
    // Note
    if (data.total_days > 14) {
        const note = document.createElement("p");
        note.className = "schedule-note";
        note.textContent = "The preview displays the first 14 days of your study plan.";
        scheduleResult.appendChild(note);
    }
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric"
    });
}

// Add "Add Subject" button to the UI
document.addEventListener("DOMContentLoaded", function() {
    // Create add subject button
    const addButton = document.createElement("button");
    addButton.textContent = "Add Subject";
    addButton.className = "primary-button";
    addButton.style.marginTop = "10px";
    addButton.addEventListener("click", addSubject);
    
    // Insert it after the difficulty select
    const difficultySelect = document.getElementById("difficulty");
    difficultySelect.parentNode.insertBefore(addButton, difficultySelect.nextSibling);
});