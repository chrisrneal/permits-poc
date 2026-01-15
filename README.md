# Toronto Building Permits - Active Permits

A Streamlit web application to visualize and explore active building permits data from the City of Toronto Open Data Portal.

## Features

- 📊 Interactive data visualizations (bar charts, pie charts, timeline)
- 🔍 Filter permits by type and structure type
- 📋 Browse detailed permit information
- 📥 Download filtered data as CSV
- 🔄 Auto-refreshing data (cached for 1 hour)

## Data Source

This app uses the [Building Permits - Active Permits](https://open.toronto.ca/dataset/building-permits-active-permits/) dataset from the City of Toronto Open Data Portal.

## Running Locally

1. Clone the repository:
```bash
git clone https://github.com/chrisrneal/permits-poc.git
cd permits-poc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deploying to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select this repository, branch, and `app.py` as the main file
6. Click "Deploy"

Your app will be live at `https://share.streamlit.io/[username]/permits-poc/main/app.py`

## Requirements

- Python 3.8+
- streamlit
- pandas
- requests
- plotly

See `requirements.txt` for specific versions.

## License

This project is open source and available under the MIT License.
