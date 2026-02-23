import pandas as pd
import json
import plotly.express as px
import os
from nicegui import ui, app
import sys
import multiprocessing
from pathlib import Path

# Add project root to sys.path to allow 'from src...' imports if needed
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.utils import get_resource_path
from src.utils.simulator import LocalCreditSimulator
from src.utils.scoring import calculate_risk_score
from src.utils.report_gen import generate_pdf_report

# =================================================================
# ULTRA GOLD STANDARD DASHBOARD (100% PYTHON)
# Built with NiceGUI - Integrated with Risk Scoring & PDF Export.
# =================================================================

class CreditDashboard:
    def __init__(self):
        self.selected_user = 1
        self.assessment_result = ""
        self.score_data = {"score": 0, "category": "N/A", "deductions": []}
        self.report_ready = False
        self.assessment_display = None
        self.score_display = None
        self.chart_display = None
        self.btn_download = None
        
    def get_user_ids(self):
        csv_path = get_resource_path('data/utility_payments.csv')
        df = pd.read_csv(csv_path)
        return sorted(df['user_id'].unique().tolist())

    def run_assessment(self):
        """Triggers the simulator and the scoring engine."""
        try:
            simulator = LocalCreditSimulator(user_id=self.selected_user)
            self.assessment_result = simulator.run()
            
            # Internal tools for scoring
            util_raw = simulator.fetch_utility_data()
            ecom_stats = simulator.analyze_spending_data()
            
            self.score_data = calculate_risk_score(
                user_id=self.selected_user,
                utility_summary=util_raw,
                ecommerce_summary=json.dumps(ecom_stats)
            )
            self.report_ready = True
            self.refresh_ui()
            ui.notify(f'Assessment complete for User {self.selected_user}', type='positive')
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative')

    def download_report(self):
        """Generates and triggers the PDF download."""
        if self.report_ready:
            path = generate_pdf_report(self.selected_user, self.assessment_result, self.score_data)
            ui.download(path)
            ui.notify('PDF Report Generated Successfully!', type='info')

    def refresh_ui(self):
        if self.assessment_display:
            self.assessment_display.clear()
            with self.assessment_display:
                ui.markdown(f"{self.assessment_result}")
            
        if self.score_display:
            self.score_display.clear()
            with self.score_display:
                color = "text-green-500" if self.score_data['score'] >= 80 else "text-orange-500" if self.score_data['score'] >= 50 else "text-red-500"
                ui.label(f"{self.score_data['score']}/100").classes(f"text-5xl font-bold {color}")
                ui.label(f"{self.score_data['category']}").classes("text-xl font-medium text-slate-700")
                with ui.column().classes('mt-4 gap-1'):
                    for d in self.score_data['deductions']:
                        ui.label(f"• {d}").classes("text-xs text-slate-500")

        if self.chart_display:
            self.chart_display.clear()
            with self.chart_display:
                self.render_charts()
            
        if self.btn_download:
            self.btn_download.set_visibility(self.report_ready)

    def render_charts(self):
        # E-commerce Chart
        json_path = get_resource_path('data/ecommerce_spending.json')
        with open(json_path, 'r') as f:
            data = json.load(f)
        df_ecom = pd.DataFrame([t for t in data if t['user_id'] == int(self.selected_user)])
        if not df_ecom.empty:
            fig = px.bar(df_ecom, x='date', y='amount', color='category', 
                         title=f"Monthly Spending Habits",
                         color_discrete_map={"Essential": "#10B981", "Luxury": "#F43F5E"})
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            ui.plotly(fig).classes('w-full h-64')
        else:
            ui.label("No spending data available for chart.").classes('text-gray-400 italic')

    def build_ui(self):
        ui.query('body').style('background-color: #F8FAFC; font-family: "Inter", sans-serif;')

        with ui.header().classes('bg-slate-900 border-b border-slate-700 px-8 py-4 items-center justify-between shadow-lg'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('security', size='32px').classes('text-blue-400')
                ui.label('REAL-TIME CREDIT UNDERWRITING AGENT').classes('text-2xl font-black tracking-tighter text-white uppercase')
            with ui.row().classes('gap-4'):
                ui.label('ULTRA GOLD EDITION').classes('bg-blue-600/20 text-blue-400 px-3 py-1 rounded-full text-xs font-bold self-center')

        with ui.column().classes('w-full max-w-7xl mx-auto p-12 gap-12'):
            
            # 1. Dashboard Header & User Selector
            with ui.row().classes('w-full items-end justify-between'):
                with ui.column().classes('gap-1'):
                    ui.label('Portfolio Dashboard').classes('text-blue-600 font-bold uppercase text-sm tracking-widest')
                    ui.label('Applicant Assessment Center').classes('text-4xl font-extrabold text-slate-900')
                
                with ui.card().classes('p-6 bg-white border border-slate-200 shadow-sm'):
                    with ui.row().classes('items-center gap-6'):
                        ui.label('Current ID:').classes('font-bold text-slate-500')
                        ui.select(self.get_user_ids(), value=self.selected_user, 
                                 on_change=lambda e: setattr(self, 'selected_user', e.value)).classes('w-28')
                        ui.button('INITIALIZE AI AUDIT', on_click=self.run_assessment).classes('bg-blue-600 hover:bg-blue-700 text-white font-bold px-10 py-4 rounded-xl shadow-lg transition-all').props('elevated')

            # 2. Results Grid
            with ui.row().classes('w-full gap-8 items-stretch'):
                
                # Left: Agent Reasoning (Main Content)
                with ui.card().classes('flex-grow p-10 bg-white border border-slate-100 shadow-xl rounded-3xl min-h-[500px] overflow-hidden'):
                    with ui.row().classes('w-full justify-between items-center mb-6'):
                        ui.label('AGENTIC AUDIT LOG').classes('text-xs font-bold text-slate-400 tracking-widest uppercase')
                        self.btn_download = ui.button('DOWNLOAD PDF REPORT', on_click=self.download_report).classes('bg-slate-800 text-white text-xs font-bold rounded-lg').props('icon=download')
                        self.btn_download.set_visibility(False)
                    
                    self.assessment_display = ui.column().classes('w-full')
                    with self.assessment_display:
                        ui.label('Awaiting Audit Initialization...').classes('text-slate-300 italic text-2xl mt-20 text-center w-full')

                # Right: Quantitative Analytics
                with ui.column().classes('w-[35%] gap-8'):
                    # Risk Score Card
                    with ui.card().classes('w-full p-8 bg-slate-50 border border-slate-200 shadow-inner rounded-3xl'):
                        ui.label('QUANTITATIVE RISK MODEL').classes('text-xs font-bold text-slate-400 mb-4 tracking-widest uppercase text-center')
                        with ui.column().classes('items-center w-full'):
                            self.score_display = ui.column().classes('text-center')
                    
                    # Trend Chart Card
                    with ui.card().classes('w-full p-8 bg-white border border-slate-100 shadow-md rounded-3xl'):
                        ui.label('DATA VISUALIZATION').classes('text-xs font-bold text-slate-400 mb-4 tracking-widest uppercase')
                        self.chart_display = ui.column().classes('w-full')

# --- INITIALIZATION ---
dashboard = CreditDashboard()

@ui.page('/')
def main_page():
    dashboard.build_ui()

# Handle Port for Deployment
if __name__ == '__main__':
    multiprocessing.freeze_support()
    port = int(os.environ.get("PORT", 9390))
    # native=True provides a desktop window experience
    # Using reload=False and ensuring no script-mode logic
    ui.run(title='Real-Time Credit Underwriting Agent', host='0.0.0.0', port=port, dark=False, reload=False, native=True)
