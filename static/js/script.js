document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("search");
  if (search) {
    search.addEventListener("keyup", () => {
      let term = search.value.toLowerCase();

      // User Dashboard (cards)
      if (document.querySelector(".grid .card")) {
        document.querySelectorAll(".grid .card").forEach(card => {
          let text = card.querySelector(".card-body").innerText.toLowerCase();
          if (term && text.includes(term)) {
            card.style.display = "block";
            card.querySelectorAll(".card-title, .card-text").forEach(el => {
              let plain = el.textContent;
              el.innerHTML = term ? plain.replace(new RegExp(`(${term})`, "gi"), `<mark>$1</mark>`) : plain;
            });
          } else {
            card.style.display = term ? "none" : "block";
            card.querySelectorAll(".card-title, .card-text").forEach(el => {
              el.innerHTML = el.textContent;
            });
          }
        });
      }

      // Admin Dashboard (table rows)

		if (document.querySelector("table")) {
		  document.querySelectorAll("table tbody tr").forEach(row => {
			let text = row.innerText.toLowerCase();

			if (term && text.includes(term)) {
			  row.style.display = "";
			  row.querySelectorAll("td").forEach(cell => {
				// Skip cells that contain buttons/links/images
				if (!cell.querySelector("img") && !cell.querySelector("a") && !cell.querySelector("button")) {
				  let plain = cell.textContent;
				  if (term) {
					let regex = new RegExp(`(${term})`, "gi");
					cell.innerHTML = plain.replace(regex, `<mark>$1</mark>`);
				  } else {
					cell.innerHTML = plain;
				  }
				}
			  });
			} else {
			  row.style.display = term ? "none" : "";
			  row.querySelectorAll("td").forEach(cell => {
				if (!cell.querySelector("img") && !cell.querySelector("a") && !cell.querySelector("button")) {
				  cell.innerHTML = cell.textContent;
				}
			  });
			}
		  });
		}


  // Image zoom + fullscreen
  document.querySelectorAll(".zoomable").forEach(img => {
    img.addEventListener("click", () => {
      let fullscreen = document.createElement("div");
      fullscreen.classList.add("fullscreen");
      fullscreen.innerHTML = `<img src="${img.src}">`;
      fullscreen.addEventListener("click", () => fullscreen.remove());
      document.body.appendChild(fullscreen);
    });
  });
});
