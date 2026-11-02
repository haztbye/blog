/* 首页倒计时：按日历天计算，支持「还有 N 天 / 就是今天 / 已过去 N 天」
   挂在 window.huanheCountdown 上方便测试；PJAX 换页后脚本会重新执行，幂等无副作用。 */
(function () {
    function startOfDay(d) {
        return new Date(d.getFullYear(), d.getMonth(), d.getDate());
    }

    /* 目标日期（本地零点）与「今天」的日历天差：正数=还有几天，0=就是今天，负数=过去几天 */
    function daysBetween(isoDate, now) {
        if (!isoDate) { return null; }
        var p = String(isoDate).split('-');
        if (p.length !== 3) { return null; }
        var target = new Date(+p[0], +p[1] - 1, +p[2], 0, 0, 0, 0);
        if (isNaN(target.getTime())) { return null; }
        var today = startOfDay(now || new Date());
        return Math.round((target - today) / 86400000);
    }

    function describe(days) {
        if (days === null) { return { text: '—', state: 'unknown' }; }
        if (days > 0) { return { text: '还有 ' + days + ' 天', num: days, state: 'upcoming' }; }
        if (days === 0) { return { text: '就是今天', num: 0, state: 'today' }; }
        return { text: '已过去 ' + Math.abs(days) + ' 天', num: Math.abs(days), state: 'past' };
    }

    function renderOne(el, now) {
        var days = daysBetween(el.getAttribute('data-date'), now);
        var info = describe(days);
        var value = el.querySelector('.countdown-value');
        if (value) { value.textContent = info.text; }
        el.classList.remove('is-upcoming', 'is-today', 'is-past');
        el.classList.add('is-' + info.state);
        el.setAttribute('data-days', days === null ? '' : String(days));
    }

    function renderAll(now) {
        var nodes = document.querySelectorAll('.countdown-item[data-date]');
        Array.prototype.forEach.call(nodes, function (el) { renderOne(el, now); });
    }

    if (typeof window !== 'undefined') {
        window.huanheCountdown = { daysBetween: daysBetween, describe: describe, renderAll: renderAll };
        renderAll();
        /* 跨过零点后自动更新一次（保持标签页长时间打开时不会显示过期数字） */
        if (!window.__hhCountdownTimer) {
            window.__hhCountdownTimer = window.setInterval(function () { renderAll(); }, 60 * 60 * 1000);
        }
    }
}());