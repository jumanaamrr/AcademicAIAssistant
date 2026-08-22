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
        grade: Number(grade)
    });

    courseNameInput.value = "";
    creditHoursInput.value = "";
    gradeInput.value = "";

    displayCourses();
    calculateGPA();
});

function displayCourses() {

    courseTable.innerHTML = "";

    courses.forEach(function (course, index) {

        const row = document.createElement("tr");

        const gradeLetter = getGradeLetter(course.grade);

        const points = course.grade * course.credits;

        row.innerHTML = `
            <td>${course.name}</td>
            <td>${course.credits}</td>
            <td>${gradeLetter}</td>
            <td>${points.toFixed(2)}</td>
            <td>
                <button
                    class="delete-button"
                    onclick="removeCourse(${index})"
                >
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
    calculateGPA();
}

function calculateGPA() {

    if (courses.length === 0) {

        gpaValue.textContent = "0.00";

        return;
    }

    let totalQualityPoints = 0;
    let totalCredits = 0;

    courses.forEach(function (course) {

        totalQualityPoints +=
            course.grade * course.credits;

        totalCredits += course.credits;

    });

    const gpa =
        totalQualityPoints / totalCredits;

    gpaValue.textContent = gpa.toFixed(2);
}

function getGradeLetter(value) {

    if (value === 4) return "A";
    if (value === 3.7) return "A-";
    if (value === 3.3) return "B+";
    if (value === 3) return "B";
    if (value === 2.7) return "B-";
    if (value === 2.3) return "C+";
    if (value === 2) return "C";
    if (value === 1.7) return "C-";
    if (value === 1.3) return "D+";
    if (value === 1) return "D";

    return "F";
}