/**
 * Created by Administrator on 2016-09-26.
 */
openerp.nantian_erp=function(instance){
    instance.nantian_erp={};
    var _t=instance.web._t,
        _lt=instance.web._lt,
        QWeb=instance.web.qweb;
    instance.nantian_erp.ModifyColor = instance.web.Widget.extend({
        color:null,
        init:function(){
            var self=this;
            this.color={
                "可调用":"rgba(24,161,95,0.73)",
                "申请离职":"rgba(255,0,0,0.73)",
                "借调中":"rgba(255,226,50,0.73)"
            }
        },
        start:function(){
            var self=this;
            var n = 0;
            var timer = setInterval(function(){
                if($("div.selfDefColor").length>0 || ++n>50){
                    clearInterval(timer);
                    $("div.selfDefColor").each(function(i,v){
                        var status=$(v).find("span.dis_states").html();
                        $(v).css({
                            "border-color":self.color[status],
                            "box-shadow":self.color[status]+" 3px 3px 3px 0px"
                        });
                    });
                }
            },200);

        }
    });


    instance.nantian_erp.SearchKey = instance.web.Widget.extend({
        template: "addSearchKey",
        events: {
            /*'click a': function(e){
                console.log(e);
            }*/
        },

        init: function(parent) {
            this._super(parent);
            this.isTrigger = false;
            this.indexObj = {};
        },

        start: function() {
            var self = this;
            var sup = this._super();
            this.$("li>a").click(function(e){
                var e=e||event;
                if (e.preventDefault){
                    e.preventDefault();
                    //IE中阻止函数器默认动作的方式
                }else{
                    e.returnValue = false;
                }
                var tag=$(this).parents("ul[data-tag]").attr("data-tag");
                var value=$(this).attr("href");
                var liActive=$(this).parent().attr("class");
                if(liActive){
                    $(this).parent().removeClass("active");
                    $.each(self.indexObj[tag],function (i,v) {
                        if(v===value){
                            self.indexObj[tag].splice(i,1);
                        }
                    })
                }else{
                    $(this).parent("li").addClass("active");
                    if(!self.indexObj[tag]){
                        self.indexObj[tag]=[];
                    }
                    self.indexObj[tag].push(value);
                }
                // console.log(JSON.stringify(indexObj));
                self.refreshData(self.indexObj,tag);

            });
            $("div.oe_searchview_clear").click(function () {
                $("div.col-md-12>ul>li").removeClass("active");
                self.indexObj={};
            });
        },
        refreshData:function(obj,t){
            var self = this;
            //开始先删除相关的已选择的选项标签
            var tag={level:"Level",
                certificate_institutions_id:"certificate_institutions",
                category:"人员状态",
                working_team_id:"Working team",
                work_age:"Work age"};
            $("span.oe_facet_values>span.oe_facet_value").each(function (i,span) {
                var html=$(span).html().trim();
                if(html.indexOf(tag[t])===0){
                    isTrigger=true;
                    $(this).parent("span").siblings("span.oe_facet_remove").trigger("click");
                    isTrigger=false;
                }
            });

            //开始根据页面上勾选的选择去自动添加查询
            var length=obj[t].length;
            for(var i=1;i<length;i++){
                $('.oe_add_condition').trigger("click");
            }
            for(var i=0;i<length;i++){
                $("form li:eq("+i+") .searchview_extended_prop_field").val(t);
                $("form li:eq("+i+") .searchview_extended_prop_field").trigger("change");
                if(t==="level"){
                    $("form li:eq("+i+") .searchview_extended_prop_op").val("=");
                    $("form li:eq("+i+") .searchview_extended_prop_value>select").val(obj[t][i]);
                }else if(t==="certificate_institutions_id"){
                    $("form li:eq("+i+") .searchview_extended_prop_op").val("ilike");
                    $("form li:eq("+i+") .searchview_extended_prop_value>input.field_char").val(obj[t][i]);
                }else if(t==="category"){
                    $("form li:eq("+i+") .searchview_extended_prop_op").val("=");
                    $("form li:eq("+i+") .searchview_extended_prop_value>select").val(obj[t][i]);
                }else if(t==="working_team_id"){
                    $("form li:eq("+i+") .searchview_extended_prop_op").val("ilike");
                    $("form li:eq("+i+") .searchview_extended_prop_value>input.field_char").val(obj[t][i]);
                }else if(t==="work_age"){
                    if(obj[t][i]=="7"){
                        $("form li:eq("+i+") .searchview_extended_prop_op").val(">=");
                    }else{
                        $("form li:eq("+i+") .searchview_extended_prop_op").val("=");
                    }
                    $("form li:eq("+i+") .searchview_extended_prop_value>input.field_integer").val(obj[t][i]);
                }
            }
            if(length>0){
                $("form button.oe_apply:first").trigger("submit");
            }
            $("div.oe_searchview_facets span.oe_facet_remove").click(function () {
                if(!isTrigger){
                    var tar=$(this).siblings(".oe_facet_values").find("span.oe_facet_value").html().trim();
                    $.each(tag,function (i,v) {
                        if(tar.indexOf(v)>=0){
                            self.indexObj[i]=[];
                            $("ul[data-tag="+i+"]>li").removeClass("active");
                            self.refreshData(self.indexObj,i);
                        }
                    });
                }
            });
        }
    });



    instance.web_kanban.KanbanView.include({
        start:function(){
            if(this.dataset.model == "hr.employee"){
                var erp =  new instance.nantian_erp.ModifyColor(this);
                erp.start();
            }
            return this._super.apply(this, arguments);
        }
    });

    instance.web.SearchViewDrawer.include({
        prepare_filters:function(data){
            var self = this;
            this.ready.done(function(){
                if(data.model == "hr.employee"){
                    var searchKey = new instance.nantian_erp.SearchKey(self);
                    searchKey.appendTo(self.$el);
                }
            });
            return this._super.apply(this, arguments);
        }
    });

}