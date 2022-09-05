import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';
import {getResizerEvents, onResizeMovable} from '../../../Utils/libs/moveable.js';


class MainViewController extends AbstractSDC {

    constructor() {
        super();
        this.menu_id = 1;
        this.contentUrl = "/sdc_view/dashboard/main_view"; //<main-view></main-view>
        this._cssUrls.push('/static/Utils/css/moveable.css',
            '/static/Dashboard/css/sdc/main_view.css');
        this.hasSubnavView = true;

        this.events.unshift(getResizerEvents(),{

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

app.register(MainViewController);