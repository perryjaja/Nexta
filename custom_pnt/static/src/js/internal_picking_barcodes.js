odoo.define('custom_pnt.internal_picking_barcodes', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget= require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var fieldRegistry = require('web.field_registry');
    var dataset = require('web.data');
    var Dialog = require('web.Dialog');
    var ControlPanel = require('web.ControlPanel');
    var Pager = require('web.Pager');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;

    var MyWidget = Widget.extend({
        template: 'InternalPickingBarcodeScannerInput',
        events: {
        'keyup #internal_picking_product_barcode_read': '_onInternalProductCodebarScanned',
        'keyup #internal_picking_lot_barcode_read': '_onInternalLotCodebarScanned',
        'keyup #internal_picking_cantidad_read': '_onInternalCantidadScanned',
        },

        init: function (parent, model, state) {
            this._super(parent);
            this.model = model;
        },

    	start: function(){
            var self = this;
            this._super.apply(this, arguments);
            self.$el.html(QWeb.render('InternalPickingBarcodeScannerInput', {
                'widget': self,
                'internal_picking_product_barcode_read': '',
                'internal_picking_lot_barcode_read': '',
                'internal_picking_cantidad_read': 1,
            }));
            setTimeout(function(){
                self.$el.parent().find('#internal_picking_product_barcode_read').focus();
                self.$el.parent().find('#internal_picking_lot_barcode_read').prop('disabled', true);
                self.$el.parent().find('#internal_picking_cantidad_read').prop('disabled', true);
            }, 80);
        },

        _onInternalProductCodebarScanned: function (ev) {
            if (ev.keyCode === 13) {
                var self = this;
                var cbProducto = document.getElementById('internal_picking_product_barcode_read').value;
                var data_array = self.model.model;
                rpc.query({
                        model: 'product.product',
                        method: 'search',
                        args: [['|', ['barcode','=',cbProducto], ['default_code','=',cbProducto]]],
                }).then(function (resultado) {
                    var domain = [['id', '=', resultado[0]], ['categ_id', 'child_of', 5]]
                    rpc.query({
                        model: 'product.product',
                        method: 'search',
                        args: [domain],
                    }).then(function (ppCategLote) {
                        if (ppCategLote[0]) {
                            // Pertenece a la categoria 2 (Necesita lote)
                            self.$el.parent().find('#internal_picking_lot_barcode_read').prop('disabled', false);
                            self.$el.parent().find('#internal_picking_product_barcode_read').prop('disabled', true);
                            self.$el.parent().find('#internal_picking_cantidad_read').prop('disabled', true);
                            self.$el.parent().find('#internal_picking_lot_barcode_read').focus();
                        } else {
                            // No pertenece a la categoria 2 (No se necesita lote)
                            self.$el.parent().find('#internal_picking_product_barcode_read').prop('disabled', true);
                            self.$el.parent().find('#internal_picking_lot_barcode_read').prop('disabled', true);
                            self.$el.parent().find('#internal_picking_cantidad_read').prop('disabled', false);
                            self.$el.parent().find('#internal_picking_cantidad_read').focus();
                        }
                    });
                });
            }

        },

        _onInternalLotCodebarScanned: function (ev) {
            if (ev.keyCode === 13) {
                var self = this;
                var cbProducto = document.getElementById('internal_picking_product_barcode_read').value;
                var cbLoteProducto = document.getElementById('internal_picking_lot_barcode_read').value;
                var data_array = self.model.model;
                self.$el.parent().find('#internal_picking_product_barcode_read').prop('disabled', true);
                self.$el.parent().find('#internal_picking_lot_barcode_read').prop('disabled', true);
                self.$el.parent().find('#internal_picking_cantidad_read').prop('disabled', false);
                self.$el.parent().find('#internal_picking_cantidad_read').focus();
            }
        },

        _onInternalCantidadScanned:  function (ev) {
            if (ev.keyCode === 13) {
                var self = this;
                var cbProducto = document.getElementById('internal_picking_product_barcode_read').value;
                var cbLoteProducto = document.getElementById('internal_picking_lot_barcode_read').value;
                var cantidadProducto = document.getElementById('internal_picking_cantidad_read').value;
                var data_array = self.model.model;
                if (cbLoteProducto) {
                    rpc.query({
                            model: 'product.product',
                            method: 'search',
                            args: [['|', ['barcode','=',cbProducto], ['default_code','=',cbProducto]]],
                    }).then(function (resultado) {
                        rpc.query({
                            model: 'stock.picking',
                            method: 'onchange_internal_product_lot_read_from_js',
                            args: [[self.model.res_id],
                                cbProducto, cbLoteProducto, cantidadProducto],
                        }).then(function (booleano) {
                            if (booleano) {
                                self.__parentedParent.trigger_up('reload')
                            } else {
                                self.do_warn(_t('Warning'),
                                _t('The product cannot be added.'));
                                self.__parentedParent.trigger_up('reload')
                            }
                        });
                    });
                } else {
                    rpc.query({
                        model: 'stock.picking',
                        method: 'onchange_internal_product_read_from_js',
                        args: [[self.model.res_id], cbProducto, cantidadProducto],
                    }).then(function (booleano) {
                        if (booleano) {
                            self.__parentedParent.trigger_up('reload')
                        } else {
                            self.do_warn(_t('Warning'),
                            _t('The product cannot be added.'));
                            self.__parentedParent.trigger_up('reload')
                        }
                    });
                }
            }
        },
    });

    widgetRegistry.add(
        'widget_pnt_internal_picking_barcode_scanner', MyWidget
    );

return MyWidget;
});
