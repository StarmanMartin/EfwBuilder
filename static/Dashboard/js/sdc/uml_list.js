import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class UmlListController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/dashboard/uml_list"; //<uml-list></uml-list>
        this._cssUrls.push('/static/Dashboard/css/sdc/uml_list.css');

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

app.register(UmlListController).addMixin('list-mixin', 'auto-submit-mixin');