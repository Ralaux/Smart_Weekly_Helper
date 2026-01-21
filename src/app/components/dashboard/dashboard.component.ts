import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { DashboardData, KpiRow } from '../../models/data.model';

declare var Plotly: any; // Use Plotly via generic

import { KpiService } from '../../services/kpi.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  data!: DashboardData;
  isDemo = false;

  constructor(private router: Router, private kpiService: KpiService) {
    const nav = this.router.getCurrentNavigation();
    if (nav?.extras.state) {
      this.data = nav.extras.state['data'];
      this.isDemo = nav.extras.state['isDemo'] || false;
    }
  }

  ngOnInit(): void {
    if (!this.data) {
      // Redirect home if no data
      this.router.navigate(['/']);
      return;
    }

    // Give time for DOM to render then plot
    setTimeout(() => {
      this.renderCharts();
    }, 100);
  }

  downloadExcel() {
    this.kpiService.exportExcel(this.data);
  }

  goBack() {
    this.router.navigate(['/']);
  }

  private renderCharts() {
    const layoutBase = {
      template: "plotly_white",
      barmode: 'stack',
      legend: { orientation: "h", yanchor: "bottom", y: 1.1, xanchor: "left", x: 0 },
      margin: { l: 50, r: 50, t: 160, b: 50 }, // Increased top margin & lower legend to fix overlap
      height: 600,
      xaxis: { type: 'category', tickmode: 'linear', dtick: 1, tickangle: -45 }
    };

    const config = { responsive: true };

    // Helper to get layout with title
    const getLayout = (title: string, barmode: string = 'stack') => ({
      ...layoutBase,
      title: { text: title, font: { size: 18 } },
      barmode: barmode
    });

    // 1. Commerce Input
    Plotly.newPlot('chart1', this.data.charts.commerceInput, getLayout('Entrées Portefeuille Commerce'), config);

    // 2. Commerce Signed
    Plotly.newPlot('chart2', this.data.charts.commerceSigned, getLayout('Projets Signés (Commerce)'), config);

    // 3. Analyse Input
    Plotly.newPlot('chart3', this.data.charts.analyseInput, getLayout('Entrées Portefeuille Analyse'), config);

    // 4. Analyse Signed
    Plotly.newPlot('chart4', this.data.charts.analyseSigned, getLayout('Projets Signés (Analyse)'), config);

    // 5. Cats
    Plotly.newPlot('chart5', this.data.charts.catCommerce, getLayout('Détail par Catégories : Entrées Portefeuille Commerce', 'group'), config);
    Plotly.newPlot('chart6', this.data.charts.catCommerceSigned, getLayout('Détail par Catégories : Projets signés', 'group'), config);
    Plotly.newPlot('chart7', this.data.charts.catAnalyse, getLayout('Détail par Catégories : Entrées Portefeuille Analyse', 'group'), config);
    Plotly.newPlot('chart8', this.data.charts.catAnalyseSigned, getLayout('Détail par Catégories : Projets signés', 'group'), config);
  }

  // --- HTML Helper for Table ---
  // We render the table using Angular/HTML instead of Plotly Table for better styling control
}
