import {app} from '../../../simpleDomControl/sdc_main.js';
import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';


class AdminEditUserController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/admin_edit_user/%(user_pk)s"; //<admin-edit-user data-user_pk=""></admin-edit-user>
        this._cssUrls.push('/static/sdc_user/css/sdc/user_edit.css',
            '/static/Adminview/css/sdc/admin_edit_user.css');

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
        return super.afterShow();
    }

    onRefresh() {
        return super.onRefresh();
    }

}

app.register(AdminEditUserController).addMixin('auto-submit-mixin', 'change-sync-mixin');;