// 表单验证JavaScript
function validateForm(form) {
  const inputs = form.querySelectorAll('input[required], input[name]');
  let isValid = true;
  
  inputs.forEach(input => {
    if (input.type === 'text' || input.type === 'password') {
      if (!input.value || input.value.trim() === '') {
        showError(input, getFieldLabel(input.name) + '不能为空！');
        isValid = false;
      } else {
        clearError(input);
      }
    }
  });
  
  return isValid;
}

function getFieldLabel(fieldName) {
  const labels = {
    'username': '用户名称',
    'phone_number': '用户号码',
    'password': '用户密码'
  };
  return labels[fieldName] || fieldName;
}

function showError(input, message) {
  clearError(input);
  
  input.style.borderColor = '#dc3545';
  input.style.backgroundColor = '#fff5f5';
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.style.color = '#dc3545';
  errorDiv.style.fontSize = '12px';
  errorDiv.style.marginTop = '4px';
  errorDiv.textContent = message;
  
  input.parentNode.appendChild(errorDiv);
  input.focus();
}

function clearError(input) {
  input.style.borderColor = '';
  input.style.backgroundColor = '';
  
  const errorMessage = input.parentNode.querySelector('.error-message');
  if (errorMessage) {
    errorMessage.remove();
  }
}

// 表单提交处理
function handleFormSubmit(form, event) {
  event.preventDefault();
  
  if (validateForm(form)) {
    // 显示加载状态
    const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.value = '处理中...';
    }
    
    // 提交表单
    form.submit();
  }
}

// 输入框实时验证
function setupRealTimeValidation(form) {
  const inputs = form.querySelectorAll('input[type="text"], input[type="password"]');
  
  inputs.forEach(input => {
    input.addEventListener('blur', function() {
      if (this.value.trim() === '') {
        showError(this, getFieldLabel(this.name) + '不能为空！');
      } else {
        clearError(this);
      }
    });
    
    input.addEventListener('input', function() {
      if (this.value.trim() !== '') {
        clearError(this);
      }
    });
  });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    setupRealTimeValidation(form);
    
    form.addEventListener('submit', function(event) {
      handleFormSubmit(this, event);
    });
  });
});
