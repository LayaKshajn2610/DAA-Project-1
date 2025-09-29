// Runs after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector("input[name='ingredients']");
  const form = document.querySelector("form");
  const previewBox = document.createElement("div");

  if (input && form) {
    previewBox.style.marginTop = "10px";
    previewBox.style.display = "flex";
    previewBox.style.flexWrap = "wrap";
    previewBox.style.gap = "6px";
    form.appendChild(previewBox);

    // Show live preview of entered ingredients
    input.addEventListener("input", () => {
      previewBox.innerHTML = "";
      const items = input.value.split(",").map(s => s.trim()).filter(Boolean);
      items.forEach(i => {
        const chip = document.createElement("span");
        chip.textContent = i;
        chip.style.padding = "4px 8px";
        chip.style.background = "rgba(37,99,235,0.1)";
        chip.style.color = "#2563eb";
        chip.style.fontSize = "13px";
        chip.style.borderRadius = "999px";
        previewBox.appendChild(chip);
      });
    });

    // Validate before submit
    form.addEventListener("submit", (e) => {
      const items = input.value.split(",").map(s => s.trim()).filter(Boolean);
      if (items.length === 0) {
        e.preventDefault();
        alert("⚠️ Please enter at least one ingredient.");
      }
    });
  }

  // Fade-in animation for recipe cards
  const recipes = document.querySelectorAll(".recipe");
  recipes.forEach((card, idx) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(10px)";
    card.style.transition = "all .4s ease";
    setTimeout(() => {
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 120 * idx);
  });
});
