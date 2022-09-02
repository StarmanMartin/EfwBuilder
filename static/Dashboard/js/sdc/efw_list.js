import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class EfwListController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/dashboard/efw_list"; //<efw-list></efw-list>
        this._cssUrls.push('/static/Dashboard/css/sdc/efw_list.css');

        this.contentReload = true;
        this.events.unshift({

        });
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