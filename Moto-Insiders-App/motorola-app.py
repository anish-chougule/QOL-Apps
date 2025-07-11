import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

# Set page configuration
st.set_page_config(
    page_title="Motorola Products Analyzer",
    page_icon="https://play-lh.googleusercontent.com/xrAQBO5EeP6FaXdh4cGfadV4jAbqdy-c93pqdpoqXxeQe7jrLjgbn6K1bnQ4hL9T_0s",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .filter-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_excel_file(uploaded_file):
    """Load Excel file and return DataFrame"""
    try:
        # Read the Excel file with header on row 1 (0-indexed)
        df = pd.read_excel(uploaded_file, sheet_name='Report_Output', header=1)
        return df, None
    except Exception as e:
        return None, str(e)

def filter_motorola_products(df):
    """Filter DataFrame for Motorola products based on the logic from your notebook"""
    try:
        # Apply the same filtering logic as in your notebook
        motorola_products = df[
            (df['Vendor Name'] == 'Ceva Logistics') & 
            (df['AR Cost'] > 0) & 
            (df['Product Name'].str.contains('Motorola', na=False)) &
            (pd.to_datetime(df['Date Created']) >= datetime.now() - timedelta(days=3))
        ]
        
        return motorola_products
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        return pd.DataFrame()

def main():
    # App header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://play-lh.googleusercontent.com/xrAQBO5EeP6FaXdh4cGfadV4jAbqdy-c93pqdpoqXxeQe7jrLjgbn6K1bnQ4hL9T_0s", width=100)
    with col2:
        st.markdown('<h1 class="main-header">Moto Insiders Submissions</h1>', unsafe_allow_html=True)


    # Sidebar
    st.sidebar.header("📂 File Upload")
    st.sidebar.markdown("Upload your Excel file to analyze Motorola products.")
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload the Sales_By_Product_Report.xlsx file"
    )
    
    if uploaded_file is not None:
        # Load the file
        with st.spinner("Loading Excel file..."):
            df, error = load_excel_file(uploaded_file)
        
        if error:
            st.error(f"Error loading file: {error}")
            return
        
        if df is not None:
            st.success(f"✅ File loaded successfully! Found {len(df)} total records.")
            
            # Show basic file info
            st.sidebar.markdown("---")
            st.sidebar.subheader("📋 File Information")
            st.sidebar.write(f"**Total Records:** {len(df)}")
            st.sidebar.write(f"**Columns:** {len(df.columns)}")
            st.sidebar.write(f"**File Name:** {uploaded_file.name}")
            
            # Filter for Motorola products
            with st.spinner("Filtering Motorola products..."):
                motorola_df = filter_motorola_products(df)
            
            if not motorola_df.empty:
                st.success(f"🎯 Found {len(motorola_df)} Motorola products!")
                
                # Main filtering section - moved to main area
                st.subheader("🔍 Filter Controls")
                
                # Create filter container
                with st.container():
                    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                    
                    # Create columns for filters
                    col1, col2, col3= st.columns(3)
                    
                    with col1:
                        # Location filter using Location Name column
                        if 'Location Name' in motorola_df.columns:
                            unique_locations = ['All'] + sorted(motorola_df['Location Name'].dropna().unique().tolist())
                            selected_location = st.selectbox(
                                "🏢 Filter by Location:",
                                unique_locations,
                                index=0
                            )
                        else:
                            st.info("📍 Location Name column not found in data")
                            selected_location = "All"
                    
                    with col2:
                        # Salesman filter (using Created By Username)
                        if 'Created By Username' in motorola_df.columns:
                            unique_salesmen = ['All'] + sorted(motorola_df['Created By Username'].dropna().unique().tolist())
                            selected_salesman = st.selectbox(
                                "👤 Filter by Salesman:",
                                unique_salesmen,
                                index=0
                            )
                        else:
                            st.info("👤 Salesman column not found in data")
                            selected_salesman = "All"
                    
                    with col3:
                        # Product model filter
                        if 'Product Name' in motorola_df.columns:
                            unique_products = ['All'] + sorted(motorola_df['Product Name'].dropna().unique().tolist())
                            selected_product = st.selectbox(
                                "📱 Filter by Product:",
                                unique_products,
                                index=0
                            )
                        else:
                            selected_product = "All"
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Apply filters
                filtered_df = motorola_df.copy()
                
                
                # Apply location filter
                if selected_location != "All":
                    filtered_df = filtered_df[filtered_df['Location Name'] == selected_location]
                
                # Apply salesman filter
                if selected_salesman != "All":
                    filtered_df = filtered_df[filtered_df['Created By Username'] == selected_salesman]
                
                # Apply product filter
                if selected_product != "All":
                    filtered_df = filtered_df[filtered_df['Product Name'] == selected_product]
                
                # Show filter results
                filter_info = []
                if selected_location != "All":
                    filter_info.append(f"Location: {selected_location}")
                if selected_salesman != "All":
                    filter_info.append(f"Salesman: {selected_salesman}")
                if selected_product != "All":
                    filter_info.append(f"Product: {selected_product}")
                
                if filter_info:
                    st.info(f"🔍 Filters applied ({', '.join(filter_info)}): Showing {len(filtered_df)} of {len(motorola_df)} records")
                
                # Main data table
                st.subheader("📊 Motorola Submissions Table")
                
                # Select columns to display
                display_columns = ['Date Created', 'Created By Username', 'Product Name', 'Tracking #']
                
                # Add column selection in sidebar
                st.sidebar.markdown("---")
                st.sidebar.subheader("🎛️ Display Options")
                
                all_columns = motorola_df.columns.tolist()
                selected_columns = st.sidebar.multiselect(
                    "Select columns to display:",
                    all_columns,
                    default=display_columns
                )
                
                if selected_columns:
                    # Display the filtered data
                    st.dataframe(
                        filtered_df[selected_columns],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Add download button
                    st.subheader("💾 Download Results")
                    
                    # Convert to CSV for download
                    csv = filtered_df[selected_columns].to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"motorola_products_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Convert to Excel for download
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        filtered_df[selected_columns].to_excel(writer, sheet_name='Motorola_Products', index=False)
                    
                    st.download_button(
                        label="📥 Download as Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"motorola_products_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Show some basic statistics in the sidebar
                st.sidebar.markdown("---")
                st.sidebar.subheader("📊 Summary Statistics")
                st.sidebar.write(f"**Total Filtered Records:** {len(filtered_df)}")
                if 'Date Created' in filtered_df.columns and not filtered_df.empty:
                    filtered_df['Date Created'] = pd.to_datetime(filtered_df['Date Created'])
                    latest_date = filtered_df['Date Created'].max().strftime('%Y-%m-%d')
                    oldest_date = filtered_df['Date Created'].min().strftime('%Y-%m-%d')
                    st.sidebar.write(f"**Date Range:** {oldest_date} to {latest_date}")
            
            else:
                st.warning("⚠️ No Eligible Motorola Devices were found matching the criteria.")
    
    else:
        # Show instructions when no file is uploaded
        st.info("👆 Please upload an Excel file using the sidebar to get started.")
        
        st.subheader("📋 Instructions")
        st.write("""
        1. **Upload File**: Use the file uploader in the sidebar to upload your Excel file
        2. **Filter Results**: Use the filter controls to narrow down by location, salesman, or product
        3. **Last 3 Days**: Check the "Show Last 3 Days Only" option to view recent transactions
        4. **View Results**: The table will update automatically based on your filters
        5. **Customize Display**: Select which columns to show using the sidebar options
        6. **Download**: Export your filtered results as CSV or Excel format
        """)
        
       

if __name__ == "__main__":
    main()
