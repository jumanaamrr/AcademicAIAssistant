const subjectInput = document.getElementById("subject");
const examDateInput = document.getElementById("examDate");
const difficultyInput = document.getElementById("difficulty");
const hoursInput = document.getElementById("hours");
const startDateInput = document.getElementById("startDate");

const generateButton =
    document.getElementById("generateButton");

const scheduleResult =
    document.getElementById("scheduleResult");

generateButton.addEventListener("click", function () {

    const subject = subjectInput.value.trim();
    const examDate = examDateInput.value;
    const difficulty = difficultyInput.value;
    const hours = Number(hoursInput.value);
    const startDate = startDateInput.value;

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

    if (!hours || hours <= 0) {
        alert("Please enter your available study hours.");
        return;
    }

    if (startDate === "") {
        alert("Please select the start date.");
        return;
    }

    const start = new Date(startDate);
    const exam = new Date(examDate);

    if (start >= exam) {
        alert("The start date must be before the exam date.");
        return;
    }

    const millisecondsPerDay =
        1000 * 60 * 60 * 24;

    const days =
        Math.ceil(
            (exam - start) / millisecondsPerDay
        );

    generateSchedule(
        subject,
        difficulty,
        hours,
        start,
        days
    );
});

function generateSchedule(
    subject,
    difficulty,
    hours,
    startDate,
    days
) {

    scheduleResult.innerHTML = "";

    const heading = document.createElement("div");

    heading.className = "schedule-summary";

    heading.innerHTML = `
        <h3>${subject}</h3>
        <p>Difficulty: ${difficulty}</p>
        <p>Available study time: ${hours} hours per day</p>
        <p>Study period: ${days} days</p>
    `;

    scheduleResult.appendChild(heading);

    const scheduleList =
        document.createElement("div");

    scheduleList.className = "schedule-list";

    const numberOfDays =
        Math.min(days, 14);

    for (let i = 0; i < numberOfDays; i++) {

        const currentDate =
            new Date(startDate);

        currentDate.setDate(
            currentDate.getDate() + i
        );

        const formattedDate =
            currentDate.toLocaleDateString(
                "en-US",
                {
                    weekday: "short",
                    month: "short",
                    day: "numeric"
                }
            );

        let topic;

        if (i % 3 === 0) {
            topic = "Study new topics";
        } else if (i % 3 === 1) {
            topic = "Review previous topics";
        } else {
            topic = "Practice questions and revision";
        }

        const item =
            document.createElement("div");

        item.className = "schedule-item";

        item.innerHTML = `
            <div>
                <strong>${formattedDate}</strong>
                <p>${topic}</p>
            </div>

            <span>${hours} hours</span>
        `;

        scheduleList.appendChild(item);
    }

    scheduleResult.appendChild(scheduleList);

    if (days > 14) {

        const note =
            document.createElement("p");

        note.className = "schedule-note";

        note.textContent =
            "The preview displays the first 14 days of your study plan.";

        scheduleResult.appendChild(note);
    }
}