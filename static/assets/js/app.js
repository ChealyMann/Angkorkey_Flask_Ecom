const PRODUCTS = [
    {
        id: '1',
        name: 'Smart Watch Pro',
        price: 299,
        category: 'accessories',
        description: 'Advanced fitness tracking with sleek design. Features heart rate monitoring, GPS, and 7-day battery life. Water resistant up to 50 meters with premium stainless steel case.',
        images: [
            'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
            'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800',
            'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800',
            'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=800'
        ]
    },
    {
        id: '2',
        name: 'Leather Backpack',
        price: 129,
        category: 'bags',
        description: 'Genuine leather with minimal aesthetic. Handcrafted from full-grain leather with padded laptop compartment.',
        images: [
            'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800',
            'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800',
            'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
            'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800'
        ]
    },
    {
        id: '3',
        name: 'Wireless Earbuds',
        price: 189,
        category: 'accessories',
        description: 'Premium audio with active noise cancellation. 24-hour battery life with charging case.',
        images: [
            'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800',
            'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800',
            'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=800',
            'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800'
        ]
    },
    {
        id: '4',
        name: 'Bronze Necklace',
        price: 249,
        category: 'jewelry',
        description: 'Handcrafted bronze pendant on chain. Vintage-inspired design with antique finish.',
        images: [
            'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800',
            'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800',
            'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800',
            'https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=800'
        ]
    },
    {
        id: '5',
        name: 'Sunglasses Premium',
        price: 159,
        category: 'accessories',
        description: 'UV400 protection with timeless frame. Polarized lenses with titanium frame.',
        images: [
            'https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800',
            'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800',
            'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800',
            'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800'
        ]
    },
    {
        id: '6',
        name: 'Ceramic Vase Set',
        price: 89,
        category: 'home',
        description: 'Modern ceramic vases for any space. Set of 3 handcrafted stoneware vases in matte finish.',
        images: [
            'https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=800',
            'https://images.unsplash.com/photo-1581783898377-1a85bf937427?w=800',
            'https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=800',
            'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=800'
        ]
    },
    {
        id: '7',
        name: 'Silk Scarf',
        price: 79,
        category: 'clothing',
        description: '100% silk with geometric pattern. Lightweight and breathable, perfect for all seasons.',
        images: [
            'https://images.unsplash.com/photo-1545173168-9f1947eebb7f?w=800',
            'https://images.unsplash.com/photo-1601924992345-5c2b5e0ab0b9?w=800',
            'https://images.unsplash.com/photo-1566217688581-b2192d5808e8?w=800',
            'https://images.unsplash.com/photo-1601924994987-69e26d5c26ce?w=800'
        ]
    },
    {
        id: '8',
        name: 'Coffee Maker Deluxe',
        price: 199,
        category: 'home',
        description: 'Automatic brewing with thermal carafe. Programmable with 12-cup capacity and keep-warm function.',
        images: [
            'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800',
            'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800',
            'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800',
            'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800'
        ]
    }
];

/* ----------------------- Utilities ----------------------- */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
const fmtPrice = v => new Intl.NumberFormat(undefined, {style: 'currency', currency: 'USD'}).format(v);

/* ----------------------- Description Popup ----------------------- */
const descPopup = $('#descPopup');
const descPopupText = $('#descPopupText');
const descCloseBtn = $('#descCloseBtn');

function openDescPopup(fullText) {
    descPopupText.textContent = fullText;
    const content = descPopup.querySelector('.bg-white');
    descPopup.classList.remove('hidden');
    descPopup.classList.add('flex');
    // Animate in
    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeDescPopup() {
    const content = descPopup.querySelector('.bg-white');
    // Animate out
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        descPopup.classList.add('hidden');
        descPopup.classList.remove('flex');
    }, 300);
}

descCloseBtn.addEventListener('click', closeDescPopup);
descPopup.addEventListener('click', (e) => {
    if (e.target === descPopup) closeDescPopup();
});

/* ----------------------- Render Products ----------------------- */
let currentFilter = 'all';
const grid = $('#productsGrid');

function cardTemplate(product, i) {
    return `
        <article class="card rounded-2xl overflow-hidden card-enter" style="animation-delay:${i * 60}ms" role="button" tabindex="0" aria-label="View ${product.name}" data-id="${product.id}">
          <div class="relative group">
            <div class="aspect-[4/5] bg-gray-100 overflow-hidden">
              <img loading="lazy" src="${product.images[0]}" alt="${product.name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"/>
            </div>
            <div class="absolute left-3 top-3 inline-flex items-center gap-1.5 bg-white/90 backdrop-blur px-2.5 py-1 rounded-full text-[11px]">
              <span class="size-1.5 rounded-full bg-emerald-500"></span> In stock
            </div>
          </div>
          <div class="p-3">
            <h3 class="text-sm font-medium truncate">${product.name}</h3>
            <div class="mt-1 flex items-center justify-between">
              <p class="text-base font-semibold text-[color:var(--accent)]">${fmtPrice(product.price)}</p>
              <button class="text-gray-400 hover:text-[color:var(--accent)]" aria-label="Quick view ${product.name}"><i class="bi bi-eye"></i></button>
            </div>
          </div>
        </article>`;
}

function render(list) {
    grid.innerHTML = list.map((p, i) => cardTemplate(p, i)).join('');
    $$('#productsGrid article').forEach(card => {
        card.addEventListener('click', () => openModal(card.dataset.id));
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openModal(card.dataset.id);
            }
        });
    });
    observeStagger();
}

function applyFilter() {
    const dataset = currentFilter === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.category === currentFilter);
    render(dataset);
}

/* ----------------------- Search ----------------------- */
const searchEl = $('#searchInput');
let searchTimer;
searchEl.addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    const q = e.target.value.trim().toLowerCase();
    searchTimer = setTimeout(() => {
        const base = currentFilter === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.category === currentFilter);
        const filtered = q ? base.filter(p => (p.name + " " + p.description).toLowerCase().includes(q)) : base;
        render(filtered);
    }, 120);
});

/* ----------------------- Category Filter ----------------------- */
$$('.chip').forEach(ch => {
    ch.addEventListener('click', () => {
        $$('.chip').forEach(c => c.dataset.active = 'false');
        ch.dataset.active = 'true';
        currentFilter = ch.dataset.category;
        applyFilter();
    });
});

/* ----------------------- Modal ----------------------- */
const modal = $('#productModal');
let lastFocus = null;

function modalTemplate(p) {
    return `
        <div class="bg-white max-w-2xl w-full rounded-2xl overflow-hidden shadow-xl" role="dialog" aria-modal="true" aria-label="${p.name}">
          <div class="relative">
            <button id="closeBtn" class="absolute top-4 right-4 bg-gray-100 hover:bg-[color:var(--accent)] hover:text-white transition-colors size-9 rounded-full grid place-items-center" aria-label="Close">
              <i class="bi bi-x-lg text-sm"></i>
            </button>
            <img id="mainImg" src="${p.images[0]}" alt="${p.name}" class="w-full h-80 object-cover"/>
          </div>
          <div class="flex gap-2 p-3 bg-gray-50 overflow-x-auto">
            ${p.images.map((src, idx) => `<img src="${src}" alt="${p.name} thumbnail ${idx + 1}" class="thumb w-16 h-16 object-cover rounded-md" ${idx === 0 ? 'aria-current="true"' : ''} data-thumb>`).join('')}
          </div>
          <div class="p-6">
            <h2 class="text-xl font-semibold mb-1">${p.name}</h2>
            <p class="text-lg font-semibold text-[color:var(--accent)] mb-3">${fmtPrice(p.price)}</p>
            
            <!-- Description trigger -->
            <div class="mb-5">
              <button id="descTrigger" class="text-[color:var(--accent)] font-medium hover:underline text-sm inline-flex items-center gap-1.5">
                <i class="bi bi-info-circle"></i>
                <span>Tap here to see desc</span>
              </button>
            </div>
            
            <div class="grid grid-cols-2 gap-3">
              <a id="msgLink" href="#" target="_blank" class="bg-black hover:bg-[color:var(--accent)] transition-colors text-white py-3 rounded-xl text-center text-sm font-medium inline-flex items-center justify-center gap-2">
                <i class="bi bi-messenger"></i><span>Message</span>
              </a>
              <a id="tgLink" href="#" target="_blank" class="bg-black hover:bg-[color:var(--accent)] transition-colors text-white py-3 rounded-xl text-center text-sm font-medium inline-flex items-center justify-center gap-2">
                <i class="bi bi-telegram"></i><span>Telegram</span>
              </a>
            </div>
          </div>
        </div>`;
}

function openModal(id) {
    const p = PRODUCTS.find(x => x.id === id);
    if (!p) return;
    lastFocus = document.activeElement;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.innerHTML = modalTemplate(p);
    document.body.style.overflow = 'hidden';

    const main = $('#mainImg', modal);
    $$('[data-thumb]', modal).forEach((thumb, idx) => {
        thumb.addEventListener('click', () => {
            main.src = p.images[idx];
            $$('[data-thumb]', modal).forEach(x => x.setAttribute('aria-current', 'false'));
            thumb.setAttribute('aria-current', 'true');
        });
    });
    $('#msgLink', modal).href = `https://m.me/yourpage?text=${encodeURIComponent('Hello, I\'m interested in ' + p.name)}`;
    $('#tgLink', modal).href = `https://t.me/yourusername?text=${encodeURIComponent('Hello, I\'m interested in ' + p.name)}`;

    const close = () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        modal.innerHTML = '';
        document.body.style.overflow = '';
        if (lastFocus) lastFocus.focus();
    }
    $('#closeBtn', modal).addEventListener('click', close);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) close();
    });
    document.addEventListener('keydown', escClose);

    function escClose(e) {
        if (e.key === 'Escape') {
            if (!descPopup.classList.contains('hidden')) {
                closeDescPopup();
            } else {
                close();
                document.removeEventListener('keydown', escClose);
            }
        }
    }

    $('#closeBtn', modal).focus();

    // Description trigger handler
    const descTrigger = $('#descTrigger', modal);
    descTrigger.addEventListener('click', () => openDescPopup(p.description));
}

/* ----------------------- Stagger on view ----------------------- */
function observeStagger() {
    const cards = $$('#productsGrid .card-enter');
    const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.style.visibility = 'visible';
                io.unobserve(e.target);
            }
        });
    }, {threshold: .06});
    cards.forEach(c => {
        c.style.visibility = 'hidden';
        io.observe(c);
    });
}

// Initial paint
applyFilter();

function toggleCart() {
    const backdrop = document.getElementById('cart-backdrop');
    const panel = document.getElementById('cart-panel');

    if (backdrop.classList.contains('hidden')) {
        // OPEN CART
        backdrop.classList.remove('hidden');
        // Small timeout allows the browser to render "display:block" before we start the fade
        setTimeout(() => {
            backdrop.classList.remove('opacity-0');
            panel.classList.remove('translate-x-full');
        }, 10);

        // Optional: Prevent body scrolling when cart is open
        document.body.style.overflow = 'hidden';
    } else {
        // CLOSE CART
        backdrop.classList.add('opacity-0');
        panel.classList.add('translate-x-full');

        // Wait for transition (300ms) before hiding
        setTimeout(() => {
            backdrop.classList.add('hidden');
            // Restore body scrolling
            document.body.style.overflow = 'auto';
        }, 300);
    }


}