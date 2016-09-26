/**
 * Created by Administrator on 2016-09-26.
 */
console.log("nantianErp模块js文件已经加载。。。。。");
openerp.nantian_erp=function(instance){
    instance.nantian_erp={};
    var _t=instance.web._t,
        _lt=instance.web._lt,
        QWeb=instance.web.qweb;

    /*instance.web.form.FieldChar = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {
        template: 'test',
        widget_class: 'oe_form_field_char',
        events: {
            'change input': 'store_dom_value',
        },
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.password = this.node.attrs.password === 'True' || this.node.attrs.password === '1';
        },
        initialize_content: function() {
            this.setupFocus(this.$('input'));
        },
        store_dom_value: function () {
            if (!this.get('effective_readonly')
                && this.$('input').length
                && this.is_syntax_valid()) {
                this.internal_set_value(
                    this.parse_value(
                        this.$('input').val()));
            }
        },
        commit_value: function () {
            this.store_dom_value();
            return this._super();
        },
        render_value: function() {
            var show_value = this.format_value(this.get('value'), '');
            if (!this.get("effective_readonly")) {
                this.$el.find('input').val(show_value);
            } else {
                if (this.password) {
                    show_value = new Array(show_value.length + 1).join('*');
                }
                this.$(".oe_form_char_content").text(show_value);
            }
        },
        is_syntax_valid: function() {
            if (!this.get("effective_readonly") && this.$("input").size() > 0) {
                try {
                    this.parse_value(this.$('input').val(), '');
                    return true;
                } catch(e) {
                    return false;
                }
            }
            return true;
        },
        parse_value: function(val, def) {
            return instance.web.parse_value(val, this, def);
        },
        format_value: function(val, def) {
            return instance.web.format_value(val, this, def);
        },
        is_false: function() {
            return this.get('value') === '' || this._super();
        },
        focus: function() {
            var input = this.$('input:first')[0];
            return input ? input.focus() : false;
        },
        set_dimensions: function (height, width) {
            this._super(height, width);
            this.$('input').css({
                height: height,
                width: width
            });
        }
    });*/
}