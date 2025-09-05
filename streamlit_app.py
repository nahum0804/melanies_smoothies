# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits for your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

order_filled = st.checkbox("Mark order as filled?", value=False)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),
                                                                     col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '  

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    ingredients_string = ingredients_string.rstrip(', ')  
  
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled, order_ts)
            VALUES ('{ingredients_string}', '{name_on_order}', {str(order_filled).upper()}, CURRENT_TIMESTAMP)
        """
        session.sql(my_insert_stmt).collect()

        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
