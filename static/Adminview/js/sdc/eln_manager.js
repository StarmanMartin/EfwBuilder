import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class ElnManagerController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = '/sdc_view/adminview/eln_manager'; //<eln-manager></eln-manager>
        this._cssUrls.push('/static/Adminview/css/sdc/eln_manager.css');
        this.events.unshift({
'click': {
    '.show-modal': this.showModal
}
        });
    }

    showModal(btn) {
        // this.find($(btn).data('target')).modal('show');
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

app.register(ElnManagerController).addMixin('list-mixin', 'auto-submit-mixin');