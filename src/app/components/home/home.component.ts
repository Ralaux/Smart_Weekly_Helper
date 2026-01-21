import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // Need CommonModule in standalone usually, or imports array
import { Router } from '@angular/router';
import { KpiService } from '../../services/kpi.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {

  isLoading = false;
  errorMsg = '';

  constructor(private kpiService: KpiService, private router: Router) { }

  async onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.isLoading = true;
    this.errorMsg = '';

    try {
      const rawData = await this.kpiService.loadData(file);
      const dashboardData = this.kpiService.calculateDashboard(rawData);

      // Navigate to dashboard with state
      this.router.navigate(['/dashboard'], { state: { data: dashboardData } });
    } catch (err) {
      console.error(err);
      this.errorMsg = "Impossible de lire le fichier. Assurez-vous qu'il s'agit d'un fichier Excel valide.";
      this.isLoading = false;
    }
  }

  launchDemo() {
    this.isLoading = true;
    setTimeout(() => { // Small fake delay for UX
      const demoData = this.kpiService.generateDemoData();
      this.router.navigate(['/dashboard'], { state: { data: demoData, isDemo: true } });
    }, 800);
  }
}
