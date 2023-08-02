#Libraries
import pandas as pd
import numpy as np
import re
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static
from haversine import haversine
import plotly.graph_objects as go


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
st.header('Marketplace - Visão Restaurantes')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:           
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
            
        with col2:          
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['distance'] = df.loc[:, cols].apply(lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis= 1)
            avg_distance = np.round(df['distance'].mean(), 2)
            col2.metric('A distância média é: ', avg_distance)
            
        with col3:         
            df_mean_delivery_festival = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                             .groupby('Festival')
                                             .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_delivery_festival.columns = ['avg_time', 'std_time']
            df_mean_delivery_festival = df_mean_delivery_festival.reset_index()
            df_mean_delivery_festival = np.round(df_mean_delivery_festival.loc[df_mean_delivery_festival['Festival'] == 'Yes', 'avg_time'], 2)
            col3.metric('Tempo médio de entrega com Festival', df_mean_delivery_festival)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            df_mean_delivery_festival = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                             .groupby('Festival')
                                             .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_delivery_festival.columns = ['avg_time', 'std_time']
            df_mean_delivery_festival = df_mean_delivery_festival.reset_index()
            df_mean_delivery_festival = np.round(df_mean_delivery_festival.loc[df_mean_delivery_festival['Festival'] == 'Yes', 'std_time'], 2)
            col1.metric('Desvio padrão de entrega com Festival', df_mean_delivery_festival)
            
        with col2:           
            df_mean_delivery_festival = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                             .groupby('Festival')
                                             .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_delivery_festival.columns = ['avg_time', 'std_time']
            df_mean_delivery_festival = df_mean_delivery_festival.reset_index()
            df_mean_delivery_festival = np.round(df_mean_delivery_festival.loc[df_mean_delivery_festival['Festival'] == 'No', 'avg_time'], 2)
            col2.metric('Tempo médio de entrega sem Festival', df_mean_delivery_festival)
            
        with col3:           
            df_mean_delivery_festival = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                             .groupby('Festival')
                                             .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_delivery_festival.columns = ['avg_time', 'std_time']
            df_mean_delivery_festival = df_mean_delivery_festival.reset_index()
            df_mean_delivery_festival = np.round(df_mean_delivery_festival.loc[df_mean_delivery_festival['Festival'] == 'No', 'std_time'], 2)
            col3.metric('Desvio padrão de entrega sem Festival', df_mean_delivery_festival)
            
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Distribuição do tempo por cidade')
            df_mean_std_by_city = (df.loc[:, ['Time_taken(min)', 'City']]
                                       .groupby('City')
                                       .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_std_by_city.columns = ['avg_time', 'std_time']
            df_mean_std_by_city = df_mean_std_by_city.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control',
                                 x=df_mean_std_by_city['City'],
                                 y=df_mean_std_by_city['avg_time'],
                                 error_y=dict(type='data', array=df_mean_std_by_city['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown('###### Tempo médio por tipo de entrega')
            df_mean_std_by_city_order = (df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                                            .groupby(['City', 'Type_of_order'])
                                            .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_std_by_city_order.columns = ['time_mean', 'time_std']
            df_mean_std_by_city_order = df_mean_std_by_city_order.reset_index()
            st.dataframe(df_mean_std_by_city_order)

    with st.container():
        st.markdown('''---''')
        st.title('Tempo médio entrega por cidade')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Distância da distribuição da distância média por cidade')
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']        
            df['distance'] = df.loc[:, cols].apply(lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis= 1)
            avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig= go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('###### Tempo médio por tipo de cidade e tipo de tráfego')
            df_mean_std_by_city_traffic = (df.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                              .groupby(['City', 'Road_traffic_density'])
                                              .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_std_by_city_traffic.columns = ['avg_time', 'std_time']

            df_mean_std_by_city_traffic = df_mean_std_by_city_traffic.reset_index()
            fig = px.sunburst(df_mean_std_by_city_traffic, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='Rdbu',
                              color_continuous_midpoint=np.average(df_mean_std_by_city_traffic['std_time']))
            st.plotly_chart(fig, use_container_width=True)     
