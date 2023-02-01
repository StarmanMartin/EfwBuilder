import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class AdminCreateUserController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/admin_create_user"; //<admin-create-user></admin-create-user>
        this._cssUrls.push('/static/sdc_user/css/sdc/user_register.css','/static/Adminview/css/sdc/admin_create_user.css');

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

}

app.register(AdminCreateUserController).addMixin('auto-submit-mixin', 'change-sync-mixin');