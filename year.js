const year = new URLSearchParams(window.location.search).get('y');

fetch('photos.json')
    .then(response => response.json())
    .then(data => {
        const photos = data[year] || [];
        const gallery = document.getElementById('gallery');
        const lightbox = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightbox-img');
        const lightboxCaption = document.getElementById('lightbox-caption');
        const prevBtn = document.getElementById('prev');
        const nextBtn = document.getElementById('next');

        document.querySelector('header h1').textContent = year;

        let currentIndex = 0;

        /* 显示指定索引的照片 */
        function showPhoto(index) {
            currentIndex = (index + photos.length) % photos.length; /* 循环翻页 */
            const photo = photos[currentIndex];
            lightboxImg.src = photo.src;
            lightboxCaption.textContent = photo.caption || '';
        }

        /* 打开灯箱 */
        function openLightbox(index) {
            showPhoto(index);
            lightbox.classList.remove('hidden');
        }

        /* 关闭灯箱 */
        function closeLightbox() {
            lightbox.classList.add('hidden');
            lightboxImg.src = '';
            lightboxCaption.textContent = '';
        }

        photos.forEach((photo, index) => {
            const img = document.createElement('img');
            img.src = photo.thumb;
            img.alt = photo.caption;
            img.addEventListener('click', () => openLightbox(index));
            gallery.appendChild(img);
        });

        /* 点击遮罩背景关闭（点箭头或图片不关闭） */
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });

        /* 箭头按钮：阻止冒泡防止触发关闭 */
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showPhoto(currentIndex - 1);
        });

        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showPhoto(currentIndex + 1);
        });

        /* 键盘控制 */
        document.addEventListener('keydown', (e) => {
            if (lightbox.classList.contains('hidden')) return;
            if (e.key === 'ArrowLeft')  showPhoto(currentIndex - 1);
            if (e.key === 'ArrowRight') showPhoto(currentIndex + 1);
            if (e.key === 'Escape')     closeLightbox();
        });
    });
