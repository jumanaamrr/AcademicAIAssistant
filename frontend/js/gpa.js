const API_BASE_URL = "http://localhost:8001";

const courseNameInput = document.getElementById("courseName");
const creditHoursInput = document.getElementById("creditHours");
const gradeInput = document.getElementById("grade");
const addCourseButton = document.getElementById("addCourseButton");
const courseTable = document.getElementById("courseTable");
const gpaValue = document.getElementById("gpaValue");

let courses = [];

addCourseButton.addEventListener("click", function () {
    const courseName = courseNameInput.value.trim();
    const creditHours = Number(creditHoursInput.value);
    const grade = gradeInput.value;
    
    if (courseName === "") {
        alert("Please enter the course name.");
        return;
    }
    
    if (!creditHours || creditHours <= 0) {
        alert("Please enter valid credit hours.");
        return;
    }
    
    if (grade === "") {
        alert("Please select a grade.");
        return;
    }
    
    courses.push({
        name: courseName,
        credits: creditHours,
        grade: grade
    });
    
    courseNameInput.value = "";
    creditHoursInput.value = "";
    gradeInput.value = "";
    
    displayCourses();
    calculateGPAWithAPI();
});

function displayCourses() {
    courseTable.innerHTML = "";
    
    courses.forEach(function (course, index) {
        const row = document.createElement("tr");
        
        row.innerHTML = `
            <td>${course.name}</td>
            <td>${course.credits}</td>
            <td>${course.grade}</td>
            <td>${(getGradePoints(course.grade) * course.credits).toFixed(2)}</td>
            <td>
                <button class="delete-button" onclick="removeCourse(${index})">
                    Remove
                </button>
            </td>
        `;
        
        courseTable.appendChild(row);
    });
}

function removeCourse(index) {
    courses.splice(index, 1);
    displayCourses();
    calculateGPAWithAPI();
}

async function calculateGPAWithAPI() {
    if (courses.length === 0) {
        gpaValue.textContent = "0.00";
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/gpa/calculate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                courses: courses.map(c => ({
                    name: c.name,
                    credits: c.credits,
                    grade: c.grade
                }))
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            gpaValue.textContent = data.gpa.toFixed(2);
        } else {
            gpaValue.textContent = "Error";
            alert(`Error: ${data.detail || "Failed to calculate GPA"}`);
        }
    } catch (error) {
        gpaValue.textContent = "Error";
        alert(`Error: ${error.message}`);
    }
}

function getGradePoints(grade) {
    const points = {
        "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0,
        "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "F": 0.0
    };
    return points[grade] || 0;
}