/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useState, useRef } from "@odoo/owl";
// 1. IMPORTAMOS LA FUNCIÓN PARA CARGAR LIBRERÍAS EXTERNAS
import { loadJS } from "@web/core/assets";

export class EstateDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("chartCanvas");
        this.chartInstance = null;

        this.state = useState({
            soldProperties: 0,
            newProperties: 0,
            canceledProperties: 0,
        });

        onWillStart(async () => {
            // 2. DESCARGAMOS CHART.JS ANTES DE HACER CUALQUIER OTRA COSA
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.fetchData();
        });

        onMounted(() => {
            this.renderChart();
        });
    }

    async fetchData() {
        const stats = await this.orm.call("estate.property", "get_dashboard_stats", []);
        this.state.soldProperties = stats.sold;
        this.state.newProperties = stats.new;
        this.state.canceledProperties = stats.canceled;
    }

    async refreshDashboard() {
        await this.fetchData();
        this.renderChart();
    }

    renderChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        
        if (!this.chartRef.el) return; 

        const ctx = this.chartRef.el.getContext('2d');
        
        // Ahora window.Chart sí existirá gracias a loadJS
        this.chartInstance = new window.Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Vendidas', 'Nuevas', 'Canceladas'],
                datasets: [{
                    data: [this.state.soldProperties, this.state.newProperties, this.state.canceledProperties],
                    backgroundColor: ['#198754', '#690dfd', '#212529'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}

EstateDashboard.template = "estate.Dashboard";

registry.category("actions").add("estate.dashboard_action", EstateDashboard);