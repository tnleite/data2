#Libraries
import pandas as pd
import numpy as np
import re
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config(page_title="Visão Empresa", page_icon="🏢", layout="wide")

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


#Visao empresa:
colunas = ['ID', 'Order_Date']
df_auxiliar = df.loc[:,colunas].groupby('Order_Date').count().reset_index()

px.bar(df_auxiliar, x='Order_Date', y='ID')

#==============================
# Barra lateral no Streamlit
#==============================
import streamlit as st
st.header('Marketplace - Visão Cliente')

image_path = 'logo3.png'
image = Image.open(image_path)
st.sidebar.image(image, width=220)


st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite :calendar:')
data_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022,4,13),min_value=pd.datetime(2022,2,11), max_value=pd.datetime(2022,4,6), format='DD/MM/YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium','High','Jam'], 
    default =['Low','Medium','High','Jam'] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered Thiago Leite')

linhas_selecionadas = df['Order_Date'] <= data_slider
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

#==============================
# Layout no Streamlit
#==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Código quantidade de pedisos dia:
        st.markdown('# Pedidos por dia:')
        colunas = ['ID', 'Order_Date']
        df_auxiliar = df.loc[:,colunas].groupby('Order_Date').count().reset_index()
        fig = px.bar(df_auxiliar, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('## Pedidos por tipo de tráfego:')
            colunas = ['ID', 'Road_traffic_density']
            df_auxiliar = df.loc[:,colunas].groupby('Road_traffic_density').count().reset_index()
            df_auxiliar = df_auxiliar.loc[df_auxiliar['Road_traffic_density'] != 'NaN',:]
            df_auxiliar['entregas_perc'] = df_auxiliar['ID'] / df_auxiliar['ID'].sum()
            
            fig = px.pie(df_auxiliar,values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width = True)
        
        
        with col2:
            st.markdown('## Pedidos por tipo de cidade e tráfego:')
            df_aux = df.loc[:, ['ID','City','Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width = True)


            
with tab2:
    with st.container():
        st.markdown('# Quantidade de pedidos por semana:')
        df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
        colunas = ['ID', 'week_of_year']
        df_auxiliar = df.loc[:,colunas].groupby('week_of_year').count().reset_index()
        fig = px.line(df_auxiliar, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        st.markdown('# Quantidade de pedidos por entregador por semana:')
        df_aux01 = df.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux = pd.merge(df_aux01,df_aux02, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_width = True)

with tab3:
    st.markdown('# Localização central de entregas por tipo de cidade e tráfego:')
    df_aux = df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width=1024,height=600)
