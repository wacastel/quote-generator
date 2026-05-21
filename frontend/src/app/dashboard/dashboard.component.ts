import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../../environments/environment';

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

  // We added ChangeDetectorRef here
  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  onFilesSelected(event: any) {
    this.selectedFiles = Array.from(event.target.files);
    this.previewUrls = [];
    
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
    console.log('🚀 Sending payload to backend...');

    const formData = new FormData();
    formData.append('email_text', this.emailInput);
    this.selectedFiles.forEach(file => formData.append('files', file));

    this.http.post(`${environment.apiUrl}/api/extract-quote`, formData).subscribe({
      next: (res: any) => { 
        console.log('✅ RAW RESPONSE RECEIVED:', res);
        
        // Defensive check: If the API returned a string, parse it into an object
        const parsedSpecs = typeof res === 'string' ? JSON.parse(res) : res;
        console.log('🧩 FINAL PARSED SPECS:', parsedSpecs);

        this.specs = parsedSpecs; 
        this.isProcessing = false; 
        
        // FORCE Angular to update the HTML template
        this.cdr.detectChanges();
      },
      error: (err) => { 
        console.error('❌ HTTP ERROR:', err);
        alert('Extraction failed. Check the console.'); 
        this.isProcessing = false; 
        this.cdr.detectChanges();
      }
    });
  }

  getConfidenceClass(score: string): string {
    if (score === 'Low') return 'conf-low';
    if (score === 'Medium') return 'conf-medium';
    return 'conf-high';
  }
}
