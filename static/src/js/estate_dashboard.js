/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks"; // Importamos el gestor de servicios de Odoo
import { Component, useState, onWillStart } from "@odoo/owl"; // Importamos onWillStart

export class EstateDashboard extends Component {
    setup() {
        // Inicializamos nuestro estado reactivo
        this.state = useState({
            soldProperties: 0,
            newProperties: 0,
            canceledProperties: 0
        });
        
        // Instanciamos el servicio ORM para hablar con la base de datos
        this.orm = useService("orm");

        // onWillStart se ejecuta ANTES de que se dibuje la pantalla
        onWillStart(async () => {
            await this.fetchData();
        });
    }

    // Función asíncrona para buscar los datos reales
    async fetchData() {
        // Realizamos una única llamada al método que creamos en Python
        const stats = await this.orm.call(
            "estate.property", 
            "get_dashboard_stats", 
            []
        );

        // Asignamos los valores recibidos al estado reactivo
        this.state.soldProperties = stats.sold;
        this.state.newProperties = stats.new;
        this.state.canceledProperties = stats.canceled;
    }

    // Botón para refrescar los datos manualmente sin recargar la página
    async refreshDashboard() {
        await this.fetchData();
    }
}

EstateDashboard.template = "estate.Dashboard";
registry.category("actions").add("estate.dashboard_action", EstateDashboard);