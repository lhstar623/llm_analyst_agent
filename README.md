# 📊 AI Data Analyst - Streamlit Interface

A powerful Streamlit web application that provides an intuitive interface for the AI Data Analyst agent. Upload your CSV data, ask questions, and get comprehensive analysis with visualizations and insights.

## 🚀 Features

- **📤 Easy CSV Upload**: Drag and drop or browse to upload your dataset
- **💬 Natural Language Queries**: Ask questions about your data in plain English
- **📊 Comprehensive Analysis**: Get statistical insights, trends, and patterns
- **📈 Interactive Visualizations**: HTML charts with PNG fallback for reliability
- **📋 Analysis History**: Keep track of all your previous analyses
- **💾 Export Results**: Download reports in Markdown and summary formats
- **🔄 Real-time Processing**: Async processing with progress indicators

## 🛠️ Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd data-analyst
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LOGFIRE_TOKEN=your_logfire_token_here
   ```

## 🚀 Usage

### Method 1: Using the Run Script (Recommended)
```bash
python run_analyst_app.py
```

### Method 2: Direct Streamlit Command
```bash
streamlit run streamlit_analyst_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

### 1. Upload Your Data
- Click on "Choose a CSV file" or drag and drop your CSV file
- Preview your data to ensure it loaded correctly
- Check the sidebar for file information (rows, columns, column names)

### 2. Ask Your Question
Enter your analysis query in natural language, such as:
- "What are the key trends in this sales data?"
- "Show me correlations between different variables"
- "Identify outliers and anomalies in the dataset"
- "Create visualizations to summarize the main findings"
- "What insights can you provide about customer behavior?"

### 3. Get Results
The app will process your request and provide:
- **📄 Analysis Report**: Comprehensive markdown-formatted analysis
- **📈 Key Metrics**: Calculated statistical values and measurements
- **🖼️ Visualizations**: Interactive HTML charts (with PNG fallback)
- **💡 Conclusion**: Summary with actionable recommendations

### 4. Explore and Export
- Navigate through different tabs to explore results
- View your analysis history in the sidebar
- Download reports and summaries for offline use

## 🎯 Example Queries

Here are some example queries you can try:

### General Analysis
- "Perform exploratory data analysis on this dataset"
- "What are the key statistical insights?"
- "Summarize the main patterns and trends"

### Specific Analysis
- "What factors influence sales performance?"
- "Are there seasonal trends in the data?"
- "Which variables are most correlated?"
- "Identify the top performing categories"

### Visual Analysis
- "Create a correlation heatmap"
- "Show distribution plots for numerical columns"
- "Generate time series plots if applicable"
- "Create comparative visualizations"

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **Backend**: Pydantic AI agent with OpenAI GPT-4
- **Analysis Engine**: Python with pandas, matplotlib, seaborn
- **Async Processing**: asyncio for non-blocking operations

### File Handling
- Temporary file storage for uploaded CSVs
- Automatic cleanup of temporary files
- Support for various CSV formats and encodings

### Visualization Strategy
1. **Primary**: HTML interactive charts (using plotly/matplotlib)
2. **Fallback**: PNG static images for compatibility
3. **Error Handling**: Graceful degradation with informative messages

## 🐛 Troubleshooting

### Common Issues

**File Upload Problems**:
- Ensure your file is in CSV format
- Check that the file isn't corrupted
- Verify column headers are properly formatted

**Analysis Errors**:
- Make sure your query is clear and specific
- Check that your data has sufficient rows/columns for analysis
- Verify API keys are correctly set in the `.env` file

**Visualization Issues**:
- If HTML charts don't load, the PNG fallback will display
- Clear browser cache if visualizations appear broken
- Check that all required packages are installed

**Performance Issues**:
- Large datasets (>10MB) may take longer to process
- Complex queries require more processing time
- Consider breaking down complex requests into simpler ones

### Error Messages

- **"Please upload a CSV file first"**: Upload a dataset before analysis
- **"Please enter an analysis query"**: Provide a question or analysis request
- **"Analysis failed"**: Check your data format and query clarity
- **"No visualizations available"**: The analysis may not have generated charts

## 📚 Dependencies

Key packages used:
- `streamlit`: Web interface framework
- `pandas`: Data manipulation and analysis
- `matplotlib/seaborn`: Statistical visualizations
- `pydantic-ai`: AI agent framework
- `openai`: Language model integration
- `asyncio`: Asynchronous processing

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the error messages in the app
3. Ensure all dependencies are properly installed
4. Verify your environment variables are set correctly

---

**Happy Analyzing! 📊🚀**
