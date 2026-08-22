const API_BASE_URL = "http://localhost:8001";

const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

fileInput.addEventListener("change", function () {
    if (fileInput.files.length === 0) {
        fileName.textContent = "No file selected";
        return;
    }
    
    const file = fileInput.files[0];
    fileName.textContent = file.name;
    uploadStatus.textContent = "";
    uploadStatus.style.color = "black";
});

uploadButton.addEventListener("click", async function () {
    if (fileInput.files.length === 0) {
        uploadStatus.textContent = "Please select a file first.";
        uploadStatus.style.color = "red";
        return;
    }
    
    const file = fileInput.files[0];
    const courseName = prompt("Enter the course name:", "Computer Science 101");
    
    if (!courseName) {
        uploadStatus.textContent = "Course name is required.";
        uploadStatus.style.color = "red";
        return;
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append("file", file);
    formData.append("course_name", courseName);
    
    // Disable button and show loading
    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    uploadStatus.textContent = "Uploading and processing syllabus...";
    uploadStatus.style.color = "blue";
    
    try {
        const response = await fetch(`${API_BASE_URL}/syllabus/upload`, {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            uploadStatus.textContent = `${data.message}`;
            uploadStatus.style.color = "green";
            fileName.textContent = "File uploaded successfully!";
        } else {
            uploadStatus.textContent = `Error: ${data.detail || "Upload failed"}`;
            uploadStatus.style.color = "red";
        }
    } catch (error) {
        uploadStatus.textContent = `Error: ${error.message}`;
        uploadStatus.style.color = "red";
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload Syllabus";
    }
});