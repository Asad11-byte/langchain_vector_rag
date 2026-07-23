// Handles file upload and the document list panel.

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const documentList = document.getElementById("document-list");

function setStatus(message, type = "") {
  uploadStatus.textContent = message;
  uploadStatus.className = `status ${type}`;
}

async function loadDocuments() {
  try {
    const res = await fetch("/api/documents");
    const data = await res.json();
    renderDocumentList(data.documents || []);
  } catch (err) {
    console.error("Failed to load documents:", err);
  }
}

function renderDocumentList(documents) {
  documentList.innerHTML = "";

  if (documents.length === 0) {
    documentList.innerHTML = `<li style="color: var(--muted);">No documents uploaded yet.</li>`;
    return;
  }

  for (const doc of documents) {
    const li = document.createElement("li");

    const label = document.createElement("span");
    label.textContent = `${doc.filename} (${doc.chunk_count} chunks)`;

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "✕";
    deleteBtn.className = "delete-btn";
    deleteBtn.title = "Delete document";
    deleteBtn.onclick = () => deleteDocument(doc.id);

    li.appendChild(label);
    li.appendChild(deleteBtn);
    documentList.appendChild(li);
  }
}

async function deleteDocument(documentId) {
  if (!confirm("Delete this document and its indexed chunks?")) return;

  try {
    const res = await fetch(`/api/documents/${documentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");
    await loadDocuments();
  } catch (err) {
    console.error(err);
    alert("Failed to delete document.");
  }
}

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  uploadBtn.disabled = true;
  setStatus("Uploading and indexing...");

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    setStatus(`✓ Indexed "${data.filename}" (${data.chunk_count} chunks)`, "success");
    fileInput.value = "";
    await loadDocuments();
  } catch (err) {
    setStatus(`✗ ${err.message}`, "error");
  } finally {
    uploadBtn.disabled = false;
  }
});

// initial load
loadDocuments();
