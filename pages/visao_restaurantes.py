#Libraries
import pandas as pd
import numpy as np
import re
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static



#Importação do arquivo
df_raw = pd.read_csv('dataset/train.csv')



# Realizando cópia do DataFrame para manipulação:
df = df_raw.copy()
   

#Excluir as linhas com Nan
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias,:]

linhas_vazias = df['City'] != 'NaN '
df = df.loc[linhas_vazias,:]

linhas_vazias = df['Road_traffic_density'] != 'NaN '
df = df.loc[linhas_vazias,:]

linhas_vazias = df['Festival'] != 'NaN '
df = df.loc[linhas_vazias,:]


#Conversão de dados da coluna 'Delivery_person_age' de object para int:
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype('int64')

#Conversão de dados da coluna 'Delivery_person_Ratings' de object para float:
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype('float64')

#Conversão de dados da coluna 'Order_Date' de object para datetime:
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

# Remove as linhas da culuna multiple_deliveries que tenham o 
# conteudo igual a 'NaN '
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( 'int64' )


#Remover espaço em branco das colunas ID e Delivery_person_ID:
df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
df.loc[:,'City'] = df.loc[:,'City'].str.strip()
df.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()

#Limpeza de coluna Time Taken
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df['Time_taken(min)'] = df['Time_taken(min)'].astype( 'int64' )

#==============================
# Barra lateral no Streamlit
#==============================
import streamlit as st
st.header('Marketplace - Visão Entregadores')

image_path = 'logo3.png'
image = Image.open(image_path)
st.sidebar.image(image, width=220)


st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite :calendar:')
data_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022,4,13),min_value=pd.datetime(2022,2,11), max_value=pd.datetime(2022,4,6), format='DD-MM-YYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium','High','Jam'], 
    default =['Low','Medium','High','Jam'] )
st.sidebar.markdown("""---""")

Weatherconditions = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Sunny','conditions Stormy','conditions Sandstorms','conditions Cloudy','conditions Fog','conditions Windy'], 
    default =['conditions Sunny','conditions Stormy','conditions Sandstorms','conditions Cloudy','conditions Fog','conditions Windy'] )

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered Thiago Leite')

linhas_selecionadas = df['Order_Date'] <= data_slider
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['Weatherconditions'].isin(Weatherconditions)
df = df.loc[linhas_selecionadas,:]

#==============================
# Layout no Streamlit
#==============================