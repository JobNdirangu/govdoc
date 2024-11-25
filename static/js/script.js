const hamBurger = document.querySelector(".toggle-btn");
const sidebar = document.querySelector("#sidebar");

// Function to check and apply the saved sidebar state from localStorage
function applySidebarState() {
    const sidebarState = localStorage.getItem("sidebarState");
    
    if (sidebarState === "expanded") {
        sidebar.classList.add("expand");
    } else {
        sidebar.classList.remove("expand");
    }
}

// Function to toggle sidebar state and save it to localStorage
function toggleSidebar() {
    sidebar.classList.toggle("expand");

    // Save the current state in localStorage
    if (sidebar.classList.contains("expand")) {
        localStorage.setItem("sidebarState", "expanded");
    } else {
        localStorage.setItem("sidebarState", "collapsed");
    }
}

// Apply the saved state on page load
applySidebarState();

// Toggle the sidebar state on button click
hamBurger.addEventListener("click", toggleSidebar);

// Prevent the full page reload if the link is not supposed to navigate away
document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', function (e) {
        if (link.getAttribute('href') === "#") {
            e.preventDefault();
        }
    });
});
