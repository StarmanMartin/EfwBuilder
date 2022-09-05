import {AbstractSDC} from '../../../simpleDomControl/AbstractSDC.js';
import {app} from '../../../simpleDomControl/sdc_main.js';


class GitListController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/adminview/git_list"; //<git-list></git-list>
        this._cssUrls.push('/static/Adminview/css/sdc/git_list.css');
        this.contentReload = true;
        this.events.unshift({
            'click': {
                '.btn-reload-git': function() {
                    this.find('.loader').show();
                }
            }
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

    onErrorSubmit(res) {
        this.find('.loader').hide();
        $('.tooltip.fade.show').remove();
    }

    onSubmit(res) {
        if (res._action === "activate") {
            this._childController.searchController[0].onChange();
        } else if (res._action === "reload") {
            let $html = $(res.html);
            let $row = this.find(`.item-row-${res.pk}`);
            app.safeReplace($row, $html);
        }


        this.onErrorSubmit();
    }

}

app.register(GitListController).addMixin('list-mixin', 'auto-submit-mixin');