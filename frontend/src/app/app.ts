import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
// 1. Import the Dashboard Component
import { DashboardComponent } from './dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  // 2. Add it to the imports array here
  imports: [CommonModule, DashboardComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  title = 'ImageWorks Quote Generator';
}
