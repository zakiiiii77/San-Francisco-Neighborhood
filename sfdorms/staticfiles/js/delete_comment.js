document.addEventListener("click", function(e) {
    if (e.target.classList.contains("delete-comment-btn")) {
        const commentId = e.target.getAttribute("data-comment-id");
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        const addCommentUrl = document.getElementById('urls').dataset.addCommentUrl;

        fetch(addCommentUrl.replace('0', taskId), {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentDiv = document.getElementById(`comment-${commentId}`);
                if (commentDiv) commentDiv.remove();
            } else {
                alert(data.error || "Failed to delete comment.");
            }
        });
    }
});

