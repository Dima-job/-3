const images = [
	'images/img1.avif',
	'images/img2.avif',
	'images/img3.avif',
	'images/img4.avif',
	'images/img5.avif',
]

let currentIndex = 0
const imageElement = document.getElementById('image')
const counter = document.getElementById('counter')

document.getElementById('next').addEventListener('click', () => {
	currentIndex = (currentIndex + 1) % images.length
	updateSlider()
})

document.getElementById('prev').addEventListener('click', () => {
	currentIndex = (currentIndex - 1 + images.length) % images.length
	updateSlider()
})

function updateSlider() {
	imageElement.src = images[currentIndex]
	counter.textContent = `Изображение ${currentIndex + 1} из ${images.length}`
}
