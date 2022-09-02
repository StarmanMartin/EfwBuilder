import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class AdminUserController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/admin_user"; //<admin-user></admin-user>
        this._cssUrls.push('/static/Adminview/css/sdc/admin_user.css');
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

    onSubmit(res) {
        let $html = $(res.html);

        if (res._action === "activate" || res._action === "set_staff") {
                let $row = this.find(`.item-row-${res.pk}`);
                app.safeReplace($row, $html);
        }

        $('.tooltip.fade.show').remove();
    }

}

app.register(AdminUserController).addMixin('list-mixin', 'auto-submit-mixin');