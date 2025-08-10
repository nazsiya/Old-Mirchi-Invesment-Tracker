import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import io

# Page configuration
st.set_page_config(
    page_title="Old Mirchi Investment Tracker",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #d32f2f, #f57c00);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #d32f2f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'serial_counter' not in st.session_state:
    st.session_state.serial_counter = 1
if 'message' not in st.session_state:
    st.session_state.message = None

# Header
st.markdown("""
<div class="main-header">
    <h1>🌶️ OLD MIRCHI RESTAURANT</h1>
    <h3>New Branch Investment Tracker</h3>
    <p>Real-time investment tracking with analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for data management
st.sidebar.header("📊 Data Management")

# Export data
if st.sidebar.button("📥 Export Data (JSON)"):
    if st.session_state.transactions:
        data = {
            'transactions': st.session_state.transactions,
            'serial_counter': st.session_state.serial_counter,
            'export_date': datetime.now().isoformat()
        }
        json_str = json.dumps(data, indent=2)
        st.sidebar.download_button(
            label="💾 Download JSON Backup",
            data=json_str,
            file_name=f"old_mirchi_backup_{date.today()}.json",
            mime="application/json"
        )
    else:
        st.sidebar.warning("No data to export")

# Import data
uploaded_file = st.sidebar.file_uploader("📤 Import Backup", type=['json'])
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        if 'transactions' in data:
            st.session_state.transactions = data['transactions']
            st.session_state.serial_counter = data.get('serial_counter', len(data['transactions']) + 1)
            st.session_state.message = ("success", f"Successfully imported {len(data['transactions'])} transactions!")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error importing data: {str(e)}")

# Clear data
if st.sidebar.button("🗑️ Clear All Data"):
    if st.sidebar.button("⚠️ Confirm Clear (This cannot be undone)"):
        st.session_state.transactions = []
        st.session_state.serial_counter = 1
        st.session_state.message = ("success", "All data cleared successfully")
        st.rerun()

# Display messages
if st.session_state.message:
    msg_type, msg_text = st.session_state.message
    if msg_type == "success":
        st.markdown(f'<div class="success-message">{msg_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="error-message">{msg_text}</div>', unsafe_allow_html=True)
    st.session_state.message = None

# Calculate summary statistics
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    df['date'] = pd.to_datetime(df['date'])
    total_amount = df['amount'].sum()
    total_transactions = len(df)
    avg_amount = df['amount'].mean()
    last_transaction_date = df['date'].max().strftime('%Y-%m-%d')
else:
    total_amount = 0
    total_transactions = 0
    avg_amount = 0
    last_transaction_date = "N/A"

# Summary cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Total Invested",
        value=f"₹{total_amount:,.2f}",
        delta=None
    )

with col2:
    st.metric(
        label="📊 Total Transactions",
        value=f"{total_transactions}",
        delta=None
    )

with col3:
    st.metric(
        label="📅 Last Transaction",
        value=last_transaction_date,
        delta=None
    )

with col4:
    st.metric(
        label="📈 Average Amount",
        value=f"₹{avg_amount:,.2f}",
        delta=None
    )

st.markdown("---")

# Add new transaction form
st.header("➕ Add New Transaction")

with st.form("add_transaction"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        transaction_date = st.date_input(
            "Date",
            value=date.today(),
            help="Select the transaction date"
        )
    
    with col2:
        purpose_options = [
            "Kitchen Equipment",
            "Furniture & Fixtures", 
            "Interior Design",
            "Licensing & Permits",
            "Rent & Deposit",
            "Staff Recruitment",
            "Marketing & Advertising",
            "Initial Inventory",
            "Utilities Setup",
            "Insurance",
            "Legal Fees",
            "Technology & POS",
            "Miscellaneous"
        ]
        
        purpose_type = st.selectbox("Purpose Type", ["Select from list", "Custom purpose"])
        
        if purpose_type == "Select from list":
            purpose = st.selectbox("Purpose", purpose_options)
        else:
            purpose = st.text_input("Custom Purpose", placeholder="Enter specific purpose")
    
    with col3:
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Enter the transaction amount"
        )
    
    # Submit button
    submitted = st.form_submit_button("🔥 Add Transaction", use_container_width=True)
    
    if submitted:
        if purpose and amount > 0:
            new_transaction = {
                'serial': st.session_state.serial_counter,
                'date': transaction_date.strftime('%Y-%m-%d'),
                'purpose': purpose,
                'amount': amount,
                'created_at': datetime.now().isoformat()
            }
            
            st.session_state.transactions.append(new_transaction)
            st.session_state.serial_counter += 1
            st.session_state.message = ("success", "Transaction added successfully! 🎉")
            st.rerun()
        else:
            st.session_state.message = ("error", "Please fill all required fields with valid values")
            st.rerun()

st.markdown("---")

# Display transactions
if st.session_state.transactions:
    st.header("📋 Transaction History")
    
    # Create DataFrame
    df = pd.DataFrame(st.session_state.transactions)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Display table with action buttons
    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 2, 1])
        
        with col1:
            st.write(f"#{row['serial']}")
        with col2:
            st.write(row['date'].strftime('%Y-%m-%d'))
        with col3:
            st.write(row['purpose'])
        with col4:
            st.write(f"₹{row['amount']:,.2f}")
        with col5:
            if st.button(f"🗑️", key=f"delete_{idx}", help="Delete transaction"):
                # Find and remove the transaction
                st.session_state.transactions = [
                    t for t in st.session_state.transactions 
                    if t['serial'] != row['serial']
                ]
                st.session_state.message = ("success", "Transaction deleted successfully")
                st.rerun()
    
    st.markdown("---")
    
    # Analytics section
    st.header("📊 Investment Analytics")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Purpose-wise spending
        purpose_summary = df.groupby('purpose')['amount'].sum().reset_index()
        purpose_summary = purpose_summary.sort_values('amount', ascending=False)
        
        fig_pie = px.pie(
            purpose_summary,
            values='amount',
            names='purpose',
            title="Investment by Purpose",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Monthly spending trend
        df['month'] = df['date'].dt.to_period('M')
        monthly_summary = df.groupby('month')['amount'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].astype(str)
        
        fig_bar = px.bar(
            monthly_summary,
            x='month',
            y='amount',
            title="Monthly Investment Trend",
            color='amount',
            color_continuous_scale='Reds'
        )
        fig_bar.update_layout(xaxis_title="Month", yaxis_title="Amount (₹)")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Timeline chart
    st.subheader("📈 Investment Timeline")
    fig_timeline = px.scatter(
        df,
        x='date',
        y='amount',
        size='amount',
        hover_data=['purpose', 'serial'],
        title="Investment Timeline",
        color='amount',
        color_continuous_scale='Reds'
    )
    fig_timeline.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount (₹)",
        height=400
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Export options
    st.header("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv_data = df[['serial', 'date', 'purpose', 'amount']].copy()
        csv_data['date'] = csv_data['date'].dt.strftime('%Y-%m-%d')
        csv_buffer = io.StringIO()
        csv_data.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📊 Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"old_mirchi_investments_{date.today()}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            csv_data.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Add summary sheet
            summary_data = pd.DataFrame({
                'Metric': ['Total Investment', 'Total Transactions', 'Average Amount', 'Date Range'],
                'Value': [
                    f"₹{total_amount:,.2f}",
                    str(total_transactions),
                    f"₹{avg_amount:,.2f}",
                    f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                ]
            })
            summary_data.to_excel(writer, sheet_name='Summary', index=False)
        
        st.download_button(
            label="📋 Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"old_mirchi_investments_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👆 Start by adding your first investment transaction above!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌶️ <strong>Old Mirchi Restaurant Investment Tracker</strong></p>
    <p>Built with Streamlit • Data stored in browser session</p>
    <p><em>Tip: Export your data regularly for backup!</em></p>
</div>
""", unsafe_allow_html=True)
