from itertools import count
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MAGNIFIQUE!!!", page_icon=":handbag:", layout="wide")

# Custom CSS for Streamlit components and page background
st.title(" :handbag: MAGNIFIQUE ANALYSIS")

st.markdown(
    """
    <style>
    body {
        background-color: #000000; /* Black background */
        color: #ffffff; /* White text color */
        font-family: Arial, sans-serif; /* Optional: Set a preferred font */
    }
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh; /* Adjust as needed for vertical centering */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# File uploader
df = pd.read_csv("E:\Downloads\internship\Final Mag Data1.csv", encoding="ISO-8859-1")


# Parse order_date column to datetime
df["Order_date"] = pd.to_datetime(df["Order_date"], format='%d-%m-%Y', errors='coerce')

# Drop rows with NaT values if any date strings couldn't be parsed
df = df.dropna(subset=["Order_date"])

# Getting the min and max date
startDate = df["Order_date"].min()
endDate = df["Order_date"].max()

# Check if startDate and endDate are valid
if pd.isnull(startDate) or pd.isnull(endDate):
    st.error("The dataset contains invalid dates.")
else:
    # Create Streamlit columns
    col1, col2 = st.columns(2)

    with col1:
        date1 = st.date_input("Start Date", startDate)

    with col2:
        date2 = st.date_input("End Date", endDate)

    # Convert the selected dates to datetime
    date1 = pd.to_datetime(date1)
    date2 = pd.to_datetime(date2)

    # Filter the DataFrame based on the selected date range
    df_filtered = df[(df["Order_date"] >= date1) & (df["Order_date"] <= date2)].copy()

    st.sidebar.header("Choose your filter:")

        # Create filters
    state = st.sidebar.multiselect("Select State", df["end_customer_state"].unique())
    if not state:
        df2 = df.copy()
    else:
        df2 = df[df["end_customer_state"].isin(state)]

    quantity = st.sidebar.multiselect("Select Quantity", df["quantity"].unique())
    if not quantity:
        df2 = df.copy()
    else:
        df2 = df[df["quantity"].isin(quantity)]

    order_status = st.sidebar.multiselect("Select Order Status", df["order_status"].unique())
    if not order_status:
        df2 = df.copy()
    else:
        df2 = df[df["order_status"].isin(order_status)]

    product_range = st.sidebar.multiselect("Select Product Range", df["Product Range"].unique())
    if not product_range:
        df2 = df.copy()
    else:
        df2 = df[df["Product Range"].isin(product_range)]



        # Filter the data based on purpose, start, and stop location
       # Filter the data based on the selected filters
    if not state and not quantity and not order_status and not product_range:
        filtered_df = df
    elif not quantity and not order_status and not product_range:
        filtered_df = df[df["end_customer_state"].isin(state)]
    elif not state and not order_status and not product_range:
        filtered_df = df[df["quantity"].isin(quantity)]
    elif not state and not quantity and not product_range:
        filtered_df = df[df["order_status"].isin(order_status)]
    elif not state and not quantity and not order_status:
        filtered_df = df[df["Product Range"].isin(product_range)]
    elif state and quantity and order_status:
        filtered_df = df[df["end_customer_state"].isin(state) & df["quantity"].isin(quantity) & df["order_status"].isin(order_status)]
    elif state and order_status and product_range:
        filtered_df = df[df["end_customer_state"].isin(state) & df["order_status"].isin(order_status) & df["Product Range"].isin(product_range)]
    elif state and quantity and product_range:
        filtered_df = df[df["end_customer_state"].isin(state) & df["quantity"].isin(quantity) & df["Product Range"].isin(product_range)]
    elif quantity and order_status and product_range:
        filtered_df = df[df["quantity"].isin(quantity) & df["order_status"].isin(order_status) & df["Product Range"].isin(product_range)]
    else:
        filtered_df = df[
            (df["end_customer_state"].isin(state) if state else True) &
            (df["quantity"].isin(quantity) if quantity else True) &
            (df["order_status"].isin(order_status) if order_status else True) &
            (df["Product Range"].isin(product_range) if product_range else True)
        ]

    category_df = filtered_df.groupby(by=["Product Range"], as_index=False)["Final Price"].sum()
    category_df1 = filtered_df.groupby(by=["end_customer_state"], as_index=False)["Final Price"].sum()
    category_df2 = filtered_df.groupby(by=["Product Range"], as_index=False)["quantity"].sum()
    category_df3 = filtered_df.groupby(by=["end_customer_state"], as_index=False)["quantity"].sum()
    category_df4 = filtered_df.groupby(by=["end_customer_state"], as_index=False).agg({"Final Price": "sum", "quantity": "sum"})
    category_df5 = filtered_df.groupby(by=["Product Range"], as_index=False).agg({"Final Price": "sum", "quantity": "sum"})



         # Plotting
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Range Wise Sales")
        fig = px.pie(filtered_df, values="Final Price", names="Product Range", hole=0.5)
        fig.update_traces(text=filtered_df["Final Price"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        fig = px.bar(category_df2, x="Product Range", y="quantity", template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("State Wise Sales")
        fig = px.pie(filtered_df, values="Final Price", names="end_customer_state", hole=0.4)
        fig.update_traces(text=filtered_df["Final Price"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(category_df3, x="end_customer_state", y="quantity", template="seaborn")
        fig.update_layout(height=700, width=700)
        st.plotly_chart(fig, use_container_width=True)


    cl1, cl2 = st.columns(2)

with cl1:
    with st.expander("Range Wise Sales Data"):
        st.write(category_df5.style.background_gradient(cmap="Blues"))
        csv = category_df5.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Range Sales.csv", mime="text/csv",
                           help='Click here to download the data as a csv file')
        
with cl2:
    with st.expander("State Wise Sales Data "):
        state = filtered_df.groupby(by=["end_customer_state"], as_index=False)["Final Price"].sum()
        st.write(category_df4.style.background_gradient(cmap="Oranges"))
        csv = category_df4.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="State Sales.csv", mime="text/csv",
                           help='Click here to download the data as a csv file')
        
        
 # Additional Time Series Analysis with both Final Price and Quantity
filtered_df["Order_date"] = filtered_df["Order_date"].dt.to_period("D")
st.subheader('Time Series Analysis')
linechart = filtered_df.groupby(filtered_df["Order_date"].dt.strftime("%Y-%m-%d")).agg({"Final Price": "sum", "quantity": "sum"}).reset_index()
linechart = linechart.rename(columns={"Order_date": "Order Date"})

fig2 = px.line(linechart, x="Order Date", y=["Final Price", "quantity"], labels={"value": "", "variable": "Metric"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("CLICK TO VIEW TIMESERIES DATA"):
    st.write(linechart.T.style.background_gradient(cmap="Oranges"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv",
                       help='Click here to download the data as a csv file') 
    
with st.expander("Click to download original dataset"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="E:\Downloads\shahbaz\ForwardReports_Clean.csv", mime="text/csv")
