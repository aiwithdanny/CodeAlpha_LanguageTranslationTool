// Frontend logic: API call, loading state, toasts, copy, text-to-speech.
const input = document.getElementById("input");
const output = document.getElementById("output");
const goBtn = document.getElementById("go");
const counter = document.getElementById("counter");
const toast = document.getElementById("toast");
const MAX_LEN = parseInt(document.getElementById("maxLen").value, 10);

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3500);
}

// Character counter: user ko limit ka pata rahe
input.addEventListener("input", () => {
  counter.textContent = `${input.value.length} / ${MAX_LEN}`;
  if (input.value.length > MAX_LEN) counter.style.color = "red";
  else counter.style.color = "";
});

// Swap button: source <-> target languages
document.getElementById("swap").onclick = () => {
  const s = document.getElementById("source");
  const t = document.getElementById("target");
  [s.value, t.value] = [t.value, s.value];
};

goBtn.onclick = async () => {
  const text = input.value.trim();
  if (!text) { showToast("Pehle kuch text likhein."); return; }
  if (text.length > MAX_LEN) { showToast(`Text ${MAX_LEN} characters se zyada hai.`); return; }

  // Loading state: button disable + spinner
  goBtn.disabled = true;
  goBtn.innerHTML = '<span class="spinner"></span>Translating...';
  output.textContent = "";
  output.classList.add("empty");

  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source: document.getElementById("source").value,
        target: document.getElementById("target").value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Kuch ghalat ho gaya.");
    output.textContent = data.translation;
    output.classList.remove("empty");
  } catch (err) {
    showToast(err.message); // neeche red toast me error
  } finally {
    goBtn.disabled = false;
    goBtn.textContent = "Translate";
  }
};

document.getElementById("copy").onclick = async () => {
  const text = output.textContent.trim();
  if (!text || output.classList.contains("empty")) { showToast("Copy karne ke liye kuch nahi."); return; }
  await navigator.clipboard.writeText(text);
  showToast("Copied!");
};

document.getElementById("speak").onclick = () => {
  const text = output.textContent.trim();
  if (!text || output.classList.contains("empty")) { showToast("Bolne ke liye kuch nahi."); return; }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = document.getElementById("target").value;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
};
