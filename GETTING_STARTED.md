# 🚀 Quick Start Guide - New Features

## Installation

1. **Install new dependencies**:
```bash
pip install openpyxl>=3.1.0
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

2. **Verify installations**:
```bash
python -c "import plotly; import pyvis; import openpyxl; print('✅ All visualization packages installed!')"
```

## Running the Enhanced App

1. **Start the Streamlit app**:
```bash
streamlit run src/ui/app.py --server.port 8501
```

Or use the provided script:
```bash
# Windows
.\run_app.bat
# or
.\run_app.ps1

# The app will open at http://localhost:8501
```

## Exploring New Features

### 1. Chat Assistant (Tab 1)
- Same familiar interface but with enhanced visuals
- Try: "Who are the top scorers?"
- Notice the beautiful player cards with photos!

### 2. Live Dashboard (Tab 2)
- Click the **📈 Live Dashboard** tab
- View real-time metrics and leaderboards
- No configuration needed - it loads automatically!

### 3. Player Comparison (Tab 3)
- Click **🔄 Player Comparison**
- Try the "Load Sample Comparison" button for a demo
- See Haaland, Salah, and Kane compared side-by-side!

### 4. Advanced Analytics (Tab 4)
- Click **📊 Advanced Analytics**
- Select "Top Performers by Metric"
- Choose a metric (e.g., "goals"), season, and click "Analyze"
- Enjoy interactive Plotly charts!

### 5. Graph Explorer (Tab 5)
- Click **🌐 Graph Explorer**
- Select "Player Connections"
- Enter a player name (e.g., "Erling Haaland")
- Click "Explore Connections"
- Interact with the network graph (zoom, pan, hover)!

### 6. Settings & Export (Tab 6)
- Click **⚙️ Settings & Export**
- After running some queries, export your history
- Choose JSON, CSV, or Excel format
- Download your data!

## Tips for Best Experience

1. **Start with the Live Dashboard** to see the overview
2. **Use Player Comparison** to compare your favorite players
3. **Try Advanced Analytics** for deep dives into statistics
4. **Explore the Graph** to see relationships visually
5. **Export your findings** for later analysis

## Troubleshooting

### Issue: Charts not displaying
**Solution**: Ensure Plotly is installed:
```bash
pip install plotly>=5.17.0
```

### Issue: Graph visualization not working
**Solution**: Install PyVis:
```bash
pip install pyvis>=0.3.2
```

### Issue: Excel export failing
**Solution**: Install openpyxl:
```bash
pip install openpyxl>=3.1.0
```

### Issue: Player photos not loading
**Solution**: This is expected for some historical players. A generated avatar will be shown instead.

### Issue: App running slow
**Solution**: 
1. Clear cache in Settings & Export tab
2. Reduce the number of results in sidebar
3. Close unused browser tabs

## Features at a Glance

| Feature | Tab | What it does |
|---------|-----|--------------|
| 💬 Chat | 1 | Ask questions, get answers |
| 📈 Dashboard | 2 | View real-time statistics |
| 🔄 Comparison | 3 | Compare players side-by-side |
| 📊 Analytics | 4 | Deep dive into stats |
| 🌐 Graph | 5 | Visualize relationships |
| ⚙️ Settings | 6 | Export and configure |

## Example Workflows

### Workflow 1: Find Best Value Players
1. Go to **Advanced Analytics** tab
2. Select "Value Analysis"
3. Set max cost (e.g., £10m)
4. Click "Find Best Value"
5. View scatter plot and table

### Workflow 2: Compare Top Strikers
1. Go to **Player Comparison** tab
2. Click "Load Sample Comparison" (or add your own)
3. View Statistics tab for detailed comparison
4. Check Value Analysis to see who's better value
5. Use Head-to-Head for direct comparison

### Workflow 3: Explore Player Network
1. Go to **Graph Explorer** tab
2. Choose "Player Connections"
3. Enter player name
4. Click "Explore Connections"
5. Interact with the graph visualization

### Workflow 4: Export Your Research
1. Use Chat Assistant to run queries
2. Go to **Settings & Export** tab
3. Choose export format (JSON/CSV/Excel)
4. Click "Export Query History"
5. Download your file

## Performance Notes

- **First load**: May take a few seconds to initialize
- **Caching**: Data is cached for 1 hour
- **Concurrent users**: Works well with multiple users
- **Browser**: Best on Chrome/Edge/Firefox

## Keyboard Shortcuts

- `Ctrl + R` - Refresh the page
- `Ctrl + K` - Focus search box (in some tabs)
- `Esc` - Close modals/dialogs

## Need Help?

Check the main [NEW_FEATURES.md](NEW_FEATURES.md) for detailed documentation!

---

**Enjoy exploring the enhanced FPL Knowledge Graph Assistant! ⚽🚀**
