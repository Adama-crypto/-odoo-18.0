from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class ShopManagerWebsite(http.Controller):
    @http.route(['/shop_catalog'], type='http', auth="public", website=True)
    def catalog(self, **kw):
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True), 
            ('qty_available', '>', 0)
        ])
        return request.render('shop_manager.website_catalog_template', {
            'products': products
        })

class ShopManagerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(ShopManagerPortal, self)._prepare_home_portal_values(counters)
        if 'shop_order_count' in counters:
            partner = request.env.user.partner_id
            values['shop_order_count'] = request.env['shop.order'].search_count([
                ('partner_id', '=', partner.id)
            ])
        return values

    @http.route(['/my/shop_orders'], type='http', auth="user", website=True)
    def my_orders(self, **kw):
        partner = request.env.user.partner_id
        orders = request.env['shop.order'].search([('partner_id', '=', partner.id)])
        return request.render('shop_manager.portal_my_orders', {
            'orders': orders,
            'page_name': 'shop_order'
        })
        
    @http.route(['/my/shop_orders/<int:order_id>'], type='http', auth="user", website=True)
    def my_order_detail(self, order_id, **kw):
        order = request.env['shop.order'].browse(order_id)
        if not order.exists() or order.partner_id != request.env.user.partner_id:
            return request.redirect('/my/shop_orders')
        return request.render('shop_manager.portal_order_detail', {
            'order': order,
            'page_name': 'shop_order'
        })
