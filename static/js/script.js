document.addEventListener("DOMContentLoaded", function () {
  
  // Teacher Registration
  const teacherRegisterForm = document.getElementById("teacher-register-form");
  teacherRegisterForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const teacherName = document.getElementById("teacher_name").value;
    const teacherId = document.getElementById("teacher_id").value;
    const password = document.getElementById("password").value;

    const data = {
      name: teacherName,
      teacher_id: teacherId,
      password: password,
    };

    fetch("/teacher_register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((result) => {
        document.getElementById("message").innerText = result.message;
        
      // Redirect to home page if registration is successful
      if (result.success) {
        setTimeout(function() {
          window.location.href = '/';  // Assuming home page is '/'
        }, 1000);  // Delay to show message before redirecting
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("message").innerText = "Error occurred!";
    });
});
});

document.addEventListener("DOMContentLoaded", function () {
    // IDs ke input fields ko select karo
    const studentIdInput = document.getElementById("student_id");
    const teacherIdInput = document.getElementById("teacher_id");

    // Function to auto-uppercase
    function autoUppercase(inputElement) {
        inputElement.addEventListener("input", function () {
            this.value = this.value.toUpperCase();
        });
    }

    // Student ID field mein uppercase lagao agar exist karta hai
    if (studentIdInput) {
        autoUppercase(studentIdInput);
    }

    // Teacher ID field mein uppercase lagao agar exist karta hai
    if (teacherIdInput) {
        autoUppercase(teacherIdInput);
    }
});


