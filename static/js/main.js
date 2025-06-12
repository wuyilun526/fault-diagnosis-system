// API endpoints
const API = {
    diagnosis: {
        analyze: '/api/diagnosis/cases/analyze/'
    },
    categories: {
        list: '/api/knowledge/categories/',
        create: '/api/knowledge/categories/'
    },
    knowledge: {
        list: '/api/knowledge/knowledge/',
        create: '/api/knowledge/knowledge/'
    }
};

// 初始化Bootstrap tabs
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有tabs
    const triggerTabList = document.querySelectorAll('[data-bs-toggle="tab"]');
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', event => {
            event.preventDefault();
            tabTrigger.show();
        });
    });

    // 加载初始数据
    loadCategories();
    loadKnowledge();
});

// 提交诊断表单
$('#diagnosisForm').on('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        alert_info: $('#alertInfo').val(),
        metrics_info: $('#metricsInfo').val(),
        log_info: $('#logInfo').val()
    };

    $.ajax({
        url: API.diagnosis.analyze,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            // 显示诊断结果
            $('#diagnosisResult').html(`
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">诊断结果</h5>
                        <p><strong>故障分类：</strong>${response.category}</p>
                        <p><strong>分析结果：</strong>${response.analysis}</p>
                        <p><strong>解决方案：</strong>${response.solution}</p>
                    </div>
                </div>
            `);

            // 显示参考案例
            if (response.reference_cases && response.reference_cases.length > 0) {
                let referenceCasesHtml = '<div class="mt-4"><h5>参考案例</h5>';
                response.reference_cases.forEach(function(referenceCase) {
                    referenceCasesHtml += `
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6 class="card-title">${referenceCase.title} <span class="badge bg-info">相似度: ${referenceCase.similarity}</span></h6>
                                <p class="card-text"><strong>故障分类：</strong>${referenceCase.category}</p>
                                <p class="card-text"><strong>症状描述：</strong>${referenceCase.symptoms}</p>
                                <p class="card-text"><strong>解决方案：</strong>${referenceCase.solution}</p>
                            </div>
                        </div>
                    `;
                });
                referenceCasesHtml += '</div>';
                $('#diagnosisResult').append(referenceCasesHtml);
            }

            // 清空表单
            $('#diagnosisForm')[0].reset();
        },
        error: function(xhr) {
            alert('诊断失败：' + (xhr.responseJSON?.error || '未知错误'));
        }
    });
});

// 加载分类列表
function loadCategories() {
    $.get(API.categories.list, function(data) {
        const categoryList = $('#categoryList');
        categoryList.empty();
        data.forEach(function(category) {
            categoryList.append(`
                <div class="list-group-item">
                    <h5>${category.name}</h5>
                    <p>${category.description || ''}</p>
                </div>
            `);
        });
    });
}

// 加载知识列表
function loadKnowledge() {
    $.get(API.knowledge.list, function(data) {
        const knowledgeList = $('#knowledgeList');
        knowledgeList.empty();
        data.forEach(function(knowledge) {
            knowledgeList.append(`
                <div class="list-group-item">
                    <h5>${knowledge.title}</h5>
                    <p><strong>分类：</strong>${knowledge.category_name}</p>
                    <p><strong>症状：</strong>${knowledge.symptoms}</p>
                    <p><strong>解决方案：</strong>${knowledge.solution}</p>
                </div>
            `);
        });
    });
}

// 保存分类
$('#saveCategory').on('click', function() {
    const data = {
        name: $('#categoryName').val(),
        description: $('#categoryDescription').val()
    };

    $.ajax({
        url: API.categories.create,
        method: 'POST',
        data: data,
        success: function() {
            $('#categoryModal').modal('hide');
            loadCategories();
            $('#categoryForm')[0].reset();
        },
        error: function(xhr) {
            alert('保存失败: ' + (xhr.responseJSON?.error || '未知错误'));
        }
    });
});

// 保存知识
$('#saveKnowledge').on('click', function() {
    const data = {
        category: $('#knowledgeCategory').val(),
        title: $('#knowledgeTitle').val(),
        symptoms: $('#knowledgeSymptoms').val(),
        solution: $('#knowledgeSolution').val()
    };

    $.ajax({
        url: API.knowledge.create,
        method: 'POST',
        data: data,
        success: function() {
            $('#knowledgeModal').modal('hide');
            loadKnowledge();
            $('#knowledgeForm')[0].reset();
        },
        error: function(xhr) {
            alert('保存失败: ' + (xhr.responseJSON?.error || '未知错误'));
        }
    });
});

// 页面加载完成后执行
$(document).ready(function() {
    // 加载初始数据
    loadCategories();
    loadKnowledge();

    // 加载分类下拉列表
    $.get(API.categories.list, function(data) {
        const categorySelect = $('#knowledgeCategory');
        categorySelect.empty();
        data.forEach(function(category) {
            categorySelect.append(`<option value="${category.id}">${category.name}</option>`);
        });
    });
});

// 显示诊断结果
function displayDiagnosisResult(result) {
    document.getElementById('resultCategory').textContent = result.category_details?.name || '未分类';
    document.getElementById('resultAnalysis').textContent = result.analysis_result;
    document.getElementById('resultSolution').textContent = result.solution;
    document.getElementById('diagnosisResult').style.display = 'block';
}

// 更新知识库分类选择框
function updateKnowledgeCategorySelect(categories) {
    const select = document.getElementById('knowledgeCategory');
    select.innerHTML = categories.map(category => 
        `<option value="${category.id}">${category.name}</option>`
    ).join('');
}

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 