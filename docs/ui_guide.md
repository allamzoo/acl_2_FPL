# FPL Knowledge Graph Assistant - UI Guide

## 🎨 Official FPL Theme

The application interface is designed to match the official Fantasy Premier League website with:

### Color Scheme
- **Primary Color**: Deep Purple (#37003c) - Main brand color used throughout FPL
- **Secondary Color**: Bright Cyan/Green (#00ff87) - Accent highlights
- **Accent Color**: Pink/Magenta (#e90052) - Call-to-action buttons
- **Background**: Light Grey (#f7f7f7) - Clean, modern background
- **Cards**: White (#ffffff) - Content containers

### Design Elements
- Gradient headers matching FPL's premium look
- Card-based layout for clean information display
- Responsive design that works on all screen sizes
- Interactive hover effects and transitions
- Professional typography using Karla font family

## 🚀 Running the Application

### Quick Start

**Option 1: PowerShell Script (Recommended)**
```powershell
.\run_app.ps1
```

**Option 2: Batch File**
```cmd
run_app.bat
```

**Option 3: Direct Command**
```powershell
python -m streamlit run src/ui/app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## 📋 Features

### 1. Intelligent Query Interface
- **Natural Language Input**: Ask questions in plain English
- **Example Queries**: Quick-start with pre-defined questions
- **Real-time Processing**: Get instant answers from the knowledge graph

### 2. Sidebar Configuration
- **LLM Model Selection**: Choose from GPT-4, GPT-3.5, Gemini Pro, or Claude
- **Retrieval Methods**: 
  - Baseline (Direct Cypher queries)
  - Embeddings (Semantic search)
  - Hybrid (Combined approach)
- **Temperature Control**: Adjust response creativity
- **Result Limits**: Control number of results returned

### 3. Database Statistics
- Live stats showing:
  - Total players in database
  - Number of teams
  - Total nodes and relationships
  - Real-time connection status

### 4. Rich Results Display
- **Answer Tab**: Clean, formatted response to your question
- **Context Tab**: View retrieved data from knowledge graph
- **Analysis Tab**: See intent classification and entity extraction
- **Debug Tab**: Inspect Cypher queries and retrieval methods

### 5. Query History
- Automatically saves recent queries
- Quick access to previous results
- Expandable result cards

## 🎯 Example Use Cases

### Player Statistics
```
"Who scored the most goals this season?"
"Show me top 5 midfielders by assists"
"Which defenders have the most clean sheets?"
```

### Team Analysis
```
"Show me all Arsenal players"
"Compare Manchester City and Liverpool forwards"
"Best players from top 6 teams"
```

### Player Comparison
```
"Compare Salah and Haaland"
"Show me similar players to Kevin De Bruyne"
"Which is better value: Kane or Watkins?"
```

### Position-Specific
```
"Top goalkeepers by save percentage"
"Midfielders with most goal involvements"
"Budget defenders under 5M"
```

### Value Analysis
```
"Best value players under 7M"
"Most expensive players in each position"
"Hidden gems for FPL teams"
```

## 🔧 Configuration Options

### Model Selection
- **GPT-4**: Most accurate, slower, higher cost
- **GPT-3.5-Turbo**: Fast, cost-effective, good quality
- **Gemini Pro**: Google's model, free tier available
- **Claude-3-Sonnet**: Anthropic's balanced model

### Retrieval Methods

**Baseline (Cypher)**
- Direct database queries
- Fast and precise
- Best for exact matches

**Embeddings**
- Semantic similarity search
- Handles fuzzy queries
- Good for exploratory questions

**Hybrid (Recommended)**
- Combines both approaches
- Most versatile
- Best overall accuracy

### Temperature Settings
- **0.0 - 0.3**: Focused, factual responses (recommended for stats)
- **0.4 - 0.6**: Balanced creativity and accuracy
- **0.7 - 1.0**: More creative, varied responses

## 🎨 UI Components

### Header Section
- Prominent FPL-branded header
- Gradient purple background
- Clear application purpose

### Query Input
- Large, accessible text input
- Placeholder examples
- Search and clear buttons

### Sidebar
- Always accessible configuration
- Live database statistics
- Quick example queries

### Results Cards
- White cards with colored accents
- Tabbed interface for detailed data
- Expandable sections for history

### Color Indicators
- **Purple**: Primary actions and headers
- **Green**: Success states and metrics
- **Pink**: Action buttons
- **Blue**: Information displays
- **Orange**: Warnings

## 📱 Responsive Design

The UI automatically adapts to:
- Desktop monitors (1920px+)
- Laptops (1366px+)
- Tablets (768px+)
- Mobile devices (320px+)

## 🐛 Troubleshooting

### Application Won't Start
1. Check Python is installed: `python --version`
2. Verify Streamlit is installed: `pip show streamlit`
3. Check for port conflicts on 8501

### No Database Connection
1. Ensure Neo4j is running
2. Verify credentials in `.env` file
3. Run connection test: `python test_neo4j_connection.py`

### Slow Performance
1. Reduce max_results in sidebar
2. Use Baseline retrieval for faster queries
3. Lower temperature setting

### Styling Issues
1. Clear browser cache
2. Try incognito/private mode
3. Use Chrome/Firefox/Edge (latest versions)

## 🔐 Security Notes

- API keys stored in `.env` file (not in git)
- Database credentials isolated
- No user data collection
- Local-only by default

## 📊 Performance Tips

1. **Start with Baseline retrieval** for fastest results
2. **Use specific queries** rather than broad questions
3. **Limit results** to 10-20 for better performance
4. **Cache is enabled** - repeated queries are faster

## 🎓 Best Practices

1. **Be Specific**: "Top 5 forwards by goals" beats "good players"
2. **Use Player Names**: "Compare Salah vs Sterling" for direct comparisons
3. **Specify Positions**: "Best midfielders" filters better than "best players"
4. **Include Metrics**: "Most assists" or "highest points" for stat queries
5. **Try Examples First**: Use sidebar examples to understand query format

## 🌟 Advanced Features

### Custom Queries
For advanced users, you can:
- Write custom Cypher queries (debug mode)
- Export results to JSON
- View graph visualizations (coming soon)

### Integration
The UI can be extended with:
- Custom retrieval strategies
- Additional LLM providers
- New visualization types
- Export functionality

## 📈 Future Enhancements

Planned features:
- [ ] Interactive graph visualization
- [ ] Player comparison charts
- [ ] Form graphs and trends
- [ ] FPL team builder integration
- [ ] Transfer suggestions
- [ ] Price change predictions
- [ ] Export to CSV/PDF

## 🤝 Support

For issues or questions:
1. Check this guide first
2. Review error messages in terminal
3. Test database connection
4. Check logs in console

## 📝 Notes

- Application runs locally on your machine
- Requires active Neo4j database
- Internet connection needed for LLM APIs
- First query may be slower (model loading)

---

**Enjoy your FPL Knowledge Graph Assistant! ⚽**
