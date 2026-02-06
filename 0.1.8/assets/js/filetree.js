document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".file-tree .folder-header").forEach(header => {
    header.addEventListener("click", () => {
      header.parentElement.classList.toggle("open");
    });
  });
});
