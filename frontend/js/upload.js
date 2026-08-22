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
});

uploadButton.addEventListener("click", function () {

    if (fileInput.files.length === 0) {
        uploadStatus.textContent = "Please select a file first.";
        return;
    }

    const file = fileInput.files[0];

    uploadStatus.textContent =
        `"${file.name}" is ready to be uploaded.`;

});