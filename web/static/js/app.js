// 全局变量
let uploadedFiles = {};
let currentTaskId = null;
let websocket = null;

console.log('app.js 文件已加载');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    
    // 验证关键DOM元素
    if (!validateDOMElements()) {
        console.error('DOM元素验证失败');
        addLogEntry('页面元素加载不完整，部分功能可能不可用', 'error');
        return;
    }
    
    initializeWebSocket();
    loadUploadedFiles();
    updateGenerateButton();
    
    console.log('初始化完成');
});

// 验证关键DOM元素
function validateDOMElements() {
    const requiredElements = [
        'schedule-file', 'syllabus-file', 'template-file',
        'schedule-upload-area', 'syllabus-upload-area', 'template-upload-area',
        'uploaded-files', 'generate-btn', 'log-container'
    ];
    
    let allValid = true;
    
    requiredElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`找不到必需的DOM元素: ${elementId}`);
            allValid = false;
        }
    });
    
    // 检查文件输入元素
    ['schedule', 'syllabus', 'template'].forEach(type => {
        const fileInput = document.getElementById(`${type}-file`);
        if (fileInput) {
            // 确保文件输入元素有正确的事件监听器
            if (!fileInput.hasAttribute('onchange')) {
                console.warn(`${type}-file 缺少 onchange 事件`);
            }
        }
    });
    
    return allValid;
}

// 初始化WebSocket连接
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/progress`;
    
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = function(event) {
        addLogEntry('WebSocket连接已建立', 'success');
        updateStatus('系统就绪', 'success');
    };
    
    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    websocket.onclose = function(event) {
        addLogEntry('WebSocket连接已断开', 'warning');
        updateStatus('连接断开', 'warning');
        // 尝试重连
        setTimeout(initializeWebSocket, 3000);
    };
    
    websocket.onerror = function(error) {
        addLogEntry('WebSocket连接错误', 'error');
        updateStatus('连接错误', 'error');
    };
}

// 处理WebSocket消息
function handleWebSocketMessage(data) {
    console.log('=== handleWebSocketMessage 被调用 ===');
    console.log('WebSocket消息数据:', data);
    
    if (data.type === 'progress') {
        updateProgress(data);
    } else {
        console.log('未知消息类型:', data.type);
    }
}

// 文件拖拽处理
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event, fileType) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0], fileType);
    }
}

// 文件选择处理
function handleFileSelect(event, fileType) {
    try {
        console.log(`文件选择事件触发: ${fileType}`, event);
        const files = event.target.files;
        console.log(`选择的文件数量: ${files.length}`);
        
        if (files.length > 0) {
            console.log(`开始上传文件: ${files[0].name}`);
            uploadFile(files[0], fileType);
        } else {
            console.log('没有选择文件');
        }
    } catch (error) {
        console.error('文件选择处理错误:', error);
        addLogEntry(`文件选择失败: ${error.message}`, 'error');
    }
}

// 上传文件
async function uploadFile(file, fileType) {
    try {
        console.log(`开始上传文件: ${file.name}, 类型: ${fileType}`);
        
        const uploadArea = document.getElementById(`${fileType}-upload-area`);
        if (!uploadArea) {
            throw new Error(`找不到上传区域: ${fileType}-upload-area`);
        }
        
        const progressDiv = uploadArea.querySelector('.upload-progress');
        const progressBar = progressDiv.querySelector('.progress-bar');
        const placeholder = uploadArea.querySelector('.upload-placeholder');
        
        if (!progressDiv || !progressBar || !placeholder) {
            throw new Error('上传区域元素不完整');
        }
        
        // 预验证文件
        const validationResult = validateFile(file, fileType);
        if (!validationResult.valid) {
            const errorMsg = `文件验证失败: ${validationResult.error}`;
            console.error(errorMsg);
            addLogEntry(errorMsg, 'error');
            return;
        }
        
        // 显示进度条
        placeholder.classList.add('d-none');
        progressDiv.classList.remove('d-none');
        progressBar.style.width = '0%';
        
        const formData = new FormData();
        formData.append('file', file);
        
        console.log(`发送上传请求到: /api/upload/${fileType}`);
        const response = await fetch(`/api/upload/${fileType}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            let errorMessage = `上传失败: ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = `上传失败: ${errorData.detail}`;
                }
            } catch (e) {
                console.log('无法解析错误响应:', e);
            }
            throw new Error(errorMessage);
        }
        
        progressBar.style.width = '100%';
        
        const result = await response.json();
        console.log('上传响应:', result);
        console.log('result.file_id:', result.file_id);
        console.log('fileType:', fileType);
        
        // 保存文件信息
        uploadedFiles[result.file_id] = {
            ...result,
            type: fileType,
            uploadTime: new Date().toLocaleString(),
            fileSize: file.size,
            originalName: file.name
        };
        
        // 更新UI
        uploadArea.classList.add('uploaded');
        placeholder.innerHTML = `
            <i class="bi bi-check-circle-fill text-success display-4"></i>
            <p class="mt-2 mb-0">${file.name}</p>
            <small class="text-muted">上传成功 (${formatFileSize(file.size)})</small>
        `;
        placeholder.classList.remove('d-none');
        
        addLogEntry(`${getFileTypeName(fileType)}上传成功: ${file.name}`, 'success');
        updateUploadedFilesList();
        updateGenerateButton();
        
        // 尝试解析文件
        console.log('准备调用parseFile, file_id:', result.file_id, 'fileType:', fileType);
        setTimeout(() => {
            console.log('开始执行parseFile');
            parseFile(result.file_id, fileType);
        }, 1000);
        
    } catch (error) {
        console.error('Upload error:', error);
        addLogEntry(`上传失败: ${error.message}`, 'error');
        
        // 重置上传区域状态
        const uploadArea = document.getElementById(`${fileType}-upload-area`);
        if (uploadArea) {
            const placeholder = uploadArea.querySelector('.upload-placeholder');
            const progressDiv = uploadArea.querySelector('.upload-progress');
            
            if (placeholder) placeholder.classList.remove('d-none');
            if (progressDiv) progressDiv.classList.add('d-none');
            uploadArea.classList.remove('uploaded');
        }
    }
}

// 预验证文件
function validateFile(file, fileType) {
    const allowedTypes = {
        'schedule': ['.xlsx', '.xls'],
        'syllabus': ['.docx'],
        'template': ['.docx']
    };
    
    const maxFileSize = 50 * 1024 * 1024; // 50MB
    const minFileSize = 100; // 100 bytes
    
    // 检查文件大小
    if (file.size > maxFileSize) {
        return {
            valid: false,
            error: `文件过大: ${formatFileSize(file.size)}, 最大允许: ${formatFileSize(maxFileSize)}`
        };
    }
    
    if (file.size < minFileSize) {
        return {
            valid: false,
            error: `文件过小: ${formatFileSize(file.size)}, 最小要求: ${formatFileSize(minFileSize)}`
        };
    }
    
    // 检查文件类型
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes[fileType].includes(fileExtension)) {
        return {
            valid: false,
            error: `文件类型错误: ${file.name}, 期望类型: ${allowedTypes[fileType].join(', ')}`
        };
    }
    
    // 检查文件名
    if (file.name.length > 100) {
        return {
            valid: false,
            error: '文件名过长，请控制在100字符以内'
        };
    }
    
    // 检查特殊字符
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(file.name)) {
        return {
            valid: false,
            error: '文件名包含非法字符: < > : " / \\ | ? *'
        };
    }
    
    return { valid: true };
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 解析文件
async function parseFile(fileId, fileType) {
    console.log('=== parseFile函数被调用 ===');
    console.log('fileId:', fileId);
    console.log('fileType:', fileType);
    console.log('typeof fileId:', typeof fileId);
    console.log('typeof fileType:', typeof fileType);
    
    try {
        // 验证参数
        if (!fileId) {
            console.error('parseFile: fileId 为空或未定义');
            addLogEntry('解析失败: 文件ID无效', 'error');
            return;
        }
        
        if (!fileType) {
            console.error('parseFile: fileType 为空或未定义');
            addLogEntry('解析失败: 文件类型无效', 'error');
            return;
        }
        
        console.log(`开始解析文件: ${fileId}, 类型: ${fileType}`);
        
        // 检查文件是否存在于uploadedFiles中
        if (!uploadedFiles[fileId]) {
            console.error(`parseFile: 文件ID ${fileId} 不存在于uploadedFiles中`);
            addLogEntry(`解析失败: 文件记录不存在`, 'error');
            return;
        }
        
        // 更新文件状态为解析中
        uploadedFiles[fileId].status = 'parsing';
        updateUploadedFilesList();
        addLogEntry(`正在解析${getFileTypeName(fileType)}...`, 'info');
        
        // 添加调试信息
        const requestBody = JSON.stringify({ file_id: fileId });
        console.log('发送解析请求:', {
            url: `/api/parse/${fileType}`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: { file_id: fileId },
            requestBody: requestBody,
            requestBodyLength: requestBody.length
        });
        
        const response = await fetch(`/api/parse/${fileType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: requestBody
        });
        
        console.log('解析响应:', {
            status: response.status,
            statusText: response.statusText
        });
        
        const result = await response.json();
        console.log('解析结果:', result);
        
        if (result.status === 'success') {
            uploadedFiles[fileId].status = 'parsed';
            uploadedFiles[fileId].data = result.data;
            
            // 显示解析成功的详细信息
            let successMessage = result.message || `${getFileTypeName(fileType)}解析成功`;
            if (result.data && Array.isArray(result.data)) {
                successMessage += ` (共${result.data.length}条记录)`;
            } else if (result.data && result.data.word_count) {
                successMessage += ` (共${result.data.word_count}字)`;
            }
            
            addLogEntry(successMessage, 'success');
            updateUploadedFilesList();
            updateGenerateButton();
        } else {
            // 处理解析错误
            uploadedFiles[fileId].status = 'error';
            uploadedFiles[fileId].error_message = result.detail || '解析失败';
            uploadedFiles[fileId].error_details = result.error_details || '';
            
            const errorMessage = result.detail || '解析失败';
            const errorDetails = result.error_details ? `\n详细信息: ${result.error_details}` : '';
            const fullErrorMessage = errorMessage + errorDetails;
            
            addLogEntry(`解析失败: ${fullErrorMessage}`, 'error');
            updateUploadedFilesList();
        }
    } catch (error) {
        console.error('Parse error:', error);
        console.error('Error details:', JSON.stringify(error, null, 2));
        
        // 更新文件状态为错误
        uploadedFiles[fileId].status = 'error';
        uploadedFiles[fileId].error_message = error.message;
        
        // 尝试获取更详细的错误信息
        let errorMessage = error.message || '未知错误';
        if (error.response) {
            errorMessage += ` (状态码: ${error.response.status})`;
        }
        
        addLogEntry(`解析失败: ${errorMessage}`, 'error');
        updateUploadedFilesList();
    }
}

// 显示重试解析按钮
function showRetryParseButton(fileId, fileType) {
    const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
    if (fileItem) {
        const existingButton = fileItem.querySelector('.retry-parse-btn');
        if (existingButton) {
            existingButton.remove();
        }
        
        const retryButton = document.createElement('button');
        retryButton.className = 'btn btn-sm btn-warning retry-parse-btn mt-2';
        retryButton.innerHTML = '<i class="bi bi-arrow-clockwise"></i> 重试解析';
        retryButton.onclick = () => {
            retryButton.remove();
            parseFile(fileId, fileType);
        };
        
        fileItem.appendChild(retryButton);
    }
}

// 更新已上传文件列表
function updateUploadedFilesList() {
    const container = document.getElementById('uploaded-files');
    container.innerHTML = '';
    
    Object.values(uploadedFiles).forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item fade-in';
        fileItem.setAttribute('data-file-id', file.file_id);
        
        let statusIcon = '';
        let statusText = '';
        let statusClass = '';
        
        switch (file.status) {
            case 'parsed':
                statusIcon = '<i class="bi bi-check-circle-fill"></i>';
                statusText = '已解析';
                statusClass = 'text-success';
                break;
            case 'parsing':
                statusIcon = '<i class="bi bi-hourglass-split"></i>';
                statusText = '解析中...';
                statusClass = 'text-primary';
                break;
            case 'error':
                statusIcon = '<i class="bi bi-exclamation-triangle-fill"></i>';
                statusText = '解析失败';
                statusClass = 'text-danger';
                break;
            default:
                statusIcon = '<i class="bi bi-hourglass-split"></i>';
                statusText = '已上传';
                statusClass = 'text-warning';
        }
        
        const typeLabels = {
            'schedule': '教学进度表',
            'syllabus': '教学大纲',
            'template': '教案模板'
        };
        
        const fileSize = file.fileSize ? ` (${formatFileSize(file.fileSize)})` : '';
        
        fileItem.innerHTML = `
            <div class="file-item-header">
                <div class="file-item-title">
                    <span class="${statusClass}">${statusIcon}</span>
                    ${file.filename}${fileSize}
                </div>
                <div class="file-item-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="showFileDetails('${file.file_id}')" title="查看详情">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${file.status === 'error' ? `
                        <button class="btn btn-sm btn-outline-warning" onclick="retryParseFile('${file.file_id}', '${file.type}')" title="重试解析">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteFile('${file.file_id}')" title="删除文件">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="file-item-type">${typeLabels[file.type]}</div>
            <div class="file-item-status ${statusClass}">${statusText}</div>
            <div class="text-muted small">${file.uploadTime}</div>
            
            ${file.status === 'parsing' ? `
                <div class="file-item-progress mt-2">
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" 
                             style="width: 100%"></div>
                    </div>
                </div>
            ` : ''}
        `;
        
        container.appendChild(fileItem);
    });
}

// 重试解析文件
async function retryParseFile(fileId, fileType) {
    const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
    if (fileItem) {
        const statusElement = fileItem.querySelector('.file-item-status');
        const progressElement = fileItem.querySelector('.file-item-progress');
        
        // 更新状态为解析中
        statusElement.className = 'file-item-status text-primary';
        statusElement.innerHTML = '<i class="bi bi-hourglass-split"></i> 解析中...';
        
        // 显示进度条
        if (!progressElement) {
            const progressDiv = document.createElement('div');
            progressDiv.className = 'file-item-progress mt-2';
            progressDiv.innerHTML = `
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: 100%"></div>
                </div>
            `;
            fileItem.appendChild(progressDiv);
        }
        
        // 重新解析
        await parseFile(fileId, fileType);
    }
}

// 显示文件详情
function showFileDetails(fileId) {
    const file = uploadedFiles[fileId];
    if (!file) return;
    
    const modal = new bootstrap.Modal(document.getElementById('fileModal'));
    const detailsContainer = document.getElementById('file-details');
    
    let statusBadge = '';
    let statusText = '';
    
    switch (file.status) {
        case 'parsed':
            statusBadge = 'bg-success';
            statusText = '已解析';
            break;
        case 'parsing':
            statusBadge = 'bg-primary';
            statusText = '解析中';
            break;
        case 'error':
            statusBadge = 'bg-danger';
            statusText = '解析失败';
            break;
        default:
            statusBadge = 'bg-warning';
            statusText = '已上传';
    }
    
    let detailsHTML = `
        <div class="mb-3">
            <strong>文件ID:</strong> <code>${file.file_id}</code>
        </div>
        <div class="mb-3">
            <strong>文件名:</strong> ${file.originalName || file.filename}
        </div>
        <div class="mb-3">
            <strong>类型:</strong> ${getFileTypeName(file.type)}
        </div>
        <div class="mb-3">
            <strong>文件大小:</strong> ${file.fileSize ? formatFileSize(file.fileSize) : '未知'}
        </div>
        <div class="mb-3">
            <strong>上传时间:</strong> ${file.uploadTime}
        </div>
        <div class="mb-3">
            <strong>状态:</strong> 
            <span class="badge ${statusBadge}">${statusText}</span>
        </div>
    `;
    
    // 显示错误信息
    if (file.status === 'error' && file.error_message) {
        detailsHTML += `
            <div class="mb-3">
                <strong>错误信息:</strong>
                <div class="alert alert-danger mt-2">
                    <div>${file.error_message}</div>
                    ${file.error_details ? `<div class="mt-2"><small>${file.error_details}</small></div>` : ''}
                </div>
            </div>
        `;
    }
    
    // 显示解析结果
    if (file.data) {
        let dataPreview = '';
        if (Array.isArray(file.data)) {
            dataPreview = `解析到 ${file.data.length} 条记录`;
            if (file.data.length > 0) {
                dataPreview += `\n\n示例记录:\n${JSON.stringify(file.data[0], null, 2)}`;
            }
        } else if (typeof file.data === 'object') {
            dataPreview = JSON.stringify(file.data, null, 2);
        } else {
            dataPreview = String(file.data);
        }
        
        detailsHTML += `
            <div class="mb-3">
                <strong>解析结果:</strong>
                <div class="mt-2">
                    <div class="bg-light p-2 rounded" style="max-height: 300px; overflow-y: auto;">
                        <pre>${dataPreview}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    // 添加调试信息
    detailsHTML += `
        <div class="mb-3">
            <strong>调试信息:</strong>
            <button class="btn btn-sm btn-outline-secondary ms-2" onclick="toggleDebugInfo('${fileId}')">
                <i class="bi bi-code-square"></i> 显示/隐藏
            </button>
            <div id="debug-info-${fileId}" class="mt-2" style="display: none;">
                <div class="bg-dark text-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">
                    <pre>${JSON.stringify(file, null, 2)}</pre>
                </div>
            </div>
        </div>
    `;
    
    detailsContainer.innerHTML = detailsHTML;
    modal.show();
}

// 切换调试信息显示
function toggleDebugInfo(fileId) {
    const debugInfo = document.getElementById(`debug-info-${fileId}`);
    if (debugInfo) {
        debugInfo.style.display = debugInfo.style.display === 'none' ? 'block' : 'none';
    }
}

// 删除文件
async function deleteFile(fileId) {
    if (!confirm('确定要删除这个文件吗？')) return;
    
    try {
        console.log(`开始删除文件: ${fileId}`);
        
        // 先获取文件类型，因为删除后uploadedFiles[fileId]就不存在了
        const fileType = uploadedFiles[fileId]?.type;
        const fileName = uploadedFiles[fileId]?.filename;
        
        if (!fileType) {
            console.error('无法确定文件类型:', fileId);
            addLogEntry('删除失败: 无法确定文件类型', 'error');
            return;
        }
        
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`删除失败: ${response.statusText}`);
        }
        
        // 删除文件记录
        delete uploadedFiles[fileId];
        
        addLogEntry(`文件删除成功: ${fileName}`, 'success');
        updateUploadedFilesList();
        updateGenerateButton();
        
        // 重置对应的上传区域
        const uploadArea = document.getElementById(`${fileType}-upload-area`);
        if (uploadArea) {
            console.log(`重置上传区域: ${fileType}-upload-area`);
            uploadArea.classList.remove('uploaded');
            
            const placeholder = uploadArea.querySelector('.upload-placeholder');
            const progressDiv = uploadArea.querySelector('.upload-progress');
            const fileInput = document.getElementById(`${fileType}-file`);
            
            // 重置占位符内容
            if (placeholder) {
                placeholder.innerHTML = `
                    <i class="bi bi-cloud-upload display-4 text-muted"></i>
                    <p class="mt-2">拖拽文件到此处或点击选择</p>
                    <button class="btn btn-outline-primary" onclick="triggerFileSelect('${fileType}')">
                        选择文件
                    </button>
                `;
                placeholder.classList.remove('d-none');
            }
            
            // 隐藏进度条
            if (progressDiv) {
                progressDiv.classList.add('d-none');
                const progressBar = progressDiv.querySelector('.progress-bar');
                if (progressBar) {
                    progressBar.style.width = '0%';
                }
            }
            
            // 重置文件输入
            if (fileInput) {
                fileInput.value = '';
            }
        } else {
            console.error(`找不到上传区域: ${fileType}-upload-area`);
        }
        
    } catch (error) {
        console.error('删除文件错误:', error);
        addLogEntry(`删除失败: ${error.message}`, 'error');
    }
}

// 清空所有文件
function clearAllFiles() {
    if (!confirm('确定要清空所有上传的文件吗？')) return;
    
    Object.keys(uploadedFiles).forEach(fileId => {
        deleteFile(fileId);
    });
}

// 更新生成按钮状态
function updateGenerateButton() {
    const generateBtn = document.getElementById('generate-btn');
    const hasSchedule = Object.values(uploadedFiles).some(file => file.type === 'schedule' && file.status === 'parsed');
    
    generateBtn.disabled = !hasSchedule;
    
    if (hasSchedule) {
        generateBtn.innerHTML = '<i class="bi bi-magic"></i> 开始生成教案';
    } else {
        generateBtn.innerHTML = '<i class="bi bi-magic"></i> 请先上传并解析教学进度表';
    }
}

// 开始生成教案
async function startGeneration() {
    console.log('=== startGeneration 被调用 ===');
    
    // 检查是否已有活动任务
    if (currentTaskId) {
        const taskStatus = await getTaskStatus(currentTaskId);
        if (taskStatus && ['running', 'pending', 'paused'].includes(taskStatus.status)) {
            addLogEntry('已有活动任务，请先停止当前任务', 'warning');
            return;
        }
    }
    
    const scheduleFile = Object.values(uploadedFiles).find(file => file.type === 'schedule');
    const syllabusFile = Object.values(uploadedFiles).find(file => file.type === 'syllabus');
    const templateFile = Object.values(uploadedFiles).find(file => file.type === 'template');
    const weekRange = document.getElementById('week-range').value;
    
    console.log('scheduleFile:', scheduleFile);
    console.log('syllabusFile:', syllabusFile);
    console.log('templateFile:', templateFile);
    console.log('weekRange:', weekRange);
    
    if (!scheduleFile || scheduleFile.status !== 'parsed') {
        addLogEntry('请先上传并解析教学进度表', 'error');
        return;
    }
    
    try {
        const requestData = {
            schedule_file_id: scheduleFile.file_id,
            week_range: weekRange
        };
        
        if (syllabusFile) {
            requestData.syllabus_file_id = syllabusFile.file_id;
        }
        
        if (templateFile) {
            requestData.template_file_id = templateFile.file_id;
        }
        
        console.log('生成请求数据:', requestData);
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('生成响应状态:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('生成请求失败:', response.status, errorText);
            throw new Error(`生成失败: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('生成响应结果:', result);
        
        // 确保设置currentTaskId
        currentTaskId = result.task_id;
        console.log('设置 currentTaskId:', currentTaskId);
        
        // 验证任务ID是否有效
        if (!currentTaskId) {
            throw new Error('未能获取有效的任务ID');
        }
        
        addLogEntry(`教案生成任务已启动 (任务ID: ${currentTaskId})`, 'success');
        updateStatus('正在生成教案...', 'running');
        
        // 显示进度容器
        showProgressContainer();
        
        // 立即检查任务状态
        setTimeout(() => {
            updateTaskStatus();
        }, 1000);
        
    } catch (error) {
        console.error('生成请求异常:', error);
        addLogEntry(`生成失败: ${error.message}`, 'error');
        currentTaskId = null; // 重置任务ID
    }
}

// 显示进度容器
function showProgressContainer() {
    console.log('=== showProgressContainer 被调用 ===');
    const container = document.getElementById('progress-container');
    console.log('progress-container 元素:', container);
    
    if (!container) {
        console.error('找不到 progress-container 元素');
        return;
    }
    
    container.innerHTML = `
        <div class="progress-container">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span id="progress-message">准备开始生成...</span>
                <span id="progress-percentage">0%</span>
            </div>
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     id="progress-bar" 
                     role="progressbar" 
                     style="width: 0%">
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted" id="progress-current">等待开始...</small>
            </div>
            <div class="mt-2">
                <small class="text-info">教案正在生成中，请耐心等待...</small>
            </div>
        </div>
    `;
}

// 更新进度
function updateProgress(data) {
    console.log('=== updateProgress 被调用 ===');
    console.log('进度数据:', data);
    
    const progressBar = document.getElementById('progress-bar');
    const progressMessage = document.getElementById('progress-message');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressCurrent = document.getElementById('progress-current');
    
    console.log('progress-bar 元素:', progressBar);
    console.log('progress-message 元素:', progressMessage);
    
    // 确保任务ID匹配
    if (data.task_id && data.task_id !== currentTaskId) {
        console.log(`任务ID不匹配: ${data.task_id} != ${currentTaskId}`);
        return;
    }
    
    // 更新进度条和消息
    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
    }
    
    if (progressMessage) {
        progressMessage.textContent = data.message;
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${data.progress}%`;
    }
    
    if (progressCurrent) {
        progressCurrent.textContent = data.current || '';
    }
    
    // 添加日志条目
    addLogEntry(data.message);
    
    // 根据状态更新UI
    switch (data.status) {
        case 'completed':
            updateStatus('生成完成', 'success');
            loadResults();
            // 重置任务ID
            currentTaskId = null;
            break;
            
        case 'failed':
            updateStatus('生成失败', 'error');
            addLogEntry(`错误: ${data.error}`, 'error');
            // 重置任务ID
            currentTaskId = null;
            break;
            
        case 'running':
            updateStatus('正在生成教案...', 'running');
            break;
            
        default:
            console.warn('未知的任务状态:', data.status);
            break;
    }
}







// 加载生成结果
async function loadResults() {
    try {
        const response = await fetch('/api/generate/results');
        const result = await response.json();
        
        if (result.results && result.results.length > 0) {
            displayResults(result.results);
        }
    } catch (error) {
        addLogEntry(`加载结果失败: ${error.message}`, 'error');
    }
}

// 显示结果
function displayResults(results) {
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item fade-in';
        
        const fileSize = (result.size / 1024).toFixed(2);
        const createdDate = new Date(result.created * 1000).toLocaleString();
        
        resultItem.innerHTML = `
            <div class="result-item-header">
                <div class="result-item-title">
                    <i class="bi bi-file-earmark-word text-primary"></i>
                    ${result.filename}
                </div>
                <div class="result-item-actions">
                    <a href="/api/download/${result.filename}" class="btn btn-sm btn-primary" download>
                        <i class="bi bi-download"></i>
                        下载
                    </a>
                </div>
            </div>
            <div class="result-item-info">
                <div>大小: ${fileSize} KB</div>
                <div>创建时间: ${createdDate}</div>
            </div>
        `;
        
        resultsContainer.appendChild(resultItem);
    });
    
    // 滚动到结果区域
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// 更新状态指示器
function updateStatus(message, type) {
    const indicator = document.getElementById('status-indicator');
    const iconClass = {
        'success': 'bi-circle-fill text-success',
        'warning': 'bi-circle-fill text-warning',
        'error': 'bi-circle-fill text-danger',
        'running': 'bi-circle-fill text-primary'
    };
    
    indicator.innerHTML = `
        <i class="bi ${iconClass[type]}"></i>
        ${message}
    `;
}

// 添加日志条目
function addLogEntry(message, type = 'info') {
    const container = document.getElementById('log-container');
    const entry = document.createElement('div');
    entry.className = 'log-entry fade-in';
    
    const timestamp = new Date().toLocaleTimeString();
    const messageClass = type ? `text-${type}` : '';
    
    entry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-message ${messageClass}">${message}</span>
    `;
    
    container.appendChild(entry);
    
    // 自动滚动到底部
    container.scrollTop = container.scrollHeight;
    
    // 限制日志条目数量
    const entries = container.querySelectorAll('.log-entry');
    if (entries.length > 100) {
        entries[0].remove();
    }
}

// 加载已上传文件
async function loadUploadedFiles() {
    try {
        const response = await fetch('/api/files');
        const result = await response.json();
        
        if (result.files) {
            uploadedFiles = result.files;
            updateUploadedFilesList();
        }
    } catch (error) {
        addLogEntry(`加载文件列表失败: ${error.message}`, 'error');
    }
}

// 安全的文件选择按钮点击函数
function triggerFileSelect(fileType) {
    try {
        console.log(`触发文件选择: ${fileType}`);
        
        const fileInput = document.getElementById(`${fileType}-file`);
        if (!fileInput) {
            console.error(`找不到文件输入元素: ${fileType}-file`);
            addLogEntry(`文件选择失败: 找不到文件输入控件`, 'error');
            return;
        }
        
        // 检查元素是否可用
        if (fileInput.disabled) {
            console.error(`文件输入元素被禁用: ${fileType}-file`);
            addLogEntry(`文件选择失败: 文件输入控件被禁用`, 'error');
            return;
        }
        
        // 触发点击事件
        fileInput.click();
        
    } catch (error) {
        console.error('触发文件选择错误:', error);
        addLogEntry(`文件选择失败: ${error.message}`, 'error');
    }
}

// 获取文件类型名称
function getFileTypeName(type) {
    const typeNames = {
        'schedule': '教学进度表',
        'syllabus': '教学大纲',
        'template': '教案模板'
    };
    
    return typeNames[type] || type;
}

// 获取任务状态
async function getTaskStatus(taskId) {
    if (!taskId) {
        console.error('getTaskStatus: taskId 为空');
        return null;
    }
    
    console.log(`获取任务状态: ${taskId}`);
    
    try {
        const response = await fetch(`/api/generate/status/${taskId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        console.log(`任务状态响应: ${response.status}`);
        
        if (response.ok) {
            const status = await response.json();
            console.log('任务状态:', status);
            return status;
        } else {
            console.error('获取任务状态失败:', response.status);
            const errorText = await response.text();
            console.error('错误详情:', errorText);
            return null;
        }
    } catch (error) {
        console.error('获取任务状态异常:', error);
        return null;
    }
}

// 更新任务状态
async function updateTaskStatus() {
    if (!currentTaskId) return;
    
    const taskStatus = await getTaskStatus(currentTaskId);
    if (taskStatus) {
        // 更新UI状态
        updateProgress(taskStatus);
    }
}

// 检查服务器连接状态
async function checkServerConnection() {
    console.log('=== 检查服务器连接状态 ===');
    
    try {
        const response = await fetch('/api/files', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            console.log('✓ 服务器连接正常');
            addLogEntry('服务器连接正常', 'success');
        } else {
            console.error('✗ 服务器响应异常:', response.status);
            addLogEntry(`服务器响应异常: ${response.status} ${response.statusText}`, 'error');
        }
    } catch (error) {
        console.error('✗ 无法连接到服务器:', error);
        addLogEntry(`无法连接到服务器: ${error.message}`, 'error');
        
        // 检查常见问题
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            addLogEntry('提示: 请检查服务器是否正在运行，或刷新页面重试', 'warning');
        }
    }
}



// 增强的任务状态检查
async function enhancedTaskStatusCheck(taskId) {
    if (!taskId) {
        console.error('enhancedTaskStatusCheck: taskId 为空');
        return null;
    }
    
    console.log(`=== 增强任务状态检查: ${taskId} ===`);
    
    try {
        const response = await fetch(`/api/generate/status/${taskId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        console.log(`任务状态响应: ${response.status}`);
        
        if (response.ok) {
            const status = await response.json();
            console.log('任务状态详情:', status);
            
            // 添加状态检查日志
            addLogEntry(`任务状态检查: ${status.status} (进度: ${status.progress || 0}%)`, 'info');
            
            return status;
        } else {
            console.error('获取任务状态失败:', response.status);
            const errorText = await response.text();
            console.error('错误详情:', errorText);
            addLogEntry(`任务状态检查失败: ${response.status} ${response.statusText}`, 'error');
            return null;
        }
    } catch (error) {
        console.error('获取任务状态异常:', error);
        addLogEntry(`任务状态检查异常: ${error.message}`, 'error');
        return null;
    }
}

// 添加全局错误处理
window.addEventListener('error', function(event) {
    console.error('全局错误:', event.error);
    addLogEntry(`页面错误: ${event.error.message}`, 'error');
});

// 添加未处理的Promise拒绝处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('未处理的Promise拒绝:', event.reason);
    addLogEntry(`未处理的异步错误: ${event.reason}`, 'error');
});

// 添加调试快捷键
document.addEventListener('keydown', function(event) {
    // Ctrl+Shift+S: 检查任务状态
    if (event.ctrlKey && event.shiftKey && event.key === 'S') {
        event.preventDefault();
        if (currentTaskId) {
            enhancedTaskStatusCheck(currentTaskId);
        } else {
            addLogEntry('没有活动的任务需要检查', 'warning');
        }
    }
});