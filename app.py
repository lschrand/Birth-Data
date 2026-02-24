import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide", page_title="Provisional Natality Data Dashboard")

st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
@st.cache_data
def load_data():
    file_path = "Provisional_Natality_2025_CDC.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error("Dataset file not found in repository.")
        st.stop()
    
    # Normalize column names
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    
    # Required logical fields
    required_fields = [
        "state_of_residence", 
        "month", 
        "month_code", 
        "year_code", 
        "sex_of_infant", 
        "births"
    ]
    
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        st.error(f"Missing required logical fields: {', '.join(missing_fields)}")
        st.write("Actual column names found:", df.columns.tolist())
        st.stop()
    
    # Convert births to numeric and drop nulls
    df['births'] = pd.to_numeric(df['births'], errors='coerce')
    df = df.dropna(subset=['births'])
    
    return df

df_raw = load_data()

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

def create_multiselect(label, options):
    selected = st.sidebar.multiselect(
        label,
        options=["All"] + sorted(list(options)),
        default=["All"]
    )
    return selected

state_sel = create_multiselect("Select State", df_raw['state_of_residence'].unique())
month_sel = create_multiselect("Select Month", df_raw['month'].unique())
sex_sel = create_multiselect("Select Gender", df_raw['sex_of_infant'].unique())

# STEP 5 — Filtering Logic
filtered_df = df_raw.copy()

if "All" not in state_sel:
    filtered_df = filtered_df[filtered_df['state_of_residence'].isin(state_sel)]

if "All" not in month_sel:
    filtered_df = filtered_df[filtered_df['month'].isin(month_sel)]

if "All" not in sex_sel:
    filtered_df = filtered_df[filtered_df['sex_of_infant'].isin(sex_sel)]

# STEP 9 — Edge Case Handling: Empty filter result
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # STEP 6 — Aggregation
    agg_df = filtered_df.groupby(['state_of_residence', 'sex_of_infant'], as_index=False)['births'].sum()
    agg_df = agg_df.sort_values('state_of_residence')

    # STEP 7 — Plot
    fig = px.bar(
        agg_df,
        x='state_of_residence',
        y='births',
        color='sex_of_infant',
        title="Total Births by State and Gender",
        labels={'births': 'Total Births', 'state_of_residence': 'State', 'sex_of_infant': 'Gender'},
        template="plotly_white",
        barmode='group'
    )
    
    fig.update_layout(
        legend_title_text='Gender',
        xaxis={'categoryorder':'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # STEP 8 — Show Filtered Table
    st.write("### Filtered Data Details")
    display_df = filtered_df[['state_of_residence', 'month', 'sex_of_infant', 'births']].reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True)
