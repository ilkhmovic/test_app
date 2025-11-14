// DOM yuklanganda
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sayt yuklandi');
    
    // Form yuborishni boshqarish
    const loginForm = document.querySelector('.login-container form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Yuklanmoqda...';
                
                // 3 soniyadan so'ng qayta faollashtirish
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Login';
                }, 3000);
            }
        });
    }
    
    // Navbar menyusi (mobil uchun)
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarContent = document.querySelector('#navbarSupportedContent');
            if (navbarContent) {
                navbarContent.classList.toggle('show');
            }
        });
    }
    
    // Parolni ko'rsatish/yashirish
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        // Parol maydoni bo'yicha qo'shimcha tugma yaratish
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.textContent = '👁';
        toggleBtn.style.background = 'none';
        toggleBtn.style.border = 'none';
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.cursor = 'pointer';
        
        const inputGroup = passwordInput.parentElement;
        inputGroup.style.position = 'relative';
        inputGroup.appendChild(toggleBtn);
        
        toggleBtn.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = '🔒';
            } else {
                passwordInput.type = 'password';
                this.textContent = '👁';
            }
        });
    }
});

// Logout funksiyasi
function handleLogout() {
    if (confirm('Chiqishni xohlaysizmi?')) {
        window.location.href = '/logout';
    }
}

// Logout tugmasini topib, event qo'shamiz
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.querySelector('a[href*="logout"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleLogout();
        });
    }
});