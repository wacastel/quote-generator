import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
  emailInput: string = 'Hi team,\nAttached is a sketch for a new custom hanging sign. We need 100 of these for our midwest stores. Weather resistant material, die-cut shape.\nCan you handle?';
  selectedFiles: File[] = [];
  previewUrls: string[] = [];
  
  isProcessing = false;
  specs: any = null;
  showPreview = false;

  constructor(private http: HttpClient) {}

  onFilesSelected(event: any) {
    this.selectedFiles = Array.from(event.target.files);
    this.previewUrls = [];
    
    // Create localized image previews for the left pane
    this.selectedFiles.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e: any) => this.previewUrls.push(e.target.result);
        reader.readAsDataURL(file);
      }
    });
  }

  extractSpecs() {
    this.isProcessing = true;
    const formData = new FormData();
    formData.append('email_text', this.emailInput);
    this.selectedFiles.forEach(file => formData.append('files', file));

    this.http.post('http://localhost:8000/api/extract-quote', formData).subscribe({
      next: (res: any) => { this.specs = res; this.isProcessing = false; },
      error: (err) => { alert('Extraction failed.'); this.isProcessing = false; }
    });
  }

  // Dynamic CSS Class Assignment
  getConfidenceClass(score: string): string {
    if (score === 'Low') return 'conf-low';
    if (score === 'Medium') return 'conf-medium';
    return 'conf-high';
  }
}
