(() => {
  const fileInput = document.getElementById("image-file");
  const fileLabel = document.getElementById("file-label");
  const dropZone = document.getElementById("drop-zone");
  const previewWrap = document.getElementById("preview-wrap");
  const preview = document.getElementById("image-preview");
  const clearButton = document.getElementById("clear-image");
  const textArea = document.getElementById("extracted-text");
  const charCount = document.getElementById("character-count");
  const copyButton = document.getElementById("copy-button");
  const downloadButton = document.getElementById("download-button");
  const feedback = document.getElementById("feedback");
  const form = document.getElementById("upload-form");
  const extractButton = document.getElementById("extract-button");
  let previewUrl = null;

  const updateCount = () => {
    charCount.textContent = `${textArea.value.length} characters`;
  };

  const showFile = (file) => {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      feedback.textContent = "File is larger than 10 MB. Choose a smaller image.";
      fileInput.value = "";
      return;
    }
    fileLabel.textContent = file.name;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = URL.createObjectURL(file);
    preview.src = previewUrl;
    previewWrap.hidden = false;
    feedback.textContent = "";
  };

  fileInput?.addEventListener("change", () => showFile(fileInput.files[0]));
  clearButton?.addEventListener("click", () => {
    fileInput.value = "";
    fileLabel.textContent = "Choose a screenshot or drop it here";
    previewWrap.hidden = true;
    preview.removeAttribute("src");
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    feedback.textContent = "";
  });

  ["dragenter", "dragover"].forEach((eventName) => dropZone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
  }));
  ["dragleave", "drop"].forEach((eventName) => dropZone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
  }));
  dropZone?.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (!file) return;
    try {
      const transfer = new DataTransfer();
      transfer.items.add(file);
      fileInput.files = transfer.files;
      showFile(file);
    } catch {
      feedback.textContent = "Use Browse files to select this image.";
    }
  });

  textArea?.addEventListener("input", updateCount);
  copyButton?.addEventListener("click", async () => {
    if (!textArea.value) {
      feedback.textContent = "There is no text to copy yet.";
      return;
    }
    try {
      await navigator.clipboard.writeText(textArea.value);
      feedback.textContent = "Text copied to clipboard.";
    } catch {
      textArea.select();
      const copied = document.execCommand("copy");
      feedback.textContent = copied ? "Text copied to clipboard." : "Select the text and copy it manually.";
    }
  });

  downloadButton?.addEventListener("click", () => {
    if (!textArea.value) {
      feedback.textContent = "There is no text to download yet.";
      return;
    }
    const blob = new Blob([textArea.value], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ocr_result.txt";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });

  form?.addEventListener("submit", () => {
    extractButton.disabled = true;
    extractButton.textContent = "Extracting text…";
  });
  updateCount();
})();
