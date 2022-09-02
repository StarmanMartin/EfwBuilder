import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class AdminPasswordChangeController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/admin_password_change/%(user_pk)s"; //<admin-password-change data-user_pk=""></admin-password-change>
        this._cssUrls.push('/static/Adminview/css/sdc/admin_password_change.css');

        this.contentReload = true;
        this.isAutoChange = false;

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

    onSubmit() {
        alert(99);
        history.back();
    }

}

app.register(AdminPasswordChangeController).addMixin('change-sync-mixin', 'auto-submit-mixin');