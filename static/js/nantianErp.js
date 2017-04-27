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
                "可调用":"rgba(24,161,95,0.73)",
                "申请离职":"rgba(255,0,0,0.73)",
                "借调中":"rgba(255,226,50,0.73)"
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
                            $(v).css({
                                "border-color":self.color[status],
                                "box-shadow":self.color[status]+" 3px 3px 3px 0px"
                            });
                        });
                    }
                },100);
            }
            if(dispalyName=="员工"){
                var timer1=setInterval(function(){
                    if($(".oe_searchview_drawer").length){
                        clearInterval(timer1);
                        self.addSearchKey();
                    }
                },100);
            }
        },
        addSearchKey:function(){
            var $div=$('<div class="col-md-12">'+
            '<ul data-tag="certificate_institutions_id"><li><span class="oe_i">w</span>证书</li><li><a href="cisco">Cisco</a></li><li><a href="华为">华为</a></li><li><a href="华三">华三</a></li><li><a href="F5">F5</a></li><li><a href="IBM">IBM</a></li></ul>'+
            '<ul data-tag="level"><li><span class="oe_i">w</span>级别</li><li><a href="1">1级</a></li><li><a href="2">2级</a></li><li><a href="3">3级</a></li><li><a href="4">4级</a></li><li><a href="5">5级</a></li><li><a href="6">6级</a></li></ul>'+
            '<ul data-tag="working_team_id"><li><span class="oe_i">w</span>工作组</li><li><a href="中行">中行</a></li><li><a href="建行">建行</a></li><li><a href="农行">农行</a></li><li><a href="国开">国开</a></li><li><a href="光大">光大</a></li><li><a href="农发">农发</a></li><li><a href="信达">信达</a></li></ul>'+
            '<ul data-tag="work_age"><li><span class="oe_i">w</span>工作年限</li><li><a href="1">1年</a></li><li><a href="2">2年</a></li><li><a href="3">3年</a></li><li><a href="4">4年</a></li><li><a href="5">5年</a></li><li><a href="6">6年</a></li><li><a href="7">7年以上</a></li></ul>'+
            '<ul data-tag="category"><li><span class="oe_i">w</span>人员状态</li><li><a href="公司储备">公司储备</a></li><li><a href="合同在岗">合同在岗</a></li><li><a href="合同备岗">合同备岗</a></li><li><a href="合同赠送">合同赠送</a></li><li><a href="公司项目">公司项目</a></li></ul>'+
            '</div>');
            // var $div=$("<form><input type='submit' value='查询'></form>");
            $(".oe_searchview_drawer").append($div);
            var isTrigger=false;
            var indexObj={};
            //{"work_age":["1","2","3","4","5","6","7"],"certificate_institutions_id":["cisco","华为","华三","F5","IBM"],"level":["1","2","3","4","5","6"],"category":["在公司","在合同中","赠送","开发","其他"],"working_team_id":["中行","建行","农行","国开","广大","农发","信达"]}
            function refreshData(obj,t) {
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
                                indexObj[i]=[];
                                $("ul[data-tag="+i+"]>li").removeClass("active");
                                refreshData(indexObj,i);
                            }
                        });
                    }
                });
            }
            $("div.col-md-12>ul>li>a").click(function(e){
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
                    $.each(indexObj[tag],function (i,v) {
                        if(v===value){
                            indexObj[tag].splice(i,1);
                        }
                    })
                }else{
                    $(this).parent("li").addClass("active");
                    if(!indexObj[tag]){
                        indexObj[tag]=[];
                    }
                    indexObj[tag].push(value);
                }
                // console.log(JSON.stringify(indexObj));
                refreshData(indexObj,tag);

            });
            $("div.oe_searchview_clear").click(function () {
                $("div.col-md-12>ul>li").removeClass("active");
                indexObj={};
            });
        }
    });

    //当视图加载时调用自己指定代码
    instance.web.actionList.push(new instance.nantian_erp.PageLoading());

}