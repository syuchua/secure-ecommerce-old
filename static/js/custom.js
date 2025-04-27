/**
 * 安全电商平台自定义脚本
 */

// 当文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 商品数量增减按钮
    setupQuantityButtons();

    // 延迟加载图片
    setupLazyLoading();

    // 表单验证
    setupFormValidation();

    // 图片预览
    setupImagePreview();

    // 初始化工具提示
    initializeTooltips();
});

/**
 * 设置商品数量增减按钮
 */
function setupQuantityButtons() {
    // 增加商品数量
    document.querySelectorAll('.btn-increment').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('.quantity-input');
            const max = parseInt(input.getAttribute('max') || Infinity);
            const currentValue = parseInt(input.value);

            if (currentValue < max) {
                input.value = currentValue + 1;
            }
        });
    });

    // 减少商品数量
    document.querySelectorAll('.btn-decrement').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('.quantity-input');
            const min = parseInt(input.getAttribute('min') || 1);
            const currentValue = parseInt(input.value);

            if (currentValue > min) {
                input.value = currentValue - 1;
            }
        });
    });

    // 直接输入时验证
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const min = parseInt(this.getAttribute('min') || 1);
            const max = parseInt(this.getAttribute('max') || Infinity);
            let value = parseInt(this.value) || min;

            if (value < min) value = min;
            if (value > max) value = max;

            this.value = value;
        });
    });
}

/**
 * 设置延迟加载图片
 */
function setupLazyLoading() {
    // 检查浏览器是否支持 Intersection Observer
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img.lazy');

        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(function(image) {
            imageObserver.observe(image);
        });
    } else {
        // 回退到传统方法
        const lazyImages = document.querySelectorAll('img.lazy');
        lazyImages.forEach(function(img) {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

/**
 * 设置表单验证
 */
function setupFormValidation() {
    // 获取所有需要验证的表单
    const forms = document.querySelectorAll('.needs-validation');

    // 对每个表单添加提交事件监听
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });

    // 密码强度检查
    const passwordInputs = document.querySelectorAll('input[type="password"].check-strength');

    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            // 长度检查
            if (password.length >= 8) strength += 1;

            // 包含大写字母
            if (/[A-Z]/.test(password)) strength += 1;

            // 包含小写字母
            if (/[a-z]/.test(password)) strength += 1;

            // 包含数字
            if (/[0-9]/.test(password)) strength += 1;

            // 包含特殊字符
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;

            // 显示密码强度
            const strengthBar = this.parentNode.querySelector('.password-strength');
            if (strengthBar) {
                strengthBar.className = 'password-strength progress-bar';

                // 根据强度级别设置不同的样式
                if (strength <= 2) {
                    strengthBar.classList.add('bg-danger');
                    strengthBar.textContent = '弱';
                } else if (strength <= 4) {
                    strengthBar.classList.add('bg-warning');
                    strengthBar.textContent = '中';
                } else {
                    strengthBar.classList.add('bg-success');
                    strengthBar.textContent = '强';
                }

                // 设置进度条宽度
                strengthBar.style.width = (strength * 20) + '%';
            }
        });
    });
}

/**
 * 设置图片预览
 */
function setupImagePreview() {
    const imageInputs = document.querySelectorAll('.image-input');

    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.getElementById(this.dataset.preview);

            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };

                reader.readAsDataURL(this.files[0]);
            }
        });
    });
}

/**
 * 初始化工具提示
 */
function initializeTooltips() {
    // 使用Bootstrap的工具提示
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
}

/**
 * 添加到购物车的动画效果
 * @param {HTMLElement} button 添加到购物车按钮
 */
function addToCartAnimation(button) {
    button.classList.add('btn-success');
    button.innerHTML = '<i class="fas fa-check"></i> 已添加';

    setTimeout(() => {
        button.classList.remove('btn-success');
        button.innerHTML = '<i class="fas fa-shopping-cart"></i> 加入购物车';
    }, 1500);
}

/**
 * 格式化价格显示
 * @param {number} price 价格
 * @param {string} currency 货币符号
 * @returns {string} 格式化后的价格
 */
function formatPrice(price, currency = '¥') {
    return currency + price.toFixed(2);
}

/**
 * 处理AJAX请求的错误
 * @param {Error} error 错误对象
 */
function handleAjaxError(error) {
    console.error('AJAX请求错误:', error);

    // 显示错误提示
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>请求出错!</strong> 无法完成您的请求，请稍后再试。
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
}

/**
 * 确认删除操作
 * @param {string} message 确认消息
 * @returns {boolean} 是否确认删除
 */
function confirmDelete(message = '确定要删除吗？此操作无法撤销。') {
    return confirm(message);
}