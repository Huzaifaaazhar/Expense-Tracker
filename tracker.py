import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import calendar
from datetime import datetime
import database as db

#Settings.
incomes = ["Salary", "Blog", "Other Income"]
expenses = ["Rent", "Utilities", "Groceries", "Bills", "Saving"]
currency = "USD"
page_title = "The Expense Tracker"
page_icon = ":money_with_wings:"
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

#Drop down values for selecting period.
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

#Database Interface.
def get_all_periods():
    items = db.fetch_all_period()
    periods = [item['key'] for item in items]
    return periods

#Hide StreamLit style.
hide_style = """<style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>"""
st.markdown(hide_style, unsafe_allow_html=True)

#Navigation menu.
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

#Input and save periods.
if selected == "Data Entry":
    st.header(f"Data Should be in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month: ", months, key="month")
        col2.selectbox("Select Year: ", years, key="year")

        "---"
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}: ", min_value=0, format="%i", step=10, key=income)

        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}: ", min_value=0, format="%i", step=10, key=expense)

        with st.expander("Comment"):
            comment = st.text_input("", placeholder="Enter here your comment")

        "---"
        submitted = st.form_submit_button('Submit')
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income:st.session_state[income] for income in incomes}
            expenses = {income:st.session_state[expense] for expense in expenses}
            db.insert_period(period, incomes, expenses, comment)
            st.success("Saved!")

#Plot periods using sankey chart.
if selected == "Data Visualization":
    st.header("Visualize the Periods")
    with st.form("saved_periods"):
        #Get periods from database.
        period = st.selectbox("Select Period: ", get_all_periods())
        submitted = st.form_submit_button("Plot")
        if submitted:
            period_data = db.get_period(period)
            incomes = period_data.get('incomes')
            expenses = period_data.get('expenses')
            comment = period_data.get('comment')

            #Metrices.
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining budget", f"{remaining} {currency}")
            st.text(f"Comment: {comment}")

            #Create Sankey chart.
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            #Data to dict, dict to sankey.
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color='#E694FF')
            data = go.Sankey(link=link, node=node)

            #Plot.
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0,r=0,t=5,b=5))
            st.plotly_chart(fig, use_container_width=True)