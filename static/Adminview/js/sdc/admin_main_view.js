import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';
import {getResizerEvents, onResizeMovable} from "../../../Utils/libs/moveable.js";


class AdminMainViewController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/admin_main_view"; //<admin-main-view></admin-main-view>
        this._cssUrls.push('/static/Utils/css/moveable.css',
            '/static/Adminview/css/sdc/admin_main_view.css');

        this.events.unshift(getResizerEvents(), {});
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
        this.onResize();
        return super.afterShow();
    }


    onRefresh() {
        this.onResize();
        return super.onRefresh();
    }

    onResize() {
        onResizeMovable.call(this);
    }

}

app.register(AdminMainViewController);