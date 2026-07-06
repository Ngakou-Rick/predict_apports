"""
Module de visualisation interactive
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class MplCanvas(FigureCanvas):
    """Canvas Matplotlib pour PyQt5"""
    
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)


class VisualizationWidget(QWidget):
    """Widget de visualisation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = None
        
    def plot_flow_comparison(self, actual: pd.Series, predicted: pd.Series, title: str = "Comparaison Réel vs Prédit"):
        """Graphique de comparaison des débits"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        self.canvas.axes.clear()
        self.canvas.axes.plot(actual.values, label='Réel', linewidth=2, alpha=0.8, color='#1f4788')
        self.canvas.axes.plot(predicted, label='Prédit', linewidth=2, alpha=0.8, color='#e74c3c', linestyle='--')
        self.canvas.axes.set_xlabel('Temps (jours)', fontsize=12)
        self.canvas.axes.set_ylabel('Débit (m³/s)', fontsize=12)
        self.canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        self.canvas.axes.legend(fontsize=10)
        self.canvas.axes.grid(True, alpha=0.3)
        
        self.canvas.fig.tight_layout()
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
    
    def plot_monthly_analysis(self, monthly_data: pd.DataFrame):
        """Graphique d'analyse mensuelle"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        self.canvas.axes.clear()
        
        months = monthly_data['mois'].values
        means = monthly_data['moyenne'].values
        
        self.canvas.axes.bar(months, means, color='#3498db', alpha=0.7, label='Moyenne')
        
        if 'min' in monthly_data.columns and 'max' in monthly_data.columns:
            mins = monthly_data['min'].values
            maxs = monthly_data['max'].values
            self.canvas.axes.fill_between(months, mins, maxs, alpha=0.2, color='#3498db', label='Min-Max')
        
        self.canvas.axes.set_xlabel('Mois', fontsize=12)
        self.canvas.axes.set_ylabel('Débit (m³/s)', fontsize=12)
        self.canvas.axes.set_title('Analyse Mensuelle des Débits', fontsize=14, fontweight='bold')
        self.canvas.axes.legend()
        self.canvas.axes.grid(True, alpha=0.3, axis='y')
        
        self.canvas.fig.tight_layout()
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
    
    def plot_correlation_heatmap(self, correlations: dict):
        """Heatmap des corrélations"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        # Préparer les données
        corr_data = {}
        for var, values in correlations.items():
            if 'pearson' in values:
                corr_data[var] = values['pearson']['correlation']
        
        if corr_data:
            df = pd.DataFrame([corr_data])
            
            self.canvas.axes.clear()
            sns.heatmap(df, annot=True, cmap='coolwarm', center=0, vmin=-1, vmax=1,
                       cbar_kws={'label': 'Corrélation'}, ax=self.canvas.axes,
                       fmt='.3f', linewidths=1)
            self.canvas.axes.set_title('Corrélations Débits-Climat', fontsize=14, fontweight='bold')
            self.canvas.axes.set_ylabel('')
            
            self.canvas.fig.tight_layout()
            self.layout.addWidget(self.canvas)
            self.canvas.draw()
    
    def plot_feature_importance(self, importance_df: pd.DataFrame):
        """Graphique d'importance des variables"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        self.canvas.axes.clear()
        
        # Top 10 features
        top_features = importance_df.head(10)
        
        self.canvas.axes.barh(top_features['feature'], top_features['importance'], color='#2ecc71')
        self.canvas.axes.set_xlabel('Importance', fontsize=12)
        self.canvas.axes.set_ylabel('Variable', fontsize=12)
        self.canvas.axes.set_title('Importance des Variables', fontsize=14, fontweight='bold')
        self.canvas.axes.grid(True, alpha=0.3, axis='x')
        
        self.canvas.fig.tight_layout()
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
    
    def plot_residuals(self, actual: pd.Series, predicted: pd.Series):
        """Graphique des résidus"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        residuals = actual.values - predicted
        
        self.canvas.axes.clear()
        self.canvas.axes.scatter(predicted, residuals, alpha=0.5, color='#e74c3c')
        self.canvas.axes.axhline(y=0, color='black', linestyle='--', linewidth=2)
        self.canvas.axes.set_xlabel('Valeurs Prédites', fontsize=12)
        self.canvas.axes.set_ylabel('Résidus', fontsize=12)
        self.canvas.axes.set_title('Analyse des Résidus', fontsize=14, fontweight='bold')
        self.canvas.axes.grid(True, alpha=0.3)
        
        self.canvas.fig.tight_layout()
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
    
    def plot_rainfall_distribution(self, rainfall_data: pd.Series):
        """Distribution des pluies"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
        
        self.canvas = MplCanvas(self, width=10, height=6)
        
        self.canvas.axes.clear()
        self.canvas.axes.hist(rainfall_data.dropna(), bins=50, color='#3498db', alpha=0.7, edgecolor='black')
        self.canvas.axes.set_xlabel('Pluie (mm)', fontsize=12)
        self.canvas.axes.set_ylabel('Fréquence', fontsize=12)
        self.canvas.axes.set_title('Distribution des Pluies', fontsize=14, fontweight='bold')
        self.canvas.axes.grid(True, alpha=0.3, axis='y')
        
        self.canvas.fig.tight_layout()
        self.layout.addWidget(self.canvas)
        self.canvas.draw()


def create_interactive_plotly(actual: pd.Series, predicted: pd.Series, title: str = "Comparaison Interactive"):
    """Crée un graphique Plotly interactif"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=actual.values,
        mode='lines',
        name='Réel',
        line=dict(color='#1f4788', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        y=predicted,
        mode='lines',
        name='Prédit',
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Temps (jours)',
        yaxis_title='Débit (m³/s)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_dashboard(data: dict):
    """Crée un tableau de bord complet"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Débits Réel vs Prédit', 'Analyse Mensuelle', 
                       'Corrélations Climat', 'Distribution des Résidus')
    )
    
    # Graphique 1: Comparaison
    if 'actual' in data and 'predicted' in data:
        fig.add_trace(
            go.Scatter(y=data['actual'], name='Réel', line=dict(color='#1f4788')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(y=data['predicted'], name='Prédit', line=dict(color='#e74c3c', dash='dash')),
            row=1, col=1
        )
    
    # Graphique 2: Mensuel
    if 'monthly' in data:
        fig.add_trace(
            go.Bar(x=data['monthly']['mois'], y=data['monthly']['moyenne'], name='Moyenne'),
            row=1, col=2
        )
    
    # Graphique 3: Corrélations
    if 'correlations' in data:
        vars_names = list(data['correlations'].keys())
        corr_values = [data['correlations'][v]['pearson']['correlation'] for v in vars_names]
        fig.add_trace(
            go.Bar(x=vars_names, y=corr_values, name='Corrélation'),
            row=2, col=1
        )
    
    # Graphique 4: Résidus
    if 'actual' in data and 'predicted' in data:
        residuals = np.array(data['actual']) - np.array(data['predicted'])
        fig.add_trace(
            go.Histogram(x=residuals, name='Résidus'),
            row=2, col=2
        )
    
    fig.update_layout(height=800, showlegend=True, title_text="Tableau de Bord Hydrologique")
    
    return fig
