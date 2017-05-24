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
            this.parent = parent;
            this.isTrigger = false;
            this.indexObj = {};
        },

        start: function() {
            var self = this;
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
            var tag={level:"级别",
                certificate_institutions_id:"证书",
                category:"人员状态",
                working_team_id:"工作组",
                work_age:"工作年限"};
            $("span.oe_facet_values>span.oe_facet_value").each(function (i,span) {
                var html=$(span).html().trim();
                if(html.indexOf(tag[t])===0){
                    self.isTrigger=true;
                    $(this).parent("span").siblings("span.oe_facet_remove").trigger("click");
                    self.isTrigger=false;
                }
            });

            //开始根据页面上勾选的选择去自动添加查询
            var length = obj[t].length,
                domain = [],
                propositions = [];
            for(var i=0;i<length;i++){
                if(i>0){
                    domain.unshift("|");
                }
                var child = [t,"",obj[t][i]];
                if(t==="level"){
                    child[1] = "=";
                }else if(t==="certificate_institutions_id"){
                    child[1] = "ilike";
                }else if(t==="category"){
                    child[1] = "=";
                }else if(t==="working_team_id"){
                    child[1] = "ilike";
                }else if(t==="work_age"){
                    if(obj[t][i]=="7"){
                        child[1] = ">=";
                    }else{
                        child[1] = "=";
                    }
                }
                domain.push(child);
                var str = (child[1] == "=" ? "是":"包含");
                propositions.push({label: tag[t]+" "+str+" "+obj[t][i]});
            }
            if(domain.length>0){
                self.parent.view.query.add({
                    category: _t("Advanced"),
                    values: propositions,
                    field: {
                        get_context: function () { },
                        get_domain: function () { return domain; },
                        get_groupby: function () { }
                    }
                });
            }

            $("div.oe_searchview_facets span.oe_facet_remove").click(function () {
                if(!self.isTrigger){
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



    instance.web_kanban.KanbanGroup.include({
        do_add_records:function(){
            if(this.view && this.view.fields_view.name == "可调整人员看板"){
                var erp =  new instance.nantian_erp.ModifyColor(this);
                erp.start();
            }
            return this._super.apply(this, arguments);
        }
    });

    instance.web.search.Advanced.include({
        start:function(){
            var self = this;
            this.view.ready.done(function(){
                if(self.view.model == "hr.employee"){
                    var searchKey = new instance.nantian_erp.SearchKey(self);
                    searchKey.appendTo(".oe_searchview_drawer");
                }
            });
            return this._super.apply(this, arguments);
        }
    });

    instance.nantian_erp.UploadResume = instance.web.Widget.extend({
        template:"nantian_erp.uploadResume",
        events: {
            "click":"triggerInput",
            "click .delete_resume":"delete_resume"
        },
        init: function(parent) {
            this._super(parent);
            this.parent = parent;
        },

        start: function() {
            this._super(this);
            var target = $(".oe_form_sheet")[0];
            if(this.parent.items.files.length){
                this.parent.$el.addClass("hidden_upload_btn");
                this.act = "preview";
                target.ondragenter = null;
                target.ondragover = null;
                target.ondragleave = null;
                target.ondrop = null;
            }else{
                this.parent.$el.removeClass("hidden_upload_btn");
                this.act = "upload";
                var me = this;
                $(target).css("position","relative");
                target.ondragenter = function(e){
                    e.preventDefault();
                }
                target.ondragover = function(e){
                    e.preventDefault();
                }
                target.ondragleave = function(e){
                    e.preventDefault();
                }
                target.ondrop = function(e){
                    e.preventDefault();
                    var files = e.dataTransfer.files;
                    me.parent.$el.find(".oe_form_binary_file")[0].files = files;
                }

            }
        },
        triggerInput:function(e){
            if(this.act == "upload"){
                this.parent.$el.find(".oe_form_binary_file").trigger("click");
            }else{
                var url = String(this.parent.items.files[0].url).replace("saveas","html_page");
                window.open(url,"_blank");
                //this.parent.$(".oe_sidebar_action_a[data-section=files]")[0].click();
            }
        },
        delete_resume:function(e){
            e.preventDefault();
            e.stopPropagation();
            this.parent.on_attachment_delete(e);
        }
    });

    instance.nantian_erp.ExportResume = instance.web.Widget.extend({

        init: function(parent) {
            this._super(parent);
            this.parent = parent;
        },

        start:function(){
            var me = this;
            this._super(this);
            this.parent.items['other'].push({
                classname:"oe_sidebar_action",
                label:"导出简历",
                callback:function(){
                    me.exportAction(this);
                }
            });
        },

        exportAction:function(a){
            var ids = a.getParent().get_selected_ids();
            console.log(ids);
        }
    });

    instance.web.Sidebar.include({
        redraw:function(){
            if(this.dataset && this.model_id && this.dataset.model == "nantian_erp.resume"){
                var UploadResume = new instance.nantian_erp.UploadResume(this);
                this.view.$el.find(".oe_right .uploadResume").remove();
                UploadResume.appendTo(this.view.$el.find(".oe_right[name=buttons]"));
            }
            return this._super.apply(this, arguments);
        },
        start:function(){
            if(this.view.model == "hr.employee"){
                var ExportResume = new instance.nantian_erp.ExportResume(this);
                ExportResume.insertAfter(this.$(".oe_sidebar_action"));
            };
            return this._super.apply(this, arguments);
        }

    });

}