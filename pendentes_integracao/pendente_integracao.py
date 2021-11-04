import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
import base64
from io import BytesIO


uploaded_file = st.file_uploader(
    "Coloque aqui o arquivo JSON", type=["csv", "json"], accept_multiple_files=False
)

df=pd.read_json(uploaded_file)
st.header('Essa é a base de dados:')
df

# Variáveis Relevantes
    # Total de pedidos pendentes de integração
total_pendentes = len(df)
st.write(f"**Total de Pendentes da Base de Dados:** {total_pendentes}")

# Graficos por parceiros
st.header("Ranking Parceiros")
df['pedidos']=1
df_parceiros = df.groupby(['site_name','usuario','squad']).sum()
df_parceiros = df_parceiros.sort_values('pedidos',ascending=False)
df_parceiros=df_parceiros.drop(columns=['order_id','id_produto','status'])
df_parceiros
# base para o grafico
df_sites=df.groupby('site_name').sum()
df_sites=df_sites.drop(columns=['order_id','id_produto','status'])
df_sites=df_sites.sort_values('pedidos',ascending=False)
df_sites = df_sites.head(20)

#grafico
plot = go.Figure(data=[go.Bar(name= 'Pendentes Integração',x=df_sites.index,y=df_sites['pedidos'],text=df_sites['pedidos'],textposition='outside', orientation='v')])
plot.update_layout(height=800, width=800)
st.plotly_chart(plot,use_container_width=True)


# Graficos por datas
st.header("Pendentes de Integração por Datas")

df['criado_em'] = df['criado_em'].astype(str)
df['criado_em'] = df['criado_em'].str[:10]
df_datas = df.groupby('criado_em').sum()
df_datas=df_datas.drop(columns=['order_id','id_produto','status'])
#df_datas = df_datas.sort_values('pedidos',ascending=False)
df_datas = df_datas.tail(50)

a , b = st.columns(2)
with a:
    st.subheader('Lista completa')
    df_datas

with b:
    st.subheader('Ranking')
    df_datas_ranking = df_datas.sort_values('pedidos',ascending=False)
    df_datas_ranking

st.markdown('#')
st.subheader('Pendentes Integração Últimos 50 dias')
#grafico
plot = go.Figure(data=[go.Bar(name= 'Pendentes Integração Últimos 50 dias',x=df_datas.index,y=df_datas['pedidos'],text=df_datas['pedidos'],textposition='outside', orientation='v')])
plot.update_layout(height=800, width=1000)
st.plotly_chart(plot,use_container_width=False)

# Filter in SideBar
Filtro_integracao =  st.sidebar.multiselect('Selecione a integração',options=df['integracao'].unique(),default=df['integracao'].unique())
# Resultado da Query
# st.header('Resultado do Filtro')
Integracoes_Filtro = df.query("integracao == @Filtro_integracao" )



# Fazer filtro dos motivos!!!!!!!!!
# Filter in SideBar
Filtro_motivo =  st.sidebar.multiselect('Selecione o motivo',options=Integracoes_Filtro['rule_name'].unique(),default=Integracoes_Filtro['rule_name'].unique())
# Resultado da Query
# st.header('Resultado do Filtro')
df_Filtro_motivo = Integracoes_Filtro.query("rule_name == @Filtro_motivo" )

# Filter in SideBar
Filtro_response =  st.sidebar.multiselect('Selecione a resposta',options=df_Filtro_motivo['rule_response'].unique(),default=df_Filtro_motivo['rule_response'].unique())
# Resultado da Query
# st.header('Resultado do Filtro')
df_Filtro_motivo = df_Filtro_motivo.query("rule_name == @Filtro_motivo" )
st.subheader('Lista de pedidos conforme o motivo da pendência')

df_Filtro_motivo

st.subheader('Lista de pedidos conforme a integração escolhida')

total_pendentes_filtro = len(df_Filtro_motivo)
st.write(f"**Total de Pendentes do Filtro:** {total_pendentes_filtro}")

percentual_pendentes = round((total_pendentes_filtro/total_pendentes)*100,2)
st.write(f"**Percentual Contribuição:** {percentual_pendentes} %")

# Graficos por parceiros
# base para o grafico
filter_parceiros =df_Filtro_motivo.groupby('site_name').sum()

filter_parceiros=filter_parceiros.drop(columns=['order_id','id_produto','status'])
filter_parceiros=filter_parceiros.sort_values('pedidos',ascending=False)
filter_parceiros_top20 = filter_parceiros.head(20)

#grafico
st.subheader('Gráfico de Pendentes conforme Integração Escolhida')
plot = go.Figure(data=[go.Bar(name= 'Parceiros por Integração',x=filter_parceiros_top20.index,y=filter_parceiros_top20['pedidos'],text=filter_parceiros_top20['pedidos'],textposition='outside', orientation='v')])
plot.update_layout(height=800, width=800)
st.plotly_chart(plot,use_container_width=True)

# Exportando documento Excel
df_Filtro_motivo_agrupa = df_Filtro_motivo.groupby(['usuario','site_name','order_id','rule_name','rule_response','id_produto']).sum()
df_Filtro_motivo_agrupa=df_Filtro_motivo_agrupa.drop(columns=['status'])
st.markdown('#')	
def to_excel(dataframe):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(dataframe):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(dataframe)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Lista_Pendentes_Integracao.xlsx">Download em Excel da lista de pedidos com status Pendente de Integracao</a>' # decode b'abc' => abc

dataframe = df_Filtro_motivo_agrupa # your dataframe
st.markdown(get_table_download_link(dataframe), unsafe_allow_html=True)

