import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Page configuration
st.set_page_config(page_title="Coffee Dashboard", layout="wide")

# Load the dataset
file_path = r"C:\Users\User\OneDrive\Desktop\python_dashboard_coffee\coffee.csv"
data = pd.read_csv(file_path)

# Convert 'datetime' to a datetime object for further analysis
data['datetime'] = pd.to_datetime(data['datetime'])

# Add a new 'DayType' column to classify as Weekday or Weekend
data['DayType'] = data['datetime'].dt.dayofweek.apply(lambda x: 'Weekday' if x < 5 else 'Weekend')

# Add 'Daypart' column based on the time of day
data['Hour'] = data['datetime'].dt.hour
data['Daypart'] = pd.cut(
    data['Hour'], 
    bins=[0, 12, 17, 24], 
    labels=['Morning', 'Afternoon', 'Evening'], 
    right=False, 
    include_lowest=True
)

# Add a column for the month names
data['Month'] = data['datetime'].dt.strftime('%B')  # Full month name

# Sidebar - adding filters
with st.sidebar:
    # 1. DayType filter (checkboxes)
    st.write("Select Day Type:")
    weekday_selected = st.checkbox("Weekday", value=True)
    weekend_selected = st.checkbox("Weekend", value=True)

    # Collect selected DayTypes
    daytype_selected = set()
    if weekday_selected:
        daytype_selected.add("Weekday")
    if weekend_selected:
        daytype_selected.add("Weekend")

    # If no checkbox is selected, default to showing both Weekday and Weekend data
    if not daytype_selected:
        daytype_selected = {"Weekday", "Weekend"}

    # 2. Add Month Radio Button with "All" option
    st.write("Select Month:")
    month_options = ["All"] + sorted(data['Month'].unique(), key=lambda x: pd.to_datetime(x, format='%B').month)
    month_filter = st.radio(
        "Select Month",
        options=month_options,
        index=0,  # Default to "All"
        help="Select one month or 'All' to filter transactions."
    )

    # 3. Coffee Item Dropdown
    st.write("Select Coffee Item:")
    coffee_options = ["All"] + sorted(data['coffee_name'].unique())
    item_filter = st.selectbox(
        "Select Coffee", options=coffee_options, index=0  # Default to "All"
    )

# Filter the data based on the filters
filtered_data = data.copy()

# 1. Apply DayType filter
filtered_data = filtered_data[filtered_data['DayType'].isin(daytype_selected)]

# 2. Apply Month filter (only filter if "All" is not selected)
if month_filter != "All":
    filtered_data = filtered_data[filtered_data['Month'] == month_filter]

# 3. Apply Coffee filter
if item_filter != "All":
    filtered_data = filtered_data[filtered_data['coffee_name'] == item_filter]

# Page title
st.title("Coffee Shop Dashboard")

# Create columns for a structured layout
col1, col2 = st.columns([2, 1])  # Wider left column for data, right column for summary

# Left column: Show filtered data and chart
with col1:
    # Clustered Bar Chart for coffee ranking (Horizontal)
    st.subheader("Coffee Ranking (Bar Chart)")
    coffee_counts = filtered_data['coffee_name'].value_counts()  # Count of each coffee type
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Use a more distinct color palette
    sns.barplot(y=coffee_counts.index, x=coffee_counts.values, ax=ax, palette="coolwarm") 

    # Add count labels to each bar
    for i, v in enumerate(coffee_counts.values):
        ax.text(v + 0.5, i, str(v), color='black', va='center')  # Adjust label position and color

    plt.xlabel("Count", fontsize=12)
    plt.ylabel("Coffee Name", fontsize=12)
    plt.title("Ranking of Coffee Names by Sales", fontsize=16)
    plt.grid(True, axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)

# Right column: Show summary statistics
with col2:
    
    # Total Transactions
    total_transactions = filtered_data.shape[0]
    st.metric("Total Transactions", total_transactions)
    
    # Average Price of Coffee
    avg_price = filtered_data['money'].mean()
    st.metric("Average Price Per Transaction", f"${avg_price:,.2f}")

    # Average Income Per Day
    daily_income = filtered_data.groupby(filtered_data['datetime'].dt.date)['money'].sum()
    avg_income_per_day = daily_income.mean()
    
    st.metric("Average Income Per Day", f"${avg_income_per_day:,.2f}")
    
    # Average Income Per Month
    monthly_income = filtered_data.groupby('Month')['money'].sum()
    overall_avg_income_per_month = monthly_income.mean()
    
    st.metric("Average Income Per Month", f"${overall_avg_income_per_month:,.2f}")

    # Total Sales
    total_sales = filtered_data['money'].sum()
    st.metric("Total Sales", f"${total_sales:,.2f}")

    
# Adding card visualization for total coffee sales and average price
col3, col4 = st.columns(2)

with col3:
   # Revenue of Each Month (Stacked Column Chart)
    st.subheader("Monthly Revenue (Stacked Column Chart)")
    
    # Calculate total revenue for each month and prepare data for stacked column chart
    monthly_revenue = filtered_data.groupby(['Month', 'coffee_name'])['money'].sum().unstack().fillna(0)
    
    # Plot stacked column chart
    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_revenue.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')  # Stacked bar chart with a color map
    
    # Customize the plot
    plt.title("Monthly Revenue by Coffee Type", fontsize=16)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Revenue", fontsize=12)
    plt.xticks(rotation=45)  # Rotate month names for better readability
    plt.legend(title="Coffee Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y')

    st.pyplot(fig)

    
    # Line chart: Count of Sales over time by month
    st.subheader("Count of Sales Over Time (Line Chart)")

    # Group the data by month and count the number of entries to get monthly sales count
    monthly_sales_count = filtered_data.groupby(filtered_data['datetime'].dt.to_period('M')).size()

    # Create the line plot
    fig, ax = plt.subplots(figsize=(10, 6))
    monthly_sales_count.plot(kind='line', marker='o', ax=ax, color='b', linewidth=2)

    # Customize the plot
    plt.title("Count of Sales Over Time by Month", fontsize=16)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Count of Sales", fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)

    # Display the plot in Streamlit
    st.pyplot(fig)



with col4:
    # Payment Methods Distribution (Donut Chart)
    st.subheader("Payment Methods Distribution (Donut Chart)")

    # Check if 'cash_type' column exists
    if 'cash_type' in filtered_data.columns:
        payment_counts = filtered_data['cash_type'].value_counts()
        
        # Create donut chart with distinct pastel colors
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            payment_counts,
            labels=payment_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette('pastel')[0:len(payment_counts)],
            wedgeprops={'width': 0.3}  # Set width for the donut chart
        )
        plt.title("Payment Methods Distribution", fontsize=16)
        
        # Ensure pie is a circle
        ax.axis('equal')  
        
        st.pyplot(fig)
    else:
        st.warning("The 'cash_type' column is not available in the dataset.")
