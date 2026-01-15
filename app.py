import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="Toronto Building Permits - Active Permits",
    page_icon="🏗️",
    layout="wide"
)

# Title and description
st.title("🏗️ Toronto Building Permits - Active Permits")
st.markdown("""
This app displays active building permits data from the City of Toronto Open Data Portal.
Data source: [Building Permits - Active Permits](https://open.toronto.ca/dataset/building-permits-active-permits/)
""")

# Data source URL - using the CSV download link from Toronto Open Data
# This URL can be overridden by setting STREAMLIT_DATA_URL environment variable
DATA_URL = os.getenv(
    "STREAMLIT_DATA_URL",
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/building-permits-active-permits/resource/d95fdb1f-3191-42b1-822a-6929b21c7ef9/download/building-permits-active-permits.csv"
)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load the building permits data from Toronto Open Data Portal"""
    try:
        df = pd.read_csv(DATA_URL)
        
        # Convert date columns to datetime if they exist
        date_columns = ['APPLICATION_DATE', 'ISSUED_DATE', 'REVISED_DATE', 'EXPIRED_DATE']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
with st.spinner("Loading building permits data..."):
    df = load_data()

if df is not None:
    # Display basic statistics
    st.header("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Active Permits", len(df))
    
    with col2:
        if 'PERMIT_TYPE' in df.columns:
            st.metric("Permit Types", df['PERMIT_TYPE'].nunique())
    
    with col3:
        if 'STRUCTURE_TYPE' in df.columns:
            st.metric("Structure Types", df['STRUCTURE_TYPE'].nunique())
    
    with col4:
        if 'CURRENT_VALUE' in df.columns and df['CURRENT_VALUE'].notna().any():
            # Convert to numeric, handling any non-numeric values
            total_value = pd.to_numeric(df['CURRENT_VALUE'], errors='coerce').sum()
            st.metric("Total Value", f"${total_value:,.0f}")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Permit Type filter
    if 'PERMIT_TYPE' in df.columns:
        permit_types = ['All'] + sorted(df['PERMIT_TYPE'].dropna().unique().tolist())
        selected_permit_type = st.sidebar.selectbox("Permit Type", permit_types)
    
    # Structure Type filter
    if 'STRUCTURE_TYPE' in df.columns:
        structure_types = ['All'] + sorted(df['STRUCTURE_TYPE'].dropna().unique().tolist())
        selected_structure_type = st.sidebar.selectbox("Structure Type", structure_types)
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'PERMIT_TYPE' in df.columns and selected_permit_type != 'All':
        filtered_df = filtered_df[filtered_df['PERMIT_TYPE'] == selected_permit_type]
    
    if 'STRUCTURE_TYPE' in df.columns and selected_structure_type != 'All':
        filtered_df = filtered_df[filtered_df['STRUCTURE_TYPE'] == selected_structure_type]
    
    st.sidebar.info(f"Showing {len(filtered_df)} of {len(df)} permits")
    
    # Visualizations
    st.header("📈 Visualizations")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Permit Types", "Structure Types", "Timeline"])
    
    with tab1:
        if 'PERMIT_TYPE' in filtered_df.columns:
            permit_counts = filtered_df['PERMIT_TYPE'].value_counts().reset_index()
            permit_counts.columns = ['Permit Type', 'Count']
            
            fig = px.bar(
                permit_counts,
                x='Permit Type',
                y='Count',
                title='Number of Permits by Type',
                labels={'Permit Type': 'Permit Type', 'Count': 'Number of Permits'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'STRUCTURE_TYPE' in filtered_df.columns:
            structure_counts = filtered_df['STRUCTURE_TYPE'].value_counts().reset_index()
            structure_counts.columns = ['Structure Type', 'Count']
            
            fig = px.pie(
                structure_counts,
                values='Count',
                names='Structure Type',
                title='Distribution of Permits by Structure Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if 'ISSUED_DATE' in filtered_df.columns:
            # Filter out rows with null dates
            timeline_df = filtered_df[filtered_df['ISSUED_DATE'].notna()].copy()
            
            if len(timeline_df) > 0:
                timeline_df['Year-Month'] = timeline_df['ISSUED_DATE'].dt.to_period('M')
                timeline_counts = timeline_df.groupby('Year-Month').size().reset_index(name='Count')
                # Sort by period to maintain chronological order
                timeline_counts = timeline_counts.sort_values('Year-Month')
                # Convert to string only for display after sorting
                timeline_counts['Year-Month'] = timeline_counts['Year-Month'].astype(str)
                
                fig = px.line(
                    timeline_counts,
                    x='Year-Month',
                    y='Count',
                    title='Permits Issued Over Time',
                    labels={'Year-Month': 'Month', 'Count': 'Number of Permits'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No date information available for timeline visualization")
    
    # Data table
    st.header("📋 Permits Data")
    
    # Select columns to display (if they exist)
    display_columns = []
    possible_columns = [
        'PERMIT_NUM', 'PERMIT_TYPE', 'STRUCTURE_TYPE', 
        'STREET_NUM', 'STREET_NAME', 'WARD',
        'APPLICATION_DATE', 'ISSUED_DATE', 'CURRENT_VALUE', 'WORK'
    ]
    
    for col in possible_columns:
        if col in filtered_df.columns:
            display_columns.append(col)
    
    # If we don't have the expected columns, just show all columns
    if not display_columns:
        display_columns = filtered_df.columns.tolist()
    
    # Show data table
    st.dataframe(
        filtered_df[display_columns].head(100),
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"Showing first 100 of {len(filtered_df)} filtered permits")
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name=f"toronto_permits_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Source:** City of Toronto Open Data Portal  
    **Last Updated:** Data is refreshed every hour  
    **Note:** This app displays a snapshot of active building permits.
    """)
else:
    st.error("Unable to load data. Please check your internet connection and try again.")
