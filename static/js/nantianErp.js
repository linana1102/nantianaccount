/**
 * Created by Administrator on 2016-09-26.
 */
openerp.nantian_erp=function(instance){
    instance.nantian_erp={};
    var _t=instance.web._t,
        _lt=instance.web._lt,
        QWeb=instance.web.qweb;
    instance.nantian_erp.PageLoading=instance.web.Widget.extend({
        color:null,
        init:function(){
            var self=this;
            this.color={
                "可调用":"rgba(255,226,50,0.73)",
                "申请离职":"rgba(255,0,0,0.73)"
            }
        },
        start:function(o){
            this.modifyColor(o.client.action_manager.inner_action.display_name);
        },
        //调整颜色
        modifyColor:function(dispalyName){
            var self=this;
            if(dispalyName=="待调整的人员"){
                var timer=setInterval(function(){
                    if($("div.selfDefColor").length){
                        clearInterval(timer);
                        $("div.selfDefColor").each(function(i,v){
                            var status=$(v).find("span.dis_states").html();
                            console.log(status);
                            $(v).css({
                                "border-color":self.color[status],
                                "box-shadow":self.color[status]+" 3px 3px 3px 0px"
                            });
                        });
                    }
                },100);
            }
        }
    });

    //当视图加载时调用自己指定代码
    instance.web.actionList.push(new instance.nantian_erp.PageLoading());
}