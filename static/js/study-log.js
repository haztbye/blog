/* 加密日志：本地解密 + 渲染（密码只在浏览器里用，不发送到任何地方）
   密文从 /study-log.json 读取（fetch 避开模板转义），加密参数与
   tools/study-log/encrypt_log.py 保持一致：PBKDF2-SHA256 + AES-256-GCM */
(function () {
    var root = document.getElementById('study-log');
    if (!root || root.dataset.bound === '1') { return; }
    root.dataset.bound = '1';
    root.dataset.js = 'start';

    var teaser = document.getElementById('study-log-teaser');
    var unlocked = document.getElementById('study-log-unlocked');
    var content = document.getElementById('study-log-content');
    var form = document.getElementById('study-log-form');
    var input = document.getElementById('study-log-pass');
    var errEl = document.getElementById('study-log-error');
    var lockBtn = document.getElementById('study-log-lock-btn');
    if (!teaser || !unlocked || !content || !form) { root.dataset.js = 'missing-nodes'; return; }
    root.dataset.js = 'bound';

    var AAD = 'huanhe-study-log';
    var SESSION_KEY = 'study-log-key';
    var meta = null;

    function showError(msg) {
        if (!errEl) { return; }
        errEl.textContent = msg;
        errEl.hidden = false;
    }

    function b64ToBytes(b64) {
        var bin = window.atob(b64);
        var out = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) { out[i] = bin.charCodeAt(i); }
        return out;
    }

    function ensureMarked() {
        return new Promise(function (resolve) {
            if (window.marked) { return resolve(true); }
            var s = document.createElement('script');
            s.src = '/js/vendor/marked.min.js';
            s.onload = function () { resolve(!!window.marked); };
            s.onerror = function () { resolve(false); };
            document.head.appendChild(s);
        });
    }

    function plainFallback(md) {
        return md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\n{2,}/g, '</p><p>').replace(/\n/g, '<br>');
    }

    function decrypt(pass) {
        if (!window.crypto || !window.crypto.subtle) {
            return Promise.reject(new Error('no-subtle'));
        }
        var enc = new TextEncoder();
        return window.crypto.subtle
            .importKey('raw', enc.encode(pass), 'PBKDF2', false, ['deriveKey'])
            .then(function (baseKey) {
                return window.crypto.subtle.deriveKey(
                    {
                        name: 'PBKDF2',
                        salt: b64ToBytes(meta.salt),
                        iterations: meta.iterations || 210000,
                        hash: 'SHA-256'
                    },
                    baseKey,
                    { name: 'AES-GCM', length: 256 },
                    false,
                    ['decrypt']
                );
            })
            .then(function (key) {
                return window.crypto.subtle.decrypt(
                    { name: 'AES-GCM', iv: b64ToBytes(meta.iv), additionalData: enc.encode(AAD) },
                    key,
                    b64ToBytes(meta.ct)
                );
            })
            .then(function (buf) { return new TextDecoder().decode(buf); });
    }

    function render(md) {
        return ensureMarked().then(function (ok) {
            content.innerHTML = ok ? window.marked.parse(md) : '<p>' + plainFallback(md) + '</p>';
            teaser.hidden = true;
            unlocked.hidden = false;
            if (errEl) { errEl.hidden = true; }
        });
    }

    function unlock(pass, remember) {
        return decrypt(pass).then(function (md) {
            if (remember !== false) {
                try { sessionStorage.setItem(SESSION_KEY, pass); } catch (e) { }
            }
            return render(md);
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!meta) { showError('密文还没加载好，稍后再试'); return; }
        var pass = input.value;
        if (!pass) { showError('先输入密码'); return; }
        unlock(pass).catch(function (err) {
            showError(err && err.message === 'no-subtle'
                ? '当前环境不支持本地解密（请用 HTTPS 打开本站）'
                : '密码不对，再试一次');
        });
    });

    if (lockBtn) {
        lockBtn.addEventListener('click', function () {
            try { sessionStorage.removeItem(SESSION_KEY); } catch (e) { }
            content.innerHTML = '';
            unlocked.hidden = true;
            teaser.hidden = false;
            if (input) { input.value = ''; }
            if (errEl) { errEl.hidden = true; }
        });
    }

    /* 取密文（带版本号避免缓存），然后尝试自动解锁 */
    var version = root.getAttribute('data-updated') || '';
    fetch('/study-log.json' + (version ? '?v=' + encodeURIComponent(version) : ''), {
        credentials: 'same-origin'
    })
        .then(function (resp) {
            if (!resp.ok) { throw new Error('HTTP ' + resp.status); }
            return resp.json();
        })
        .then(function (data) {
            meta = data;
            if (!meta || !meta.ct) { root.dataset.js = 'meta-empty'; throw new Error('empty'); }
            root.dataset.js = 'meta-ok';
            var saved = null;
            try { saved = sessionStorage.getItem(SESSION_KEY); } catch (e) { }
            if (saved) {
                unlock(saved, false).catch(function () {
                    try { sessionStorage.removeItem(SESSION_KEY); } catch (e) { }
                });
            }
        })
        .catch(function () {
            root.dataset.js = 'meta-fail';
            showError('密文加载失败，刷新页面再试');
        });
}());