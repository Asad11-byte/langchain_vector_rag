// Handles the chat/query panel.

const queryForm = document.getElementById("query-form");
const questionInput = document.getElementById("question-input");
const queryBtn = document.getElementById("query-btn");
const chatWindow = document.getElementById("chat-window");

function appendMessage(role, text, sources = []) {
  const msg = document.createElement("div");
  msg.className = `message ${role}`;
  msg.textContent = text;

  if (sources && sources.length > 0) {
    const details = document.createElement("details");
    details.className = "sources";

    const summary = document.createElement("summary");
    summary.textContent = `${sources.length} source${sources.length > 1 ? "s" : ""}`;
    details.appendChild(summary);

    sources.forEach((s) => {
      const p = document.createElement("p");
      const label = s.source_filename ? `${s.source_filename}${s.page ? ` (p.${s.page})` : ""}` : "Source";
      p.innerHTML = `<strong>${label}:</strong> ${s.text.slice(0, 200)}${s.text.length > 200 ? "..." : ""}`;
      details.appendChild(p);
    });

    msg.appendChild(details);
  }

  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

queryForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage("user", question);
  questionInput.value = "";
  queryBtn.disabled = true;

  const thinkingMsg = document.createElement("div");
  thinkingMsg.className = "message bot";
  thinkingMsg.textContent = "Thinking...";
  chatWindow.appendChild(thinkingMsg);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    thinkingMsg.remove();

    if (!res.ok) {
      throw new Error(data.detail || "Query failed");
    }

    appendMessage("bot", data.answer, data.sources);
  } catch (err) {
    thinkingMsg.remove();
    appendMessage("bot", `Error: ${err.message}`);
  } finally {
    queryBtn.disabled = false;
  }
});
