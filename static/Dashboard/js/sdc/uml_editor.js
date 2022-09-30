import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';
import {uuidv4} from "../../../simpleDomControl/sdc_utils.js";

const MODE = {
    POINTER: 0,
    DRAG_CANVAS: 1,
    DRAG_NODE: 2,
    ADD_EDGE: 3,
};

const FIELDS = ["Checkbox",
    "Drag Element",
    "Drag Molecule",
    "Drag Sample",
    "Formula-Field",
    "Input Group",
    "Integer",
    "Select",
    "System-Defined",
    "Table",
    "Text",
    "Text-Formula",
    "Text area",
    "Upload"];

const ARROW_COLOR = '#ffffff';

function drawArrow(ctx, fromx, fromy, tox, toy) {
    //variables to be used when creating the arrow
    const headlen = 10;
    const angle = Math.atan2(toy - fromy, tox - fromx);
    tox -= Math.cos(angle) * (2);
    toy -= Math.sin(angle) * (2);

    //starting path of the arrow from the start square to the end square and drawing the stroke
    ctx.beginPath();
    ctx.moveTo(fromx, fromy);
    ctx.lineTo(tox, toy);
    ctx.strokeStyle = ARROW_COLOR;
    ctx.lineWidth = 2;
    ctx.stroke();

    //starting a new path from the head of the arrow to one of the sides of the point
    ctx.beginPath();
    ctx.moveTo(tox, toy);
    ctx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 7), toy - headlen * Math.sin(angle - Math.PI / 7));

    //path from the side point of the arrow, to the other side point
    ctx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 7), toy - headlen * Math.sin(angle + Math.PI / 7));

    //path from the side point back to the tip of the arrow, and then again to the opposite side point
    ctx.lineTo(tox, toy);
    ctx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 7), toy - headlen * Math.sin(angle - Math.PI / 7));

    //draws the paths created above
    ctx.stroke();
    ctx.fill();
}


class UmlEditorController extends AbstractSDC {

    constructor() {
        super();

        this.contentUrl = "/sdc_view/dashboard/uml_editor/%(dia_pk)s"; //<uml-editor data-dia_pk=""></uml-editor>
        this._cssUrls.push('/static/Dashboard/css/sdc/uml_editor.css');
        this.elements = [];

        this._tResize = false;
        this._tMousedown = false;

        this.mode = MODE.POINTER;
        this.mousePos = {x: 0, y: 0};
        this.canvasPos = {x: 0, y: 0};
        this.$selectedNode = null;
        this.zoom = 1;
        this.relationEdges = []
        this.newEdges = null;

        this.events.unshift({
            '.uml-canvas': {
                'mousedown': this.onCanvasMousedown,
                'mousemove': this.onCanvasMousemove,
                'mouseup': this.onCanvasMouseup,
                'mouseleave': this.onMouseleave,
                'mousewheel': this.onScroll,
                'DOMMouseScroll': this.onScroll,
                'click': this.onCanvasClick
            },
            '.uml-canvas .menu-handler, .uml-canvas.menu-handler': {
                'contextmenu': this.onContextMenu
            },
            '.uml-canvas .uml-node': {
                'mousedown': this.onNodeMousedown,
                'click': this.onNodeClick,
            },
            '.uml-canvas .uml-node .text-container': {
                'mouseup': this.editElement
            },
            '.uml-menu': {
                'mouseleave': this._clearMode,
                'mousedown': (_, e) => {
                    e.stopPropagation();
                },
            },
            '.uml-menu-canvas .btn': {
                'click': this.addNode,
            },
            '.uml-menu-node .btn-rm-element': {
                'click': this.rmElement,
            },
            '.uml-menu-node .btn-add-segment': {
                'click': this.addSegment,
            },
            '.uml-menu-node .add-relation': {
                'click': this.addRelation,
            },
            '.uml-menu-Segment .btn-rm-segment': {
                'click': this.rmElement,
            },
            '.uml-menu-Segment .btn-add-layer': {
                'click': this.addNodeLayer,
            },
            '.uml-menu-Layer .btn-rm-layer': {
                'click': this.rmElement
            },
            '.btn-save': {
                'click': this.saveToJSON
            }
        });
    }

    /**
     * this._clearTimeout('_tResize')
     * this._clearTimeout('_tMousedown')
     * @param  tName:string  Timer name
     * @private
     */
    _clearTimeout(tName) {
        if (this[tName]) {
            clearTimeout(this[tName]);
            this[tName] = false;
        }
    }

    _clearMode(elm, event) {
        if (this.mode === MODE.ADD_EDGE) {
            return
        }
        this._clearTimeout('_tMousedown');
        this.mode = MODE.POINTER;
        this.find('.dragging').removeClass('dragging');
        this.find('.uml-menu').removeClass('active');
        this._drawEdges();
    }

    _getMousePosZoom(evt) {
        this.rect = this.find('.uml-node-container').get(0).getBoundingClientRect();
        return {
            x: (evt.clientX - this.rect.left) / this.zoom,
            y: (evt.clientY - this.rect.top) / this.zoom,
        };
    }

    _getMousePosAbs(evt) {
        this.rect = this.find('.uml-canvas').get(0).getBoundingClientRect();
        return {
            x: (evt.clientX - this.rect.left),
            y: (evt.clientY - this.rect.top),
        };
    }

    _getMousePosCanvas(evt) {
        let pos = this._getMousePosZoom(evt);
        return {
            x: pos.x - this.canvasPos.x,
            y: pos.y - this.canvasPos.y
        };
    }

    _openMenu(name, $fromElement, event) {
        let tempMP = this._getMousePosAbs(event);
        let $menu = this.find(name);
        $menu.addClass('active').css({
            top: `${tempMP.y - $menu.height() / 2}px`,
            left: `${tempMP.x - $menu.width() / 2}px`
        }).data('target', $fromElement);
    }

    _turnEditOn($target, event) {
        if (this.mode !== MODE.POINTER) {
            return;
        }
        event.stopPropagation();
        this._clearMode();
        let $textarea = $(document.createElement('input')).addClass('node-text-change-area').val($target.find('h4').text());
        $target.append($textarea);
        $textarea.get(0).focus();

        function onChange() {
            $target.find('h4').text($textarea.val());
            $textarea.off('focusout', onChange);
            $textarea.remove();
        }

        $textarea.on('focusout', onChange);
    }

    _turnListEditOn($target, event) {
        event.stopPropagation();
        this._clearMode();
        let val = [];
        $target.find('li').each(function () {
            let $this = $(this);
            if ($this.closest('ul').hasClass('table-list')) {
                val.push(`--${$this.text()}`);
            } else {
                val.push(`-${$this.text()}`);
            }
        });
        let $textarea = $(document.createElement('textarea')).addClass('node-text-change-area').val(val.join('\n'));
        $target.append($textarea);
        $textarea.get(0).focus();

        function onChange() {
            let inTable = false;
            let htmlText = $textarea.val().split('\n').map((a) => {
                let isInTable = a.startsWith('--');

                if (isInTable && inTable) {
                    return ` <li>${a.substr(2)}</li>`;
                } else if (isInTable && !inTable) {
                    inTable = true;
                    return `<ul class="table-list">\n <li>${a.substr(2)}</li>`;
                } else if (!isInTable && inTable) {
                    inTable = false;
                    return `</ul>\n<li>${a.substr(1)}</li>`;
                }
                return `<li>${a.substr(1)}</li>`;
            });

            if (inTable) {
                htmlText.push('</ul>');
            }

            $target.find('ul').html((htmlText.join('\n')));
            $textarea.off('focusout', onChange);
            $textarea.remove();
        }

        $textarea.on('focusout', onChange);
    }

    _getApsPosOfElem($elem) {
        const $canvas = this.find('.uml-canvas ');

        let x = parseInt($elem.css('left')) + this.canvasPos.x;
        let y = parseInt($elem.css('top')) + this.canvasPos.y;
        let h = parseInt($elem.height());
        let w = parseInt($elem.width());

        x = (x + w / 2) * this.zoom - $canvas.width() * ((this.zoom - 1) / 2);
        y = (y + h / 2) * this.zoom - $canvas.outerHeight() * ((this.zoom - 1) / 2);

        return {
            x: x, y: y
        }

    }

    _drawEdges(event) {
        const canvas = this.find('.background-canvas').get(0);
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (this.mode !== MODE.ADD_EDGE && this.newEdges) {
            this.newEdges = null;
        }
        this.relationEdges = [];
        let self = this;
        this.find('.uml-node').each(function() {
            let $node = $(this);
            if($node.data('related')) {
                for (const target of $node.data('related').split(',')) {
                    self.relationEdges.push([$node, self.find(`.${target}`)]);
                }
            }
        });

        if(this.newEdges !== null) {
            self.relationEdges.push(this.newEdges);
        }

        for (let e of this.relationEdges) {
            let mp;

            let elem_pos = this._getApsPosOfElem(e[0]);
            if (e[1] === 'mouse') {
                mp = this._getMousePosAbs(event);
            } else {
                mp = this._getApsPosOfElem(e[1]);
                const angle = Math.atan2(elem_pos.y - mp.y, elem_pos.x - mp.x);
                const testAngle = (angle + (2 * Math.PI)) % Math.PI;
                if (testAngle < 3 * Math.PI / 4 && testAngle > Math.PI / 4) {
                    mp.x += Math.cos(angle) * ((e[1].width() + 5) / 2 * this.zoom);
                    mp.y += Math.sign(Math.sin(angle)) * ((e[1].height() + 5) / 2 * this.zoom);
                } else {
                    mp.y += Math.sin(angle) * ((e[1].height() + 5) / 2 * this.zoom);
                    mp.x += Math.sign(Math.cos(angle)) * ((e[1].width() + 5) / 2 * this.zoom);
                }


            }
            drawArrow(ctx, elem_pos.x, elem_pos.y, mp.x, mp.y);
        }
    }

    //-------------------------------------------------//
    // - Button Event Element Layer                    //
    //-------------------------------------------------//

    onElemMouseup(btn, event) {
        this._clearMode();
        let $target = $(btn).closest('.uml-menu').data('target').find('.layer-body li');
        let $textarea = $(document.createElement('input')).addClass('node-text-change-area').val();
        $target.append($textarea);
        $textarea.get(0).focus();

        function onChange() {
            $target.find('h4').text($textarea.val());
            $textarea.off('change', onChange);
            $textarea.remove();
        }

        $textarea.on('change', onChange);
    }

    //-------------------------------------------------//
    // - Button Event Handler Segment                  //
    //-------------------------------------------------//


    addNodeLayer(btn, event) {
        this._clearMode();
        let $target = $(btn).closest('.uml-menu').data('target');
        let $node = this.find('.dummy-node .segment-layer').clone();
        $target.append($node)
        app.refresh($target);
    }

    //-------------------------------------------------//
    // - Button Event Handler Node                     //
    //-------------------------------------------------//

    addRelation(btn, event) {
        event.stopPropagation();
        this._clearMode();
        this.mode = MODE.ADD_EDGE;
        let $target = $(btn).closest('.uml-menu').data('target');
        this.newEdges = [$target, 'mouse'];
    }

    addSegment(btn, event) {
        this._clearMode();
        let $target = $(btn).closest('.uml-menu').data('target');
        let $node = this.find('.dummy-node .node-segment').clone();
        $target.find('.node-segment-container').append($node)
        app.refresh($target);
    }

    addNode(_, event) {
        this._clearMode();
        let mousePos = this._getMousePosCanvas(event);
        let x = (mousePos.x);
        let y = (mousePos.y);

        let $node = this.find('.dummy-node .uml-node').clone();
        let newUuid;
        do {
            newUuid = uuidv4();
        } while (this.find(`.${newUuid}`).length !== 0)

        $node.css({
            top: `${y}px`,
            left: `${x}px`,
            transform: `translate(${this.canvasPos.x}px,${this.canvasPos.y}px)`
        }).addClass(newUuid).data('token', newUuid);
        let $container = this.find('.uml-node-container').append($node)
        app.refresh($container);
    }

    //-------------------------------------------------//
    // - Node Event Handler                            //
    //-------------------------------------------------//

    onNodeMousedown(elm, event) {
        event.stopPropagation();
        if (this.mode === MODE.ADD_EDGE) {
            return;
        }
        this._clearMode();
        this._tMousedown = setTimeout(() => {
            this.mode = MODE.DRAG_NODE;
            this.$selectedNode = $(elm);
            this.$selectedNode.closest('.uml-canvas').addClass('dragging');
            this.mousePos = {
                x: this.canvasPos.x + this.$selectedNode.width() / 2,
                y: this.canvasPos.y
            };
        }, 200);
    }

    onNodeClick(elm, event) {
        if (this.mode === MODE.ADD_EDGE) {
            let related = this.newEdges[0].data('related');
            let cv;
            if(related) {
                cv = related.split(',');
            } else {
                cv = []
            }
            cv.push($(elm).data('token'));
            this.newEdges[0].data('related', cv.join(','));
            this.newEdges = null;
            this.mode = MODE.POINTER
            this._clearMode();
        }
    }

    //-------------------------------------------------//
    // - Canvas Event Handler                          //
    //-------------------------------------------------//

    editElement(btn, event) {
        let $btn = $(btn);
        if ($btn.hasClass('list-text')) {
            this._turnListEditOn($btn, event);
        } else {
            this._turnEditOn($btn, event);
        }
    }

    rmElement(btn, event) {
        this._clearMode();
        let $target = $(btn).closest('.uml-menu').data('target');
        $target.remove();
        app.refresh(this.find('.uml-node-container'));
    }


    onContextMenu(elm, event) {
        event.stopPropagation();
        event.preventDefault();
        let mode = this.mode
        this._clearMode();
        if (mode === MODE.POINTER) {
            event.preventDefault();
            let $elm = $(elm);
            this._openMenu($elm.data('menu'), $elm, event);
        }
    }

    onCanvasMousedown(elm, event) {
        if (this.mode === MODE.ADD_EDGE) {
            return;
        }
        let $elm = $(elm);
        this._clearMode();
        this._tMousedown = setTimeout(() => {
            this.mode = MODE.DRAG_CANVAS;
            $elm.addClass('dragging');
            this.mousePos = this._getMousePosZoom(event);
            this.mousePos.x -= this.canvasPos.x;
            this.mousePos.y -= this.canvasPos.y;
        }, 200);
    }

    onCanvasMousemove(_, event) {

        if (this.mode === MODE.DRAG_CANVAS) {
            let tempMP = this._getMousePosZoom(event);
            this.canvasPos = {x: tempMP.x - this.mousePos.x, y: tempMP.y - this.mousePos.y};
            this.find('.uml-node-container > .uml-node').css(`transform`, `translate(${this.canvasPos.x}px,${this.canvasPos.y}px)`);
            this._drawEdges(event);
        } else if (this.mode === MODE.DRAG_NODE) {
            let tempMP = this._getMousePosZoom(event);
            let x = (tempMP.x - this.mousePos.x);
            let y = (tempMP.y - this.mousePos.y);
            this.$selectedNode.css({
                top: `${y}px`,
                left: `${x}px`
            });
            this._drawEdges(event);
        } else if (this.mode === MODE.ADD_EDGE) {
            this._drawEdges(event);
        }
    }

    onCanvasMouseup(elm, event) {
        if (event.which !== 3) {
            this._clearMode();
        }
    }

    onMouseleave() {
        this.mode = MODE.POINTER
        this._clearMode();
    }

    onCanvasClick() {
        if (this.mode === MODE.ADD_EDGE) {
            this.newEdges = null;
            this.mode = MODE.POINTER
            this._clearMode();
        }
    }

    onScroll(_, e) {
        e.preventDefault();
        var delta = e.delta || e.originalEvent.wheelDelta;
        var zoomOut;
        if (delta === undefined) {
            //we are on firefox
            delta = e.originalEvent.detail;
            zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
            zoomOut = !zoomOut;
        } else {
            zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
        }

        if (zoomOut && this.zoom > 0.2) {
            //we are zooming out
            this.zoom -= .1;
            this._drawEdges();
        } else if (this.zoom < 4) {
            //we are zooming in
            this.zoom += .1;
            this._drawEdges();
        }


        this.find('.uml-node-container').css(`transform`, `scale(${this.zoom})`);
    }


    //------------------------------------------------//
    // Save to JSON                                   //
    //------------------------------------------------//

    /**
     *
     * @param text {string}
     * @returns {string}
     * @private
     */
    _toSnakeCase(text) {
        return text.toLowerCase().replaceAll(' ', '_');
    }

    saveToJSON() {
        let jsonData = this._toJSON();
        let $form = this.find('.save-json-form');
        $form.find('.json-input').val(JSON.stringify(jsonData));
        $form.trigger('submit');
    }

    _toJSON() {
        this._drawEdges();
        let jsonDiagram = {
            elements: [],
            relations: this.relationEdges.map((a)=> [a[0].data('token'), a[1].data('token')])
        };

        let self = this;
        this.find('.uml-canvas .uml-node').each(function () {
            let $node = $(this);
            let title = $node.find('.node-header h4').text();
            let element = {
                key: self._toSnakeCase(title),
                label: title,
                token: $node.data('token'),
                x: parseInt($node.css('left')),
                y: parseInt($node.css('top')),
                segments: []
            };

            jsonDiagram.elements.push(element);

            /*
             * Filling Segments
             */
            $node.find('.node-segment').each(function () {
                let $segment = $(this);
                title = $segment.find('.segment-header h4').text();
                let segment = {
                    key: self._toSnakeCase(title),
                    label: title,
                    layers: []
                };
                element.segments.push(segment);

                /*
                 * Filling Layers
                 */
                $segment.find('.segment-layer').each(function () {
                    let $layer = $(this);
                    title = $layer.find('.layer-header h4').text();
                    let layer = {
                        key: self._toSnakeCase(title),
                        label: title,
                        fields: []
                    };
                    segment.layers.push(layer);
                    let tableCounter = 0;
                    let field = {};

                    /*
                    * Filling Fields
                    * */
                    $layer.find('.layer-body ul').children().each(function () {
                        let $field = $(this);

                        function runFieldDecoding($field) {
                            let field_title = $field.text().split(':');
                            return {
                                field: self._toSnakeCase(field_title[0]),
                                type: field_title.length === 2 ? field_title[1].toLowerCase() : 'text',
                                label: field_title[0],
                                sub_fields: []
                            };
                        }

                        if ($field.hasClass('table-list')) {
                            if (field.type !== 'table') {
                                field = {
                                    field: `table_${self._toSnakeCase(title)}_${tableCounter}`,
                                    type: 'table',
                                    label: `Table ${title} ${tableCounter}`,
                                    sub_fields: []
                                };
                            }

                            $field.find('li').each(function () {
                                let subField = runFieldDecoding($(this));
                                field.sub_fields.push(subField);
                            });


                        } else {
                            field = runFieldDecoding($field);
                        }
                        layer.fields.push(field);
                    });
                });
            });
        });

        return jsonDiagram;
    }

    //-------------------------------------------------//
    // Lifecycle handler                               //
    // - onInit (tag parameter)                        //
    // - onLoad (DOM not set)                          //
    // - willShow  (DOM set)                           //
    // - afterShow  (recalled on reload)               //
    //-------------------------------------------------//
    // - onRefresh                                     //
    //-------------------------------------------------//
    // - onRemove                                      //
    //-------------------------------------------------//

    onInit() {
    }

    onLoad($html) {
        return super.onLoad($html);
    }

    willShow() {
        return super.willShow();
    }

    afterShow() {
        this.onResize();
        this.find('[data-toggle="tooltip"]').tooltip();
        return super.afterShow();
    }

    onRefresh() {
        this.find('[data-toggle="tooltip"]').tooltip();
        return super.onRefresh();
    }

    onResize() {
        let $nav_container = this.$container.closest('.movable-flex-item');
        this.find('.uml-canvas').height(0);
        this._clearTimeout('_tResize');

        this._tResize = setTimeout(() => {
            this.rect = this.find('.uml-canvas').height($nav_container.height()).get(0).getBoundingClientRect();
            const canvas = this.find('.background-canvas').get(0);
            canvas.width = this.rect.width;
            canvas.height = this.rect.height;
            this._drawEdges();
        }, 100)

    }

}

app.register(UmlEditorController).addMixin('auto-submit-mixin');