import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';

class FileTreeController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = '/sdc_view/dashboard/file_tree'; //<file-tree></file-tree>
        this._cssUrls.push('/static/sdc_tools/css/sdc/search_controller.css',
            '/static/Dashboard/css/sdc/file_tree.css');
        this.events.unshift({
            'click': {
                '.element': this.toggleCollection
            }
        });
    }

    toggleCollection(elem, event) {
        event.stopPropagation();
        const $elem = $(elem);
        $elem.find('> .element').toggle();
        $elem.find('> .element .element').hide();
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
        let self = this;
        this.search_objects = [];
        this.find('.element').each(function () {
            const $this = $(this);
            self.search_objects.push({
                'name': $this.find('> .element-name').text().trim().toLowerCase(),
                'dom': $this
            });
        });

        return super.afterShow();
    }

    onRefresh() {
        return super.onRefresh();
    }

    onChange(elem) {
        let value = $(elem).val();
        if(value && value.length !== 0) {
            this.find('.element').hide();
            value = value.toLowerCase();
            const result = this.search_objects.filter(obj => obj.name.indexOf(value) >= 0);

            for(let elm of result) {
                let $elm = elm.dom
                while($elm.length > 0) {
                    $elm.show();
                    $elm = $elm.parent().closest('.element');
                }
            }
        } else {
            this.find('.element.depth-1').show();
        }
    }

}

app.register(FileTreeController).addMixin('change-sync-mixin');