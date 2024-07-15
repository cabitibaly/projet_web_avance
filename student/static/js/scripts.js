const nav = document.getElementById('nav');
const menu = document.getElementById('menu-bar');

menu.addEventListener('click', () => {
    menu.classList.toggle('fa-times');
    nav.classList.toggle('max-585:hidden');
    console.log("click")
})