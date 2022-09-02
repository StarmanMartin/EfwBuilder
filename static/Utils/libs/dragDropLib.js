
/**
 * To make the DragDropManager work, the following rules must be maintained:
 * <ol>
 *  <li> The draggable elements must have the class 'draggable'.</li>
 *  <li> The element in which the moving is possible must have the class 'drag-ground'.</li>
 *  <li> The elements where the draggable element can be dropped on must have the class 'drop-space'</li>
 *  <li> You must add the even 'drop' to the evens object. the handler gets three arguments:
 *      <ul>
 *      <li>elm: the draggable element</li>
 *      <li>event: the drop event</li>
 *      <li>target: the drop space element</li>
 *      </ul>
 * </li>
 * <li> Add a instance variable called <b>isDDActive</b> to your controller. The Drag&Drop only works if  <b>isDDActive</b> is true.
 * <li> Add the events to your events array
 *    <p>-> this.events.unshift(ddm.generateEvents(), { ... })</p>
 * </li>
 * </ol>
 */
export class DragDropManager {

    constructor() {
        this.drag_start_timer = false;
        this.$drag_elm = false;

    }

    generateEvents() {
        let self = this
        return {
            '.draggable-layer': {
                'mousedown': function (btn, e) {
                    if (!this.isDDActive) {
                        return;
                    }
                    self.handleDragStart(btn, e, this.find.bind(this));
                },
            },
            '.drag-ground': {
                'mousemove':
                    function (btn, e) {
                        self.handleDragMove(btn, e, this.find.bind(this));
                    },
                'mouseleave':
                    function (btn, e) {
                        self.handleDragLeave(btn, e, this.find.bind(this));
                        self.handleDragEnd(btn, e, this.find.bind(this));
                    },
                'mouseup':
                    function (btn, e) {
                        self.handleDragEnd(btn, e, this.find.bind(this));
                    }
            }
        }

    }

    _blurAll() {
        let tmp = document.createElement("input");
        document.body.appendChild(tmp);
        tmp.focus();
        document.body.removeChild(tmp);
    }

    handleDragStart(elm, e, find) {


        this._blurAll();
        e.stopPropagation();
        if (this.drag_start_timer) {
            clearTimeout(this.drag_start_timer);
        }

        this.drag_start_timer = setTimeout(() => {
            this._blurAll();
            let $elm = this.$drag_elm = $(elm);
            let $offsetter = $elm.parent();
            while ($offsetter && $offsetter.css('position') !== 'relative') {
                $offsetter = $offsetter.parent();
            }
            find('.drop-space').removeClass('over');
            find('.drop-space').addClass('active');
            $elm.find('.drop-space').removeClass('active');

            this.position = {
                left: $elm.offset().left - $offsetter.offset().left,
                top: $elm.offset().top - $offsetter.offset().top,
                width: $elm.width()
            };

            this.mouse = {
                left: e.pageX,
                top: e.pageY,
            };

            this.dragging = true;

            $elm.addClass('dragging');
            $elm.css(this.position);
        }, 500);

        return false;
    }

    handleDragMove(elm, e, find) {
        if (this.dragging) {
            let position = {
                left: this.position.left - this.mouse.left + e.pageX,
                top: this.position.top - this.mouse.top + e.pageY
            };

            this.$drag_elm.css(position);
            let $elem = find('.drop-space.active')
                .filter(function () {
                    let $this = $(this);
                    let rect = {
                        x: $this.offset().left,
                        y: $this.offset().top,
                        w: $this.outerWidth(),
                        h: $this.outerHeight(),
                    }

                    return rect.y < e.pageY && rect.y + rect.h > e.pageY
                        && rect.x < e.pageX && rect.x + rect.w > e.pageX;
                });
            if ($elem.length === 0) {
                this.handleDragLeave();
            } else if ($elem[0] !== this.drag_over_elm) {
                this.handleDragLeave();
                this.handleDragEnter($elem);
                this.drag_over_elm = $elem[0];
            }
        }
    }

    handleDragEnd(elm, e, find) {
        if (this.dragging) {
            find('.drop-space').removeClass('over');
            find('.drop-space').removeClass('active');
            this.$drag_elm.css({left: 0, top: 0, height: ''}).removeClass('dragging');

            if (this.drag_over_elm) {
                this.handleDrop(this.drag_over_elm);
                this.handleDragLeave();
            }
            this.dragging = false;
        } else if (this.drag_start_timer) {
            clearTimeout(this.drag_start_timer);
            this.drag_start_timer = false;
        }
    }

    handleDragEnter(elm) {
        if (this.dragging) {
            let $elm = $(elm).addClass('over');
            if ($elm.hasClass('drop-space-between')) {
                $elm.height(this.$drag_elm.outerHeight());
            }
        }
    }

    handleDragLeave() {
        if (this.dragging) {
            if (this.drag_over_elm) {
                $(this.drag_over_elm).removeClass('over').css('height', '');
                this.drag_over_elm = false;
            }
        }
    }

    handleDrop(elm) {
        let $target = $(elm).removeClass('over').css('height', '');
        this.$drag_elm.trigger('drop', $target);
    }
}