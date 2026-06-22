/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ITDashboard extends Component {
    static template = "it_parc.Dashboard";

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            totalEquipements: 0,
            equipementsAffectes: 0,
            equipementsMaintenance: 0,
            interventionsEnCours: 0,
            equipementsParCategorie: [],
            interventionsParMois: [],
            // Add a computed max value for the bar chart scaling
            maxEquipementsParCategorie: 0,
            maxInterventionsParMois: 0,
        });

        onWillStart(async () => {
            await this.fetchData();
        });
    }

    async fetchData() {
        const data = await this.rpc("/it_parc/dashboard/data");
        this.state.totalEquipements = data.total_equipements;
        this.state.equipementsAffectes = data.equipements_affectes;
        this.state.equipementsMaintenance = data.equipements_maintenance;
        this.state.interventionsEnCours = data.interventions_en_cours;
        this.state.equipementsParCategorie = data.equipements_par_categorie;
        this.state.interventionsParMois = data.interventions_par_mois;
        
        if (data.equipements_par_categorie.length > 0) {
            this.state.maxEquipementsParCategorie = Math.max(...data.equipements_par_categorie.map(i => i.count)) || 1;
        }
        if (data.interventions_par_mois.length > 0) {
            this.state.maxInterventionsParMois = Math.max(...data.interventions_par_mois.map(i => i.count)) || 1;
        }
    }
}

registry.category("actions").add("it_dashboard_action", ITDashboard);
