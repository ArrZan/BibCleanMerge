document.querySelector('.sidebar-btn').addEventListener('click', function() {
    this.parentNode.classList.toggle('hidden-sb');
})

document.querySelector('.blur-section').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.add('hidden-nv');
    document.querySelector('.blur-section').classList.add('hidden-b');
})

document.querySelector('.navbar-btn').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.remove('hidden-sb');
    document.querySelector('.sidebar').classList.remove('hidden-nv');
    document.querySelector('.blur-section').classList.remove('hidden-b');
})