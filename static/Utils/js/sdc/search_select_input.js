import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class SearchSelectInputController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/utils/search_select_input/%(model)s/%(value)s"; //<search-select-input data-model="" data-value=""></search-select-input>
        this._cssUrls.push('/static/Utils/css/sdc/search_select_input.css');
        this.events.unshift({
            'click': {
                '.btn-not-selected': this.onSelect,
                '.btn-selected': this.onUnselect,
            }
        });
    }

    onSelect(btn, ev) {
        let $btn = $(btn);
        let $container = $btn.closest('.selectable');
        let $tbody = this.find('.table-selected-value');
        let btVal = "" + $container.data('value');
        if($tbody.find(`.selectable-${btVal}`).length === 0) {
            $tbody.append($container);
            this.value.push(btVal);
            this.find('.search-value').val(this.value.join(','));
        }

    }

    onUnselect(btn, ev) {
        let $btn = $(btn);
        let $container = $btn.closest('.selectable');
        let $tbody = this.find('.list-container');
        let btVal = "" + $container.data('value');

        if($tbody.find(`.selectable-${btVal}`).length === 0) {
            $tbody.prepend($container);
            const index = this.value.indexOf(btVal);
            if (index > -1) { // only splice array when item is found
               this.value.splice(index, 1); // 2nd parameter means remove one item only
            }

            this.find('.search-value').val(this.value.join(','));
        } else {
            $container.remove();
        }

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

    onInit(name, value) {
        this.name = name;
        if(!value || value === "") {
            this.value = [];
        } else {
            this.value = value.split(',');
        }
    }

    onLoad($html) {
        return super.onLoad($html);
    }

    willShow() {
        return super.willShow();
    }

    afterShow() {
        this.find('.search-value').attr('name', this.name);
        this.find('.search-value').val(this.value.join(','));
        this.removeDuplicates();
        return super.afterShow();
    }

    removeDuplicates() {
        let $selected = this.find('.table-selected-value .selectable');

        let $tbody = this.find('.list-container');

        $selected.each(function() {
            let $container = $(this);
            let $newSelectable = $tbody.find(`.selectable-${$container.data('value')}`);
            if($newSelectable.length !== 0) {
                $newSelectable.remove();
            }
        });
    }

    onRefresh() {
        this.removeDuplicates();

        return super.onRefresh();
    }

    onSearch(form) {
        this._mixins.ListMixinController.onSearch.call(this, form);
    };

}

app.register(SearchSelectInputController).addMixin('list-mixin');