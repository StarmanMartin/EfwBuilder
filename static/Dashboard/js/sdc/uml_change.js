import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class UmlChangeController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/dashboard/uml_change/%(dia_pk)s"; //<uml-change data-dia_pk=""></uml-change>
        this._cssUrls.push('/static/Dashboard/css/sdc/uml_change.css');
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
        return super.afterShow();
    }

    onRefresh() {
        return super.onRefresh();
    }

}

app.register(UmlChangeController).addMixin('auto-submit-mixin', 'change-sync-mixin');