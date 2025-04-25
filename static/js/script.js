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
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("message").innerText = "Error occurred!";
      });
  });

  
  
 
});

