document.querySelectorAll(".add-comment-form"). forEach(form => {
    form.addEventListener("submit", function(e) {
        e.preventDefault();
        const taskId = this.getAttribute("data-task-id");
        const formData = new FormData(this);
        const roomId = form.getAttribute("data-room-id");

        fetch(`/rooms/${roomId}/tasks/${taskId}/comment`, {
            method: "POST",
            headers: {
                'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentsDiv = document.getElementById(`comments-${taskId}`);
                commentsDiv.insertAdjacentHTML("beforeend", data.html);
                this.reset();
            }
        });
    });
});