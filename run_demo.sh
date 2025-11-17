#!/bin/bash
# Track 9 Hackathon Demo Launcher

echo "🏆 Track 9 - Graph-First Intelligence System Demo"
echo "=================================================="
echo ""

# Install dashboard dependencies if needed
echo "📦 Checking dependencies..."
pip install -q streamlit plotly

echo ""
echo "🚀 Launching demo dashboard..."
echo ""
echo "📊 Dashboard will open in your browser at: http://localhost:8501"
echo ""
echo "💡 TIP: Run the pipeline first:"
echo "   python main.py --emails Antler_Hackathon_Email_Data_fixed.json --output ./output_hackathon"
echo ""

# Launch Streamlit
streamlit run demo_dashboard.py --server.port=8501 --server.headless=false
