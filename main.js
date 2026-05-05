fetch('photos.json')
    .then(response => response.json())
    .then(data => {
        const gallery = document.getElementById('gallery');

        /* 取出所有年份，倒序排列（最新年份在前） */
        const years = Object.keys(data).sort((a, b) => b - a);

        years.forEach(year => {
            const photos = data[year];

            /* 每个年份卡片是一个链接，点击跳转到该年的照片页 */
            const card = document.createElement('a');
            card.href = `year.html?y=${year}`;
            card.className = 'year-card';

            /* 用该年第一张照片的缩略图作为封面 */
            const cover = document.createElement('img');
            cover.src = photos[0].thumb;
            cover.alt = year;

            const label = document.createElement('span');
            label.textContent = year;

            card.appendChild(cover);
            card.appendChild(label);
            gallery.appendChild(card);
        });
    });
