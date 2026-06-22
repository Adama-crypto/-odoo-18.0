from odoo import models, fields, api, exceptions, _


class ShopOrder(models.Model):
    _name = 'shop.order'
    _description = 'Commande Boutique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc, id desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True
    )
    date_order = fields.Datetime(
        string='Date de commande',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    line_ids = fields.One2many(
        'shop.order.line',
        'order_id',
        string='Lignes de commande'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    amount_total = fields.Monetary(
        string='Montant total',
        compute='_compute_amount_total',
        currency_field='currency_id',
        store=True,
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('preparation', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancel', 'Annulée'),
    ], string='Statut', default='draft', required=True, tracking=True)

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture associée',
        readonly=True,
        copy=False,
    )

    # ------------------------------------------------------------------ #
    # CORRECTION 1 : amount_total doit dépendre des lignes, pas d'un
    # champ inexistant. Le compute est correct mais on garde store=True
    # pour permettre le filtrage/tri en base.
    # ------------------------------------------------------------------ #
    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))

    # ------------------------------------------------------------------ #
    # CORRECTION 2 : unlink() — OK dans l'original, on garde tel quel.
    # ------------------------------------------------------------------ #
    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise exceptions.UserError(
                    _("Vous ne pouvez supprimer que les commandes en brouillon ou annulées.")
                )
        return super().unlink()

    # ------------------------------------------------------------------ #
    # CORRECTION 3 : action_confirm
    #   - Vérifier que la commande a au moins une ligne
    #   - Utiliser virtual_available (stock prévisionnel) plutôt que
    #     qty_available uniquement, mais qty_available est suffisant ici
    #   - Le champ stock sur product.product est qty_available ; sur
    #     product.template c'est aussi qty_available. Le Many2one de la
    #     ligne pointe sur product.product → correct.
    #   - CORRECTION CRITIQUE : les invoice_line_ids doivent utiliser le
    #     champ 'name' (description) qui est obligatoire sur account.move.line
    #   - CORRECTION CRITIQUE : l'account de la ligne de facture doit être
    #     renseigné ; Odoo 17/18 le résout via product._get_product_accounts()
    #     mais il est plus sûr de laisser Odoo le calculer via onchange.
    #     La bonne pratique Odoo 18 est de passer par account.move avec
    #     invoice_line_ids en commande (0,0,{...}) et Odoo remplit le
    #     compte automatiquement si on ne le force pas.
    # ------------------------------------------------------------------ #
    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                continue

            # Vérification : au moins une ligne
            if not order.line_ids:
                raise exceptions.ValidationError(
                    _("Vous ne pouvez pas confirmer une commande sans lignes.")
                )

            # Vérification : montant total > 0
            if order.amount_total <= 0:
                raise exceptions.ValidationError(
                    _("Le montant total d'une commande doit être strictement supérieur à zéro.")
                )

            # Vérification stock pour chaque ligne
            for line in order.line_ids:
                # CORRECTION : qty_available est sur product.product
                # product_id est déjà un product.product → OK
                if line.product_id.qty_available < line.product_uom_qty:
                    raise exceptions.UserError(
                        _("Le produit '%s' est en rupture de stock (disponible : %s, demandé : %s).")
                        % (line.product_id.display_name,
                           line.product_id.qty_available,
                           line.product_uom_qty)
                    )

            # --- Génération de la facture ---
            # CORRECTION : ajouter 'name' sur chaque ligne (obligatoire en Odoo 18)
            invoice_line_vals = []
            for line in order.line_ids:
                invoice_line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.display_name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                }))

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': order.name,   # AJOUT : traçabilité
                'invoice_line_ids': invoice_line_vals,
            })
            order.invoice_id = invoice.id

            # --- Décrémentation du stock via stock.move ---
            stock_location = self.env.ref('stock.stock_location_stock')
            customer_location = self.env.ref('stock.stock_location_customers')

            for line in order.line_ids:
                move = self.env['stock.move'].create({
                    'name': _('Sortie commande %s', order.name),
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': stock_location.id,
                    'location_dest_id': customer_location.id,
                    # CORRECTION : relier le mouvement à un picking ou au
                    # moins indiquer la société pour éviter l'erreur
                    # "company_id required"
                    'company_id': order.company_id.id,
                })
                move._action_confirm()
                move._action_assign()
                # CORRECTION : en Odoo 17/18 le champ s'appelle 'qty_done'
                # sur stock.move.line, pas 'quantity' (qui est réservé)
                move.move_line_ids.write({'qty_done': line.product_uom_qty})
                move._action_done()

                # Masquage auto si rupture de stock après mouvement
                if line.product_id.qty_available <= 0:
                    line.product_id.sudo().write({'is_published': False})

            order.write({'state': 'confirmed'})

    # ------------------------------------------------------------------ #
    # CORRECTION 4 : action_cancel — idem qty_done pour le retour stock
    # ------------------------------------------------------------------ #
    def action_cancel(self):
        for order in self:
            if order.state == 'cancel':
                continue

            # Annuler la facture si elle est encore en brouillon
            if order.invoice_id and order.invoice_id.state == 'draft':
                try:
                    order.invoice_id.button_cancel()
                except Exception:
                    pass

            # Recrédit stock si la commande avait déjà déclenché des mouvements
            if order.state in ('confirmed', 'preparation', 'shipped', 'delivered'):
                stock_location = self.env.ref('stock.stock_location_stock')
                customer_location = self.env.ref('stock.stock_location_customers')
                for line in order.line_ids:
                    move = self.env['stock.move'].create({
                        'name': _('Retour annulation %s', order.name),
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': customer_location.id,
                        'location_dest_id': stock_location.id,
                        'company_id': order.company_id.id,
                    })
                    move._action_confirm()
                    move._action_assign()
                    move.move_line_ids.write({'qty_done': line.product_uom_qty})
                    move._action_done()

                    # Republier le produit si le stock redevient positif
                    if line.product_id.qty_available > 0:
                        line.product_id.sudo().write({'is_published': True})

            order.write({'state': 'cancel'})

    def action_draft(self):
        for order in self:
            if order.state != 'cancel':
                continue
            order.write({'state': 'draft'})

    def action_preparation(self):
        for order in self:
            if order.state != 'confirmed':
                continue
            order.write({'state': 'preparation'})

    def action_shipped(self):
        for order in self:
            if order.state != 'preparation':
                continue
            order.write({'state': 'shipped'})

    def action_delivered(self):
        for order in self:
            if order.state != 'shipped':
                continue
            order.write({'state': 'delivered'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('shop.order')
                    or _('Nouveau')
                )
        return super().create(vals_list)


class ShopOrderLine(models.Model):
    _name = 'shop.order.line'
    _description = 'Ligne de commande Boutique'

    order_id = fields.Many2one(
        'shop.order',
        string='Commande',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True
    )
    product_uom_qty = fields.Float(
        string='Quantité',
        required=True,
        default=1.0
    )
    price_unit = fields.Float(
        string='Prix unitaire',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='order_id.currency_id',
        store=True,
        readonly=True
    )
    price_subtotal = fields.Monetary(
        string='Sous-total',
        compute='_compute_price_subtotal',
        currency_field='currency_id',
        store=True
    )

    _sql_constraints = [
        ('qty_positive', 'CHECK(product_uom_qty > 0)',
         'La quantité doit être strictement positive.'),
        ('price_positive', 'CHECK(price_unit >= 0)',
         'Le prix unitaire doit être positif ou nul.'),
    ]

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price