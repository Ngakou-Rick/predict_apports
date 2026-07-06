"""
Module d'export des résultats (Excel et PDF)
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Dict


class ReportGenerator:
    """Génère des rapports Excel et PDF"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def export_to_excel(self, data: Dict, filename: str) -> str:
        """Export les résultats vers Excel"""
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Données brutes
            if 'data' in data:
                data['data'].to_excel(writer, sheet_name='Données', index=False)
            
            # Prédictions
            if 'predictions' in data:
                pred_df = pd.DataFrame(data['predictions'])
                pred_df.to_excel(writer, sheet_name='Prédictions', index=False)
            
            # Métriques
            if 'metrics' in data:
                metrics_df = pd.DataFrame(data['metrics'])
                metrics_df.to_excel(writer, sheet_name='Métriques', index=False)
            
            # Analyse mensuelle
            if 'monthly_analysis' in data:
                monthly_df = pd.DataFrame(data['monthly_analysis'])
                monthly_df.to_excel(writer, sheet_name='Analyse Mensuelle', index=False)
            
            # Corrélations climatiques
            if 'climate_correlations' in data:
                corr_df = pd.DataFrame(data['climate_correlations'])
                corr_df.to_excel(writer, sheet_name='Corrélations Climat', index=False)
        
        return filepath
    
    def create_prediction_plot(self, actual: pd.Series, predicted: pd.Series, title: str) -> str:
        """Crée un graphique de comparaison réel vs prédit"""
        plt.figure(figsize=(12, 6))
        plt.plot(actual.values, label='Réel', linewidth=2, alpha=0.7)
        plt.plot(predicted, label='Prédit', linewidth=2, alpha=0.7)
        plt.xlabel('Temps')
        plt.ylabel('Débit (m³/s)')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'prediction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_correlation_heatmap(self, correlations: Dict, title: str) -> str:
        """Crée une heatmap des corrélations"""
        if not correlations:
            return None
        
        # Préparer les données
        corr_data = {}
        for var, values in correlations.items():
            if 'pearson' in values:
                corr_data[var] = values['pearson']['correlation']
        
        if not corr_data:
            return None
        
        plt.figure(figsize=(10, 6))
        df = pd.DataFrame([corr_data])
        sns.heatmap(df, annot=True, cmap='coolwarm', center=0, vmin=-1, vmax=1, cbar_kws={'label': 'Corrélation'})
        plt.title(title)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'correlation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def export_to_pdf(self, data: Dict, filename: str) -> str:
        """Génère un rapport PDF professionnel"""
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Style personnalisé
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        # Titre
        story.append(Paragraph("Rapport de Prévision Hydrologique", title_style))
        story.append(Paragraph(f"Barrage de Mbakaou", styles['Heading2']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Informations générales
        if 'season_info' in data:
            story.append(Paragraph("Informations sur la saison", heading_style))
            info_data = [
                ['Saison', data['season_info'].get('saison', 'N/A')],
                ['Année', data['season_info'].get('annee', 'N/A')],
                ['Modèle utilisé', data['season_info'].get('modele', 'N/A')]
            ]
            info_table = Table(info_data, colWidths=[3*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Métriques de performance
        if 'metrics' in data:
            story.append(Paragraph("Métriques de Performance", heading_style))
            metrics = data['metrics']
            if 'test' in metrics:
                metrics_data = [
                    ['Métrique', 'Valeur'],
                    ['RMSE', f"{metrics['test'].get('RMSE', 0):.4f}"],
                    ['MAE', f"{metrics['test'].get('MAE', 0):.4f}"],
                    ['R²', f"{metrics['test'].get('R2', 0):.4f}"]
                ]
                metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 0.2*inch))
        
        # Graphiques
        if 'plot_paths' in data:
            for plot_path in data['plot_paths']:
                if os.path.exists(plot_path):
                    story.append(PageBreak())
                    story.append(Paragraph("Visualisations", heading_style))
                    img = Image(plot_path, width=6*inch, height=3*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
        
        # Construire le PDF
        doc.build(story)
        return filepath
    
    def generate_training_report(self, optimization_results: Dict, model_name: str, 
                                 season_info: Dict, filepath: str) -> str:
        """Génère un rapport PDF d'entraînement optimisé"""
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1
        )
        
        # Titre
        story.append(Paragraph("Rapport d'Entraînement Optimisé", title_style))
        story.append(Paragraph(f"Modèle: {model_name}", styles['Heading2']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Informations générales
        story.append(Paragraph("Informations Générales", styles['Heading2']))
        info_data = [
            ['Saison', season_info.get('saison', 'N/A')],
            ['Période entraînement', season_info.get('train_period', 'N/A')],
            ['Période test', season_info.get('test_period', 'N/A')],
            ['Nombre d\'itérations', str(optimization_results['total_iterations'])]
        ]
        info_table = Table(info_data, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Meilleure configuration
        story.append(Paragraph("Meilleure Configuration Trouvée", styles['Heading2']))
        best_params = optimization_results.get('best_params', {})
        
        # Gérer le cas où best_params est None ou vide
        if best_params is None:
            best_params = {}
        
        params_data = [['Paramètre', 'Valeur']]
        if best_params:
            for key, value in best_params.items():
                params_data.append([str(key), str(value)])
        else:
            params_data.append(['Aucun paramètre', 'N/A'])
        
        params_table = Table(params_data, colWidths=[3*inch, 3*inch])
        params_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(params_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Meilleures métriques
        story.append(Paragraph("Meilleures Métriques", styles['Heading2']))
        best_iteration = [h for h in optimization_results['history'] if h.get('is_best', False)][-1]
        metrics_data = [
            ['Métrique', 'Entraînement', 'Test'],
            ['R²', f"{best_iteration['train_r2']:.4f}", f"{best_iteration['test_r2']:.4f}"],
            ['RMSE', f"{best_iteration['train_rmse']:.4f}", f"{best_iteration['test_rmse']:.4f}"],
            ['MAE', f"{best_iteration['train_mae']:.4f}", f"{best_iteration['test_mae']:.4f}"]
        ]
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(metrics_table)
        story.append(PageBreak())
        
        # Graphique évolution R²
        story.append(Paragraph("Évolution du R² par Itération", styles['Heading2']))
        plot_path = self._create_r2_evolution_plot(optimization_results['history'])
        if plot_path and os.path.exists(plot_path):
            img = Image(plot_path, width=6*inch, height=3*inch)
            story.append(img)
        
        story.append(PageBreak())
        
        # Historique des itérations (top 10)
        story.append(Paragraph("Top 10 Meilleures Itérations", styles['Heading2']))
        sorted_history = sorted(optimization_results['history'], 
                               key=lambda x: x['test_r2'], reverse=True)[:10]
        
        history_data = [['#', 'R² Test', 'RMSE Test', 'MAE Test', 'Temps (s)']]
        for h in sorted_history:
            history_data.append([
                str(h['iteration']),
                f"{h['test_r2']:.4f}",
                f"{h['test_rmse']:.4f}",
                f"{h['test_mae']:.4f}",
                f"{h['time']:.2f}"
            ])
        
        history_table = Table(history_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(history_table)
        
        # Construire le PDF
        doc.build(story)
        return filepath
    
    def _create_r2_evolution_plot(self, history: list) -> str:
        """Crée un graphique d'évolution du R²"""
        plt.figure(figsize=(10, 5))
        
        iterations = [h['iteration'] for h in history]
        train_r2 = [h['train_r2'] for h in history]
        test_r2 = [h['test_r2'] for h in history]
        
        plt.plot(iterations, train_r2, label='R² Entraînement', marker='o', alpha=0.7)
        plt.plot(iterations, test_r2, label='R² Test', marker='s', alpha=0.7)
        plt.xlabel('Itération')
        plt.ylabel('R²')
        plt.title('Évolution du R² par Itération')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'r2_evolution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
