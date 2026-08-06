 function searchTable() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let table = document.getElementById("phoneTable");
    let rows = table.getElementsByTagName("tr");
    let depRows = document.querySelectorAll(".department-row");

    // Avval barcha department satrlarini yashiramiz
    depRows.forEach(dep => dep.style.display = "none");

    let lastDep = null;
    for (let i = 0; i < rows.length; i++) {
        let row = rows[i];
        if (row.classList.contains("department-row")) {
            lastDep = row; // Oxirgi departmentni eslab qolamiz
            continue;
        }

        let text = row.innerText.toLowerCase();
        if (text.includes(input)) {
            row.style.display = "";
            if (lastDep) lastDep.style.display = ""; // Department ham ko‘rinsin
        } else {
            row.style.display = "none";
        }
    }
}