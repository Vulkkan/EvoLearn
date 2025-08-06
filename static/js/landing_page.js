const hamburger = document.getElementById('hamburger');

const navMenu = document.getElementById('navMenu');

const navLinks = document.querySelectorAll('.nav a');

hamburger.addEventListener('click', () => {
navMenu.classList.toggle('open');
hamburger.classList.toggle('active');
});

navLinks.forEach(link => {
link.addEventListener('click', () => {
    navMenu.classList.remove('open');
    hamburger.classList.remove('active');
});
});

// out-tema

const wrapper = document.getElementById('teamWrapper');
const leftArrow = document.querySelector('.arrow.left');
const rightArrow = document.querySelector('.arrow.right');

function scrollTeam(direction) {
const scrollAmount = 280;
wrapper.scrollBy({
left: scrollAmount * direction,
behavior: 'smooth'
});
}

function updateArrowVisibility() {
const scrollLeft = wrapper.scrollLeft;
const maxScrollLeft = wrapper.scrollWidth - wrapper.clientWidth;

// Hide/show arrows
leftArrow.style.display = scrollLeft > 10 ? 'flex' : 'none';
rightArrow.style.display = scrollLeft < maxScrollLeft - 10 ? 'flex' : 'none';
}

// Check on load and scroll
wrapper.addEventListener('scroll', updateArrowVisibility);
window.addEventListener('load', updateArrowVisibility);