import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class EfwListController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/dashboard/efw_list"; //<efw-list></efw-list>
        this._cssUrls.push('/static/Dashboard/css/sdc/efw_list.css');

        this.contentReload = true;
        this.events.unshift({
            '.delete-item-btn': {
                'click': this.openDelete
            },
        });
    }

    openDelete(item, ev) {
        let $ddc = this.find('.delete-dialog-container .modal').modal('show');
        let id = $(item).data('id');
        $ddc.find('.id_field').val(id);
        $ddc.find('.item_name').text($(item).closest(`.item-row-${ id }`).find('.item-row-name').text());
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

    onSubmit(res) {
        this.find(`.item-row-${res.id}`).remove();

    }

    onLoad($html) {
        return super.onLoad($html);
    }

    willShow() {
        return super.willShow();
    }

    afterShow() {
        this.find('[data-toggle="tooltip"]').tooltip();
        return super.afterShow();
    }

    onRefresh() {
        this.find('[data-toggle="tooltip"]').tooltip();
        return super.onRefresh();
    }

    onBack() {
        this._childController.searchController[0].onChange();
    }

}

app.register(EfwListController).addMixin('list-mixin', 'auto-submit-mixin');