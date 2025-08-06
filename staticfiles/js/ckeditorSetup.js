let editorInstance = null;
let editEditorInstance = null;

function initializeCKEditor() {
    console.log("Attempting to initialize CKEditor");
    
    if (typeof CKEDITOR === 'undefined') {
        console.error("CKEditor not loaded!");
        return;
    }
    
    if (!editorInstance) {
        try {
            editorInstance = CKEDITOR.replace('content-input', {
                height: 400,
                width: '100%',
                allowedContent: true
            });
            
            console.log("CKEditor initialized successfully");
            
            editorInstance.on('instanceReady', function() {
                console.log("CKEditor instance ready");
                
                setTimeout(function() {
                    addSimpleUploadButton('content-input', editorInstance);
                }, 500);
            });
            
        } catch (error) {
            console.error("Error initializing CKEditor:", error);
        }
    }
}

function initializeEditCKEditor() {
    console.log("Attempting to initialize Edit CKEditor");
    
    if (typeof CKEDITOR === 'undefined') {
        console.error("CKEditor not loaded!");
        return;
    }
    
    if (!editEditorInstance) {
        try {
            editEditorInstance = CKEDITOR.replace('edit-content-input', {
                height: 400,
                width: '100%',
                allowedContent: true
            });
            
            console.log("Edit CKEditor initialized successfully");
            
            editEditorInstance.on('instanceReady', function() {
                console.log("Edit CKEditor instance ready");
                
                setTimeout(function() {
                    addSimpleUploadButton('edit-content-input', editEditorInstance);
                }, 500);
            });
            
        } catch (error) {
            console.error("Error initializing Edit CKEditor:", error);
        }
    }
}

// Add upload button
function addSimpleUploadButton(textareaId, editor) {
    var editorContainer = document.getElementById('cke_' + textareaId);
    if (editorContainer) {
        var existingButton = editorContainer.parentNode.querySelector('.custom-upload-button');
        if (existingButton) {
            existingButton.remove();
        }
        
        var uploadButton = document.createElement('button');
        uploadButton.type = 'button';
        uploadButton.innerHTML = '📹 Upload Video/Image';
        uploadButton.className = 'custom-upload-button';
        uploadButton.style.cssText = 'margin-top: 5px; padding: 8px 12px; background: #0084ff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; display: block;';
        
        uploadButton.onclick = function() {
            console.log("Upload button clicked");
            uploadVideoDialog(editor);
        };
        
        editorContainer.parentNode.insertBefore(uploadButton, editorContainer.nextSibling);
        console.log("Upload button added for", textareaId);
    }
}

// Upload function
function uploadVideoDialog(editor) {
    console.log("Opening upload dialog");
    
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '*';
    input.style.display = 'none';
    
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        console.log("File selected:", file.name, file.type, "Size:", file.size);
        
        const loadingMsg = editor.showNotification('Uploading file...', 'info', 0);
        
        const formData = new FormData();
        formData.append('upload', file);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        fetch('/upload-media/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingMsg.hide();
            
            if (data.uploaded) {
                const fileName = file.name.toLowerCase();
                const ext = fileName.split('.').pop();
                const videoExts = ['webm', 'mp4', 'ogg', 'avi', 'mov'];
                
                if (videoExts.includes(ext)) {
                    createDraggableVideo(editor, data.url);
                } else {
                    createDraggableImage(editor, data.url);
                }
                
                editor.showNotification('File uploaded successfully!', 'success', 3000);
            } else {
                editor.showNotification('Upload failed: ' + (data.error || 'Unknown error'), 'warning', 5000);
            }
        })
        .catch(error => {
            loadingMsg.hide();
            console.error('Upload error:', error);
            editor.showNotification('Upload failed. Please try again.', 'warning', 5000);
        });
    });
    
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// Create draggable video - all videos autoplay like GIFs
function createDraggableVideo(editor, videoUrl) {
    const videoId = 'vid_' + Date.now();
    
    // All videos autoplay, loop, and are muted (GIF-like behavior)
    const videoHtml = `<video id="${videoId}" autoplay loop muted playsinline src="${videoUrl}" draggable="true" style="width: 200px; height: auto; margin: 5px; cursor: move; border: 2px solid #ddd;">
        Your browser does not support the video tag.
    </video>`;
    
    editor.insertHtml(videoHtml);
    
    // Wait for insertion then setup drag
    setTimeout(() => {
        setupDragAndDrop(editor, videoId);
    }, 200);
}

// Create draggable image
function createDraggableImage(editor, imageUrl) {
    const imgId = 'img_' + Date.now();
    
    const imageHtml = `<img id="${imgId}" src="${imageUrl}" draggable="true" style="width: 300px; height: auto; margin: 5px; cursor: move; border: 2px solid #ddd;" alt="Uploaded image">`;
    
    editor.insertHtml(imageHtml);
    
    setTimeout(() => {
        setupDragAndDrop(editor, imgId);
    }, 200);
}

// Setup drag and drop
function setupDragAndDrop(editor, elementId) {
    const element = editor.document.$.getElementById(elementId);
    if (!element) {
        console.log("Element not found:", elementId);
        return;
    }
    
    console.log("Setting up drag for:", elementId);
    
    // Drag start
    element.addEventListener('dragstart', function(e) {
        console.log("Drag started for", elementId);
        e.dataTransfer.setData('text/plain', elementId);
        e.dataTransfer.effectAllowed = 'move';
        
        // Visual feedback
        element.style.opacity = '0.5';
        element.style.border = '2px solid #0084ff';
    });
    
    // Drag end
    element.addEventListener('dragend', function(e) {
        console.log("Drag ended for", elementId);
        element.style.opacity = '1';
        element.style.border = '2px solid #ddd';
    });
    
    // Make the editor body a drop zone
    const editorBody = editor.document.$.body;
    
    editorBody.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    
    editorBody.addEventListener('drop', function(e) {
        e.preventDefault();
        
        const draggedId = e.dataTransfer.getData('text/plain');
        const draggedElement = editor.document.$.getElementById(draggedId);
        
        if (!draggedElement) return;
        
        console.log("Dropped", draggedId, "at", e.clientX, e.clientY);
        
        // Get drop position relative to editor
        const editorRect = editorBody.getBoundingClientRect();
        const x = e.clientX - editorRect.left;
        const y = e.clientY - editorRect.top;
        
        // Position the element
        draggedElement.style.position = 'absolute';
        draggedElement.style.left = x + 'px';
        draggedElement.style.top = y + 'px';
        draggedElement.style.zIndex = '10';
        
        console.log("Positioned", draggedId, "at", x, y);
    });
    
    console.log("Drag setup completed for", elementId);
}

// Keep your existing show/hide functions
function showAddLogForm() {
    console.log("showAddLogForm called");
    const overlay = document.getElementById('addLogFormOverlay');
    overlay.style.display = 'flex';
    
    if (typeof CKEDITOR !== 'undefined') {
        setTimeout(initializeCKEditor, 300);
    } else {
        console.error("CKEditor not available");
    }
}

function hideAddLogForm() {
    const overlay = document.getElementById('addLogFormOverlay');
    overlay.style.display = 'none';
    if (editorInstance) {
        editorInstance.destroy();
        editorInstance = null;
    }
}

function showEditLogForm() {
    const overlay = document.getElementById('editLogFormOverlay');
    overlay.style.display = 'flex';
    
    if (typeof CKEDITOR !== 'undefined') {
        setTimeout(initializeEditCKEditor, 300);
    } else {
        console.error("CKEditor not available");
    }
}

function hideEditLogForm() {
    const overlay = document.getElementById('editLogFormOverlay');
    overlay.style.display = 'none';
    if (editEditorInstance) {
        editEditorInstance.destroy();
        editEditorInstance = null;
    }
}

// Keep your existing form submission handlers
document.getElementById('addLogForm').addEventListener('submit', function(e) {
    if (editorInstance) {
        editorInstance.updateElement();
    }
});

document.getElementById('editLogForm').addEventListener('submit', function(e) {
    if (editEditorInstance) {
        editEditorInstance.updateElement();
    }
});