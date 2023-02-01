export function onResizeMovable() {
    let absheight = $(window).height();
    if (!this._restHeight) {
        let height = $('.div-page-container.active').innerHeight();
        let space = this.find('.footer-menu-dummy').innerHeight();
        this._restHeight = absheight - height + space;
    }


    this.find('.main-view-flex-container').css({'min-height': `${100 / absheight * (absheight - this._restHeight)}vh`});
}


export function getResizerEvents() {
    let $elem = null

    function toggleMenu() {
        if ($elem.hasClass('active')) {
            $elem.removeClass('active');
            window.removeEventListener("click", toggleMenu);
        } else {
            $elem.addClass('active');
            setTimeout(() => {
                window.addEventListener("click", toggleMenu);

            }, 10);
        }
    }

    return {
        '.resizer': {
            'mousedown': handleResizerEvents
        },
        '.collapse-btn': {
            'click': function () {
                if ($elem === null) {
                    $elem = this.find('#flex-elem-left');
                }
                toggleMenu();
            }
        }
    }
}

function manageResize(md, sizeProp, posProp) {
    let r = md.target;

    let prev = r.previousElementSibling;
    let next = r.nextElementSibling;
    if (!prev || !next) {
        return;
    }

    md.preventDefault();

    let prevSize = prev[sizeProp];
    let nextSize = next[sizeProp];
    let sumSize = prevSize + nextSize;
    let prevGrow = Number(prev.style.flexGrow);
    let nextGrow = Number(next.style.flexGrow);
    let sumGrow = prevGrow + nextGrow;
    let lastPos = md[posProp];

    function onMouseMove(mm) {
        let pos = mm[posProp];
        let d = pos - lastPos;
        prevSize += d;
        nextSize -= d;
        if (prevSize < 0) {
            nextSize += prevSize;
            pos -= prevSize;
            prevSize = 0;
        }
        if (nextSize < 0) {
            prevSize += nextSize;
            pos += nextSize;
            nextSize = 0;
        }

        let prevGrowNew = sumGrow * (prevSize / sumSize);
        let nextGrowNew = sumGrow * (nextSize / sumSize);

        prev.style.flexGrow = prevGrowNew;
        next.style.flexGrow = nextGrowNew;

        lastPos = pos;

        $(window).trigger('resize');
    }

    function onMouseUp(mu) {
        // Change cursor to signal a state's change: stop resizing.
        const html = document.querySelector('html');
        html.style.cursor = 'default';

        if (posProp === 'pageX') {
            r.style.cursor = 'ew-resize';
        } else {
            r.style.cursor = 'ns-resize';
        }

        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
}


function handleResizerEvents(target, ev) {
    const html = document.querySelector('html');

    if (target.nodeType !== 1 || !target.classList.contains("movable-flex-resizer")) {
        return;
    }
    let parent = target.parentNode;
    let h = parent.classList.contains("h");
    if (h) {
        // Change cursor to signal a state's change: begin resizing on H.
        target.style.cursor = 'col-resize';
        html.style.cursor = 'col-resize'; // avoid cursor's flickering

        // use offsetWidth versus scrollWidth to avoid splitter's jump on resize when content overflow.
        manageResize(ev, "offsetWidth", "pageX");

    }
}