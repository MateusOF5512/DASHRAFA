import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

@st.cache_data
def load_google_sheet():
    # Autenticação do Google
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds_json = st.secrets["google"]["credentials_json"]
    creds_dict = json.loads(creds_json)  # Converter a string JSON em um dicionário

    # Autenticar usando as credenciais carregadas
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Carregar a planilha do Google Sheets
    url = 'https://docs.google.com/spreadsheets/d/1RzYx_XV2PW-drzJfRQfaYMWoO0AmPUTK5zjtbLHt8YI/edit?usp=sharing'
    sheet = client.open_by_url(url).worksheet("Página1")

    # Converter os dados da planilha em um DataFrame do Pandas
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    df['DATA_ENTRADA'] = (pd.to_datetime(df['DATA_ENTRADA'], format='%d/%m/%Y', errors='coerce')).dt.date
    df['DATA_SAIDA'] = (pd.to_datetime(df['DATA_SAIDA'], format='%d/%m/%Y', errors='coerce')).dt.date

    df["DIAS_RESERVA"] = ((df["DATA_SAIDA"] - df["DATA_ENTRADA"]).dt.days )

    df['ID_LOCACAO'] = df['ID_LOCACAO'].astype(str)
    df['COD_IMOVEL'] = df['COD_IMOVEL'].astype(str)
    df['OCORRENCIAS'] = df['OCORRENCIAS'].astype(int)
    df['VALOR_TOTAL'] = df['VALOR_TOTAL'].astype(str).str.replace('.', '', regex=True)
    df['VALOR_TOTAL'] = df['VALOR_TOTAL'].astype(str).str.replace(',', '.', regex=True)
    df['VALOR_TOTAL'] = df['VALOR_TOTAL'].astype(float)
    df['COMISSAO'] = df['COMISSAO'].astype(int)

    df["VALOR_DIARIA"] = (df['VALOR_TOTAL'] / df["DIAS_RESERVA"]).round(2)
    df["VALOR_COMISSAO"] = (df["VALOR_TOTAL"] * (df["COMISSAO"] / 100)).round(2)
    df["VALOR_COMISSAO_DIARIA"] = (df["VALOR_COMISSAO"] / df["DIAS_RESERVA"]).round(2)

    df['SEMANA_ANO'] = df['DATA_ENTRADA'].apply(get_week_number)
    df['SEMANA'] = df['DATA_ENTRADA'].apply(get_week_name)
    df['MES_ANO'] = df['DATA_ENTRADA'].apply(get_month_number)
    df['MES'] = df['DATA_ENTRADA'].apply(get_month_name)
    df['ANO'] = df['DATA_ENTRADA'].apply(get_year_number)



    return df



def get_month_number(date):

    date = pd.to_datetime(date)
    year = date.year
    month = date.month

    month = f'{year}.{month:02d}'

    return float(month)


def get_week_number(date):
    # Converter para objeto de data do pandas
    date = pd.to_datetime(date)
    year = date.year
    week_number = date.isocalendar()[1]

    semana = f'{year}{week_number:02d}'
    return int(semana)

def get_year_number(date):

    date = pd.to_datetime(date)
    year = date.year

    return int(year)

def get_week_name(date):
    date = pd.to_datetime(date)
    dia_semana = date.strftime('%A')

    if dia_semana == 'Monday':
        dia_semana = 'Segunda'
    elif dia_semana == 'Tuesday':
        dia_semana = 'Terça'
    elif dia_semana == 'Wednesday':
        dia_semana = 'Quarta'
    elif dia_semana == 'Thursday':
        dia_semana = 'Quinta'
    elif dia_semana == 'Friday':
        dia_semana = 'Sexta'
    elif dia_semana == 'Saturday':
        dia_semana = 'Sábado'
    elif dia_semana == 'Sunday':
        dia_semana = 'Domingo'

    dia_semana = f'{dia_semana}'

    return str(dia_semana)

def get_month_name(date):
    date = pd.to_datetime(date)

    mes_nome = date.strftime('%B')

    if mes_nome == 'January':
        mes_nome = 'Janeiro'
    elif mes_nome == 'February':
        mes_nome = 'Fevereiro'
    elif mes_nome == 'March':
        mes_nome = 'Março'
    elif mes_nome == 'April':
        mes_nome = 'Abril'
    elif mes_nome == 'May':
        mes_nome = 'Maio'
    elif mes_nome == 'June':
        mes_nome = 'Junho'
    elif mes_nome == 'July':
        mes_nome = 'Julho'
    elif mes_nome == 'August':
        mes_nome = 'Agosto'
    elif mes_nome == 'September':
        mes_nome = 'Setembro'
    elif mes_nome == 'October':
        mes_nome = 'Outubro'
    elif mes_nome == 'November':
        mes_nome = 'Novembro'
    elif mes_nome == 'December':
        mes_nome = 'Dezembro'

    mes_nome = f'{mes_nome}'

    return str(mes_nome)

def bar_plot_horiz(df, categico, numerico, cor1, y_name, textposition, colortext, margin):

    df[numerico] = df[numerico].astype(int)
    df[categico] = df[categico].astype(str)
    df = df.sort_values(numerico, ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[numerico], y=df[categico], text=df[numerico], textposition=textposition, insidetextanchor='end', name='',
        textfont=dict(color=colortext, family='Arial'),
        textangle=0,
        hovertemplate="</br>"+y_name+": <b>%{y}</b>" +
                      "</br>Total: <b>%{x}</b>",
        orientation='h',
        marker_color=cor1))

    fig.update_layout(
        paper_bgcolor="#F8F8FF", plot_bgcolor="#F8F8FF", font={'color': "#000000", 'family': "sans-serif"},
        height=300, margin=margin, autosize=False, dragmode=False )
    fig.update_yaxes(
        title_font=dict(family='Sans-serif', size=10),
        tickfont=dict(family='Sans-serif', size=12), nticks=20, showgrid=True,
        gridwidth=0.5, gridcolor='#D3D3D3')
    fig.update_xaxes(
        tickfont=dict(family='Sans-serif', size=10), nticks=5,
        showgrid=True, gridwidth=0.8, gridcolor='#D3D3D3')


    return fig


def linha_data(df, tempo, variavel):


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[tempo], y=df[variavel], name='',
        mode='lines+markers',
        line=dict(width=1, color='#197119'),
        marker=dict(line=dict(width=0.5),size=3, symbol='diamond', color='#197119'),
        stackgroup='one',
    ))


    fig.update_layout(
        showlegend=True, xaxis_type='category',
        paper_bgcolor="#F8F8FF", plot_bgcolor="#F8F8FF", font={'color': "#000000", 'family': "sans-serif"},
        legend=dict(font_size=10, orientation="h", yanchor="top", y=1.40, xanchor="center", x=0.50),
        height=300, hovermode="x unified", autosize=False, dragmode=False, margin=dict(l=20, r=20, b=20, t=20)
    )
    fig.update_yaxes(
        tickfont=dict(family='Sans-serif', size=12), nticks=5, showgrid=True, gridwidth=0.5, gridcolor='#D3D3D3'
    )
    fig.update_xaxes(
        title_text="Semanas do Ano", title_font=dict(family='Sans-serif', size=10),
        tickfont=dict(family='Sans-serif', size=12), showgrid=False, gridwidth=0.5, gridcolor='#D3D3D3'
    )

    return fig


def linha(df):
    # Criando um índice de datas que cobre todas as reservas
    data_inicio = df["DATA_ENTRADA"].min()
    data_fim = df["DATA_SAIDA"].max()
    df_datas = pd.DataFrame({"Data": pd.date_range(start=data_inicio, end=data_fim)})
    df_datas = df_datas.iloc[:-1]

    # Criando a contagem de reservas ativas por dia
    df_reservas = []
    for _, row in df.iterrows():
        periodo_reserva = pd.date_range(start=row["DATA_ENTRADA"], end=row["DATA_SAIDA"] - pd.Timedelta(days=1))
        df_reservas.append(pd.DataFrame({"Data": periodo_reserva, "Reservas_Ativas": 1}))

    # Concatenando todas as reservas e agrupando para somar os dias com múltiplas reservas
    df_reservas = pd.concat(df_reservas).groupby("Data").sum().reset_index()

    # Juntando com todas as datas possíveis e preenchendo dias sem reservas com zero
    df_final = df_datas.merge(df_reservas, on="Data", how="left").fillna(0)

    # Criando o gráfico com Plotly
    fig = px.line(df_final, x="Data", y="Reservas_Ativas",
                  labels={"Data": "Data", "Reservas_Ativas": "Reservas Ativas"},
                  markers=False)

    # Encontrar todos os domingos no intervalo de datas
    domingos = pd.date_range(start=data_inicio, end=data_fim, freq='W-SUN')

    # Adicionar as linhas verticais pontilhadas
    for domingo in domingos:
        fig.add_vline(x=domingo, line_dash="dot", line_color="gray", opacity=0.5)

    # Melhorando o layout
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Número de Reservas Ativas",
        xaxis=dict(tickangle=90),
        template="plotly_white"
    )

    fig.update_yaxes(
        tickfont=dict(family='Sans-serif', size=12), nticks=10, showgrid=True, gridwidth=0.5, gridcolor='#D3D3D3'
    )
    fig.update_xaxes(
        tickfont=dict(family='Sans-serif', size=12), nticks=20, showgrid=False, gridwidth=0.5, gridcolor='#D3D3D3'
    )

    return fig

def linha_valor_diaria(df):
    # Criando um índice de datas que cobre todas as reservas
    data_inicio = df["DATA_ENTRADA"].min()
    data_fim = df["DATA_SAIDA"].max()
    df_datas = pd.DataFrame({"Data": pd.date_range(start=data_inicio, end=data_fim)})
    df_datas = df_datas.iloc[:-1]

    # Criando a distribuição de valores diários
    df_diarias = []
    for _, row in df.iterrows():
        periodo_reserva = pd.date_range(start=row["DATA_ENTRADA"], end=row["DATA_SAIDA"] - pd.Timedelta(days=1))
        df_diarias.append(pd.DataFrame({"Data": periodo_reserva, "Valor_Diaria": row["VALOR_DIARIA"]}))

    # Concatenando e somando os valores diários de todas as reservas ativas
    df_diarias = pd.concat(df_diarias).groupby("Data").sum().reset_index()

    # Juntando com todas as datas possíveis e preenchendo dias sem reservas com zero
    df_final = df_datas.merge(df_diarias, on="Data", how="left").fillna(0)

    # Criando o gráfico com Plotly
    fig = px.line(df_final, x="Data", y="Valor_Diaria",
                  labels={"Data": "Data", "Valor_Diaria": "Ganho Diário Total (R$)"},
                  markers=False)

    # Encontrar todos os domingos no intervalo de datas
    domingos = pd.date_range(start=data_inicio, end=data_fim, freq='W-SUN')

    # Adicionar as linhas verticais pontilhadas
    for domingo in domingos:
        fig.add_vline(x=domingo, line_dash="dot", line_color="gray", opacity=0.5)

    # Melhorando o layout
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Ganho Diário Total (R$)",
        xaxis=dict(tickangle=90),
        template="plotly_white"
    )

    fig.update_yaxes(
        tickfont=dict(family='Sans-serif', size=12), nticks=10, showgrid=True, gridwidth=0.5, gridcolor='#D3D3D3'
    )
    fig.update_xaxes(
        tickfont=dict(family='Sans-serif', size=12), nticks=20, showgrid=False, gridwidth=0.5, gridcolor='#D3D3D3'
    )

    return fig


def plot_hotmap1(df):

    df_map = df.groupby(['SEMANA', 'MES'])['ID_LOCACAO'].agg('count').reset_index().sort_values('SEMANA', ascending=True)

    df_map.rename(columns={'SEMANA': 'Semana', 'ID_LOCACAO': 'ID'}, inplace=True)


    jan_seg = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Segunda')]['ID']
    jan_ter = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Terça')]['ID']
    jan_qua = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Quarta')]['ID']
    jan_qui = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Quinta')]['ID']
    jan_sex = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Sexta')]['ID']
    jan_sab = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Sábado')]['ID']
    jan_dom = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Domingo')]['ID']

    fev_seg = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Segunda')]['ID']
    fev_ter = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Terça')]['ID']
    fev_qua = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Quarta')]['ID']
    fev_qui = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Quinta')]['ID']
    fev_sex = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Sexta')]['ID']
    fev_sab = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Sábado')]['ID']
    fev_dom = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Domingo')]['ID']

    mar_seg = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Segunda')]['ID']
    mar_ter = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Terça')]['ID']
    mar_qua = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Quarta')]['ID']
    mar_qui = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Quinta')]['ID']
    mar_sex = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Sexta')]['ID']
    mar_sab = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Sábado')]['ID']
    mar_dom = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Domingo')]['ID']

    abr_seg = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Segunda')]['ID']
    abr_ter = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Terça')]['ID']
    abr_qua = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Quarta')]['ID']
    abr_qui = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Quinta')]['ID']
    abr_sex = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Sexta')]['ID']
    abr_sab = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Sábado')]['ID']
    abr_dom = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Domingo')]['ID']

    mai_seg = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Segunda')]['ID']
    mai_ter = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Terça')]['ID']
    mai_qua = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Quarta')]['ID']
    mai_qui = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Quinta')]['ID']
    mai_sex = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Sexta')]['ID']
    mai_sab = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Sábado')]['ID']
    mai_dom = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Domingo')]['ID']

    jun_seg = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Segunda')]['ID']
    jun_ter = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Terça')]['ID']
    jun_qua = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Quarta')]['ID']
    jun_qui = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Quinta')]['ID']
    jun_sex = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Sexta')]['ID']
    jun_sab = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Sábado')]['ID']
    jun_dom = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Domingo')]['ID']

    jul_seg = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Segunda')]['ID']
    jul_ter = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Terça')]['ID']
    jul_qua = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Quarta')]['ID']
    jul_qui = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Quinta')]['ID']
    jul_sex = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Sexta')]['ID']
    jul_sab = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Sábado')]['ID']
    jul_dom = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Domingo')]['ID']

    ago_seg = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Segunda')]['ID']
    ago_ter = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Terça')]['ID']
    ago_qua = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Quarta')]['ID']
    ago_qui = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Quinta')]['ID']
    ago_sex = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Sexta')]['ID']
    ago_sab = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Sábado')]['ID']
    ago_dom = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Domingo')]['ID']

    set_seg = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Segunda')]['ID']
    set_ter = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Terça')]['ID']
    set_qua = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Quarta')]['ID']
    set_qui = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Quinta')]['ID']
    set_sex = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Sexta')]['ID']
    set_sab = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Sábado')]['ID']
    set_dom = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Domingo')]['ID']

    out_seg = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Segunda')]['ID']
    out_ter = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Terça')]['ID']
    out_qua = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Quarta')]['ID']
    out_qui = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Quinta')]['ID']
    out_sex = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Sexta')]['ID']
    out_sab = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Sábado')]['ID']
    out_dom = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Domingo')]['ID']

    nov_seg = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Segunda')]['ID']
    nov_ter = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Terça')]['ID']
    nov_qua = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Quarta')]['ID']
    nov_qui = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Quinta')]['ID']
    nov_sex = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Sexta')]['ID']
    nov_sab = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Sábado')]['ID']
    nov_dom = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Domingo')]['ID']

    dez_seg = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Segunda')]['ID']
    dez_ter = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Terça')]['ID']
    dez_qua = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Quarta')]['ID']
    dez_qui = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Quinta')]['ID']
    dez_sex = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Sexta')]['ID']
    dez_sab = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Sábado')]['ID']
    dez_dom = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Domingo')]['ID']

    jan_seg = 0 if len(jan_seg) == 0 else jan_seg.values[0]
    jan_ter = 0 if len(jan_ter) == 0 else jan_ter.values[0]
    jan_qua = 0 if len(jan_qua) == 0 else jan_qua.values[0]
    jan_qui = 0 if len(jan_qui) == 0 else jan_qui.values[0]
    jan_sex = 0 if len(jan_sex) == 0 else jan_sex.values[0]
    jan_sab = 0 if len(jan_sab) == 0 else jan_sab.values[0]
    jan_dom = 0 if len(jan_dom) == 0 else jan_dom.values[0]

    fev_seg = 0 if len(fev_seg) == 0 else fev_seg.values[0]
    fev_ter = 0 if len(fev_ter) == 0 else fev_ter.values[0]
    fev_qua = 0 if len(fev_qua) == 0 else fev_qua.values[0]
    fev_qui = 0 if len(fev_qui) == 0 else fev_qui.values[0]
    fev_sex = 0 if len(fev_sex) == 0 else fev_sex.values[0]
    fev_sab = 0 if len(fev_sab) == 0 else fev_sab.values[0]
    fev_dom = 0 if len(fev_dom) == 0 else fev_dom.values[0]

    mar_seg = 0 if len(mar_seg) == 0 else mar_seg.values[0]
    mar_ter = 0 if len(mar_ter) == 0 else mar_ter.values[0]
    mar_qua = 0 if len(mar_qua) == 0 else mar_qua.values[0]
    mar_qui = 0 if len(mar_qui) == 0 else mar_qui.values[0]
    mar_sex = 0 if len(mar_sex) == 0 else mar_sex.values[0]
    mar_sab = 0 if len(mar_sab) == 0 else mar_sab.values[0]
    mar_dom = 0 if len(mar_dom) == 0 else mar_dom.values[0]

    abr_seg = 0 if len(abr_seg) == 0 else abr_seg.values[0]
    abr_ter = 0 if len(abr_ter) == 0 else abr_ter.values[0]
    abr_qua = 0 if len(abr_qua) == 0 else abr_qua.values[0]
    abr_qui = 0 if len(abr_qui) == 0 else abr_qui.values[0]
    abr_sex = 0 if len(abr_sex) == 0 else abr_sex.values[0]
    abr_sab = 0 if len(abr_sab) == 0 else abr_sab.values[0]
    abr_dom = 0 if len(abr_dom) == 0 else abr_dom.values[0]

    mai_seg = 0 if len(mai_seg) == 0 else mai_seg.values[0]
    mai_ter = 0 if len(mai_ter) == 0 else mai_ter.values[0]
    mai_qua = 0 if len(mai_qua) == 0 else mai_qua.values[0]
    mai_qui = 0 if len(mai_qui) == 0 else mai_qui.values[0]
    mai_sex = 0 if len(mai_sex) == 0 else mai_sex.values[0]
    mai_sab = 0 if len(mai_sab) == 0 else mai_sab.values[0]
    mai_dom = 0 if len(mai_dom) == 0 else mai_dom.values[0]

    jun_seg = 0 if len(jun_seg) == 0 else jun_seg.values[0]
    jun_ter = 0 if len(jun_ter) == 0 else jun_ter.values[0]
    jun_qua = 0 if len(jun_qua) == 0 else jun_qua.values[0]
    jun_qui = 0 if len(jun_qui) == 0 else jun_qui.values[0]
    jun_sex = 0 if len(jun_sex) == 0 else jun_sex.values[0]
    jun_sab = 0 if len(jun_sab) == 0 else jun_sab.values[0]
    jun_dom = 0 if len(jun_dom) == 0 else jun_dom.values[0]

    jul_seg = 0 if len(jul_seg) == 0 else jul_seg.values[0]
    jul_ter = 0 if len(jul_ter) == 0 else jul_ter.values[0]
    jul_qua = 0 if len(jul_qua) == 0 else jul_qua.values[0]
    jul_qui = 0 if len(jul_qui) == 0 else jul_qui.values[0]
    jul_sex = 0 if len(jul_sex) == 0 else jul_sex.values[0]
    jul_sab = 0 if len(jul_sab) == 0 else jul_sab.values[0]
    jul_dom = 0 if len(jul_dom) == 0 else jul_dom.values[0]

    ago_seg = 0 if len(ago_seg) == 0 else ago_seg.values[0]
    ago_ter = 0 if len(ago_ter) == 0 else ago_ter.values[0]
    ago_qua = 0 if len(ago_qua) == 0 else ago_qua.values[0]
    ago_qui = 0 if len(ago_qui) == 0 else ago_qui.values[0]
    ago_sex = 0 if len(ago_sex) == 0 else ago_sex.values[0]
    ago_sab = 0 if len(ago_sab) == 0 else ago_sab.values[0]
    ago_dom = 0 if len(ago_dom) == 0 else ago_dom.values[0]

    set_seg = 0 if len(set_seg) == 0 else set_seg.values[0]
    set_ter = 0 if len(set_ter) == 0 else set_ter.values[0]
    set_qua = 0 if len(set_qua) == 0 else set_qua.values[0]
    set_qui = 0 if len(set_qui) == 0 else set_qui.values[0]
    set_sex = 0 if len(set_sex) == 0 else set_sex.values[0]
    set_sab = 0 if len(set_sab) == 0 else set_sab.values[0]
    set_dom = 0 if len(set_dom) == 0 else set_dom.values[0]

    out_seg = 0 if len(out_seg) == 0 else out_seg.values[0]
    out_ter = 0 if len(out_ter) == 0 else out_ter.values[0]
    out_qua = 0 if len(out_qua) == 0 else out_qua.values[0]
    out_qui = 0 if len(out_qui) == 0 else out_qui.values[0]
    out_sex = 0 if len(out_sex) == 0 else out_sex.values[0]
    out_sab = 0 if len(out_sab) == 0 else out_sab.values[0]
    out_dom = 0 if len(out_dom) == 0 else out_dom.values[0]

    nov_seg = 0 if len(nov_seg) == 0 else nov_seg.values[0]
    nov_ter = 0 if len(nov_ter) == 0 else nov_ter.values[0]
    nov_qua = 0 if len(nov_qua) == 0 else nov_qua.values[0]
    nov_qui = 0 if len(nov_qui) == 0 else nov_qui.values[0]
    nov_sex = 0 if len(nov_sex) == 0 else nov_sex.values[0]
    nov_sab = 0 if len(nov_sab) == 0 else nov_sab.values[0]
    nov_dom = 0 if len(nov_dom) == 0 else nov_dom.values[0]

    dez_seg = 0 if len(dez_seg) == 0 else dez_seg.values[0]
    dez_ter = 0 if len(dez_ter) == 0 else dez_ter.values[0]
    dez_qua = 0 if len(dez_qua) == 0 else dez_qua.values[0]
    dez_qui = 0 if len(dez_qui) == 0 else dez_qui.values[0]
    dez_sex = 0 if len(dez_sex) == 0 else dez_sex.values[0]
    dez_sab = 0 if len(dez_sab) == 0 else dez_sab.values[0]
    dez_dom = 0 if len(dez_dom) == 0 else dez_dom.values[0]


    matriz = [
        [jan_dom, fev_dom, mar_dom, abr_dom, mai_dom, jun_dom, jul_dom, ago_dom, set_dom, out_dom, nov_dom, dez_dom],
        [jan_sab, fev_sab, mar_sab, abr_sab, mai_sab, jun_sab, jul_sab, ago_sab, set_sab, out_sab, nov_sab, dez_sab],
        [jan_sex, fev_sex, mar_sex, abr_sex, mai_sex, jun_sex, jul_sex, ago_sex, set_sex, out_sex, nov_sex, dez_sex],
        [jan_qui, fev_qui, mar_qui, abr_qui, mai_qui, jun_qui, jul_qui, ago_qui, set_qui, out_qui, nov_qui, dez_qui],
        [jan_qua, fev_qua, mar_qua, abr_qua, mai_qua, jun_qua, jul_qua, ago_qua, set_qua, out_qua, nov_qua, dez_qua],
        [jan_ter, fev_ter, mar_ter, abr_ter, mai_ter, jun_ter, jul_ter, ago_ter, set_ter, out_ter, nov_ter, dez_ter],
        [jan_seg, fev_seg, mar_seg, abr_seg, mai_seg, jun_seg, jul_seg, ago_seg, set_seg, out_seg, nov_seg, dez_seg],

    ]

    fig = go.Figure(data=go.Heatmap(
        z=matriz, name="", text=matriz,
        y=['Domingo', 'Sábado', 'Sexta', 'Quinta', 'Quarta', 'Terça' , 'Segunda'],
        x=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
        texttemplate="",
        hovertemplate="</br><b>Semana:</b> %{y}" +
                      "</br><b>Mês:</b> %{x}" +
                      "</br><b>Reservas:</b> %{z:,.0f}",
        showscale=True,
        colorscale='Portland'))
    fig.update_layout(height=300, margin=dict(l=20, r=20, b=20, t=20),
                      paper_bgcolor="#F8F8FF", font={'size': 16})

    return fig



def plot_hotmap2(df):

    df_map = df.groupby(['SEMANA', 'MES'])['VALOR_TOTAL'].agg('sum').reset_index().sort_values('SEMANA', ascending=True)

    df_map.rename(columns={'SEMANA': 'Semana', 'VALOR_TOTAL': 'ID'}, inplace=True)


    jan_seg = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Segunda')]['ID']
    jan_ter = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Terça')]['ID']
    jan_qua = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Quarta')]['ID']
    jan_qui = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Quinta')]['ID']
    jan_sex = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Sexta')]['ID']
    jan_sab = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Sábado')]['ID']
    jan_dom = df_map[(df_map['MES'] == 'Janeiro') & (df_map['Semana'] == 'Domingo')]['ID']

    fev_seg = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Segunda')]['ID']
    fev_ter = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Terça')]['ID']
    fev_qua = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Quarta')]['ID']
    fev_qui = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Quinta')]['ID']
    fev_sex = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Sexta')]['ID']
    fev_sab = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Sábado')]['ID']
    fev_dom = df_map[(df_map['MES'] == 'Fevereiro') & (df_map['Semana'] == 'Domingo')]['ID']

    mar_seg = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Segunda')]['ID']
    mar_ter = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Terça')]['ID']
    mar_qua = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Quarta')]['ID']
    mar_qui = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Quinta')]['ID']
    mar_sex = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Sexta')]['ID']
    mar_sab = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Sábado')]['ID']
    mar_dom = df_map[(df_map['MES'] == 'Março') & (df_map['Semana'] == 'Domingo')]['ID']

    abr_seg = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Segunda')]['ID']
    abr_ter = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Terça')]['ID']
    abr_qua = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Quarta')]['ID']
    abr_qui = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Quinta')]['ID']
    abr_sex = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Sexta')]['ID']
    abr_sab = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Sábado')]['ID']
    abr_dom = df_map[(df_map['MES'] == 'Abril') & (df_map['Semana'] == 'Domingo')]['ID']

    mai_seg = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Segunda')]['ID']
    mai_ter = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Terça')]['ID']
    mai_qua = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Quarta')]['ID']
    mai_qui = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Quinta')]['ID']
    mai_sex = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Sexta')]['ID']
    mai_sab = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Sábado')]['ID']
    mai_dom = df_map[(df_map['MES'] == 'Maio') & (df_map['Semana'] == 'Domingo')]['ID']

    jun_seg = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Segunda')]['ID']
    jun_ter = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Terça')]['ID']
    jun_qua = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Quarta')]['ID']
    jun_qui = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Quinta')]['ID']
    jun_sex = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Sexta')]['ID']
    jun_sab = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Sábado')]['ID']
    jun_dom = df_map[(df_map['MES'] == 'Junho') & (df_map['Semana'] == 'Domingo')]['ID']

    jul_seg = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Segunda')]['ID']
    jul_ter = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Terça')]['ID']
    jul_qua = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Quarta')]['ID']
    jul_qui = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Quinta')]['ID']
    jul_sex = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Sexta')]['ID']
    jul_sab = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Sábado')]['ID']
    jul_dom = df_map[(df_map['MES'] == 'Julho') & (df_map['Semana'] == 'Domingo')]['ID']

    ago_seg = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Segunda')]['ID']
    ago_ter = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Terça')]['ID']
    ago_qua = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Quarta')]['ID']
    ago_qui = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Quinta')]['ID']
    ago_sex = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Sexta')]['ID']
    ago_sab = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Sábado')]['ID']
    ago_dom = df_map[(df_map['MES'] == 'Agosto') & (df_map['Semana'] == 'Domingo')]['ID']

    set_seg = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Segunda')]['ID']
    set_ter = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Terça')]['ID']
    set_qua = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Quarta')]['ID']
    set_qui = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Quinta')]['ID']
    set_sex = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Sexta')]['ID']
    set_sab = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Sábado')]['ID']
    set_dom = df_map[(df_map['MES'] == 'Setembro') & (df_map['Semana'] == 'Domingo')]['ID']

    out_seg = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Segunda')]['ID']
    out_ter = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Terça')]['ID']
    out_qua = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Quarta')]['ID']
    out_qui = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Quinta')]['ID']
    out_sex = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Sexta')]['ID']
    out_sab = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Sábado')]['ID']
    out_dom = df_map[(df_map['MES'] == 'Outubro') & (df_map['Semana'] == 'Domingo')]['ID']

    nov_seg = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Segunda')]['ID']
    nov_ter = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Terça')]['ID']
    nov_qua = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Quarta')]['ID']
    nov_qui = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Quinta')]['ID']
    nov_sex = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Sexta')]['ID']
    nov_sab = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Sábado')]['ID']
    nov_dom = df_map[(df_map['MES'] == 'Novembro') & (df_map['Semana'] == 'Domingo')]['ID']

    dez_seg = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Segunda')]['ID']
    dez_ter = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Terça')]['ID']
    dez_qua = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Quarta')]['ID']
    dez_qui = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Quinta')]['ID']
    dez_sex = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Sexta')]['ID']
    dez_sab = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Sábado')]['ID']
    dez_dom = df_map[(df_map['MES'] == 'Dezembro') & (df_map['Semana'] == 'Domingo')]['ID']

    jan_seg = 0 if len(jan_seg) == 0 else jan_seg.values[0]
    jan_ter = 0 if len(jan_ter) == 0 else jan_ter.values[0]
    jan_qua = 0 if len(jan_qua) == 0 else jan_qua.values[0]
    jan_qui = 0 if len(jan_qui) == 0 else jan_qui.values[0]
    jan_sex = 0 if len(jan_sex) == 0 else jan_sex.values[0]
    jan_sab = 0 if len(jan_sab) == 0 else jan_sab.values[0]
    jan_dom = 0 if len(jan_dom) == 0 else jan_dom.values[0]

    fev_seg = 0 if len(fev_seg) == 0 else fev_seg.values[0]
    fev_ter = 0 if len(fev_ter) == 0 else fev_ter.values[0]
    fev_qua = 0 if len(fev_qua) == 0 else fev_qua.values[0]
    fev_qui = 0 if len(fev_qui) == 0 else fev_qui.values[0]
    fev_sex = 0 if len(fev_sex) == 0 else fev_sex.values[0]
    fev_sab = 0 if len(fev_sab) == 0 else fev_sab.values[0]
    fev_dom = 0 if len(fev_dom) == 0 else fev_dom.values[0]

    mar_seg = 0 if len(mar_seg) == 0 else mar_seg.values[0]
    mar_ter = 0 if len(mar_ter) == 0 else mar_ter.values[0]
    mar_qua = 0 if len(mar_qua) == 0 else mar_qua.values[0]
    mar_qui = 0 if len(mar_qui) == 0 else mar_qui.values[0]
    mar_sex = 0 if len(mar_sex) == 0 else mar_sex.values[0]
    mar_sab = 0 if len(mar_sab) == 0 else mar_sab.values[0]
    mar_dom = 0 if len(mar_dom) == 0 else mar_dom.values[0]

    abr_seg = 0 if len(abr_seg) == 0 else abr_seg.values[0]
    abr_ter = 0 if len(abr_ter) == 0 else abr_ter.values[0]
    abr_qua = 0 if len(abr_qua) == 0 else abr_qua.values[0]
    abr_qui = 0 if len(abr_qui) == 0 else abr_qui.values[0]
    abr_sex = 0 if len(abr_sex) == 0 else abr_sex.values[0]
    abr_sab = 0 if len(abr_sab) == 0 else abr_sab.values[0]
    abr_dom = 0 if len(abr_dom) == 0 else abr_dom.values[0]

    mai_seg = 0 if len(mai_seg) == 0 else mai_seg.values[0]
    mai_ter = 0 if len(mai_ter) == 0 else mai_ter.values[0]
    mai_qua = 0 if len(mai_qua) == 0 else mai_qua.values[0]
    mai_qui = 0 if len(mai_qui) == 0 else mai_qui.values[0]
    mai_sex = 0 if len(mai_sex) == 0 else mai_sex.values[0]
    mai_sab = 0 if len(mai_sab) == 0 else mai_sab.values[0]
    mai_dom = 0 if len(mai_dom) == 0 else mai_dom.values[0]

    jun_seg = 0 if len(jun_seg) == 0 else jun_seg.values[0]
    jun_ter = 0 if len(jun_ter) == 0 else jun_ter.values[0]
    jun_qua = 0 if len(jun_qua) == 0 else jun_qua.values[0]
    jun_qui = 0 if len(jun_qui) == 0 else jun_qui.values[0]
    jun_sex = 0 if len(jun_sex) == 0 else jun_sex.values[0]
    jun_sab = 0 if len(jun_sab) == 0 else jun_sab.values[0]
    jun_dom = 0 if len(jun_dom) == 0 else jun_dom.values[0]

    jul_seg = 0 if len(jul_seg) == 0 else jul_seg.values[0]
    jul_ter = 0 if len(jul_ter) == 0 else jul_ter.values[0]
    jul_qua = 0 if len(jul_qua) == 0 else jul_qua.values[0]
    jul_qui = 0 if len(jul_qui) == 0 else jul_qui.values[0]
    jul_sex = 0 if len(jul_sex) == 0 else jul_sex.values[0]
    jul_sab = 0 if len(jul_sab) == 0 else jul_sab.values[0]
    jul_dom = 0 if len(jul_dom) == 0 else jul_dom.values[0]

    ago_seg = 0 if len(ago_seg) == 0 else ago_seg.values[0]
    ago_ter = 0 if len(ago_ter) == 0 else ago_ter.values[0]
    ago_qua = 0 if len(ago_qua) == 0 else ago_qua.values[0]
    ago_qui = 0 if len(ago_qui) == 0 else ago_qui.values[0]
    ago_sex = 0 if len(ago_sex) == 0 else ago_sex.values[0]
    ago_sab = 0 if len(ago_sab) == 0 else ago_sab.values[0]
    ago_dom = 0 if len(ago_dom) == 0 else ago_dom.values[0]

    set_seg = 0 if len(set_seg) == 0 else set_seg.values[0]
    set_ter = 0 if len(set_ter) == 0 else set_ter.values[0]
    set_qua = 0 if len(set_qua) == 0 else set_qua.values[0]
    set_qui = 0 if len(set_qui) == 0 else set_qui.values[0]
    set_sex = 0 if len(set_sex) == 0 else set_sex.values[0]
    set_sab = 0 if len(set_sab) == 0 else set_sab.values[0]
    set_dom = 0 if len(set_dom) == 0 else set_dom.values[0]

    out_seg = 0 if len(out_seg) == 0 else out_seg.values[0]
    out_ter = 0 if len(out_ter) == 0 else out_ter.values[0]
    out_qua = 0 if len(out_qua) == 0 else out_qua.values[0]
    out_qui = 0 if len(out_qui) == 0 else out_qui.values[0]
    out_sex = 0 if len(out_sex) == 0 else out_sex.values[0]
    out_sab = 0 if len(out_sab) == 0 else out_sab.values[0]
    out_dom = 0 if len(out_dom) == 0 else out_dom.values[0]

    nov_seg = 0 if len(nov_seg) == 0 else nov_seg.values[0]
    nov_ter = 0 if len(nov_ter) == 0 else nov_ter.values[0]
    nov_qua = 0 if len(nov_qua) == 0 else nov_qua.values[0]
    nov_qui = 0 if len(nov_qui) == 0 else nov_qui.values[0]
    nov_sex = 0 if len(nov_sex) == 0 else nov_sex.values[0]
    nov_sab = 0 if len(nov_sab) == 0 else nov_sab.values[0]
    nov_dom = 0 if len(nov_dom) == 0 else nov_dom.values[0]

    dez_seg = 0 if len(dez_seg) == 0 else dez_seg.values[0]
    dez_ter = 0 if len(dez_ter) == 0 else dez_ter.values[0]
    dez_qua = 0 if len(dez_qua) == 0 else dez_qua.values[0]
    dez_qui = 0 if len(dez_qui) == 0 else dez_qui.values[0]
    dez_sex = 0 if len(dez_sex) == 0 else dez_sex.values[0]
    dez_sab = 0 if len(dez_sab) == 0 else dez_sab.values[0]
    dez_dom = 0 if len(dez_dom) == 0 else dez_dom.values[0]


    matriz = [
        [jan_dom, fev_dom, mar_dom, abr_dom, mai_dom, jun_dom, jul_dom, ago_dom, set_dom, out_dom, nov_dom, dez_dom],
        [jan_sab, fev_sab, mar_sab, abr_sab, mai_sab, jun_sab, jul_sab, ago_sab, set_sab, out_sab, nov_sab, dez_sab],
        [jan_sex, fev_sex, mar_sex, abr_sex, mai_sex, jun_sex, jul_sex, ago_sex, set_sex, out_sex, nov_sex, dez_sex],
        [jan_qui, fev_qui, mar_qui, abr_qui, mai_qui, jun_qui, jul_qui, ago_qui, set_qui, out_qui, nov_qui, dez_qui],
        [jan_qua, fev_qua, mar_qua, abr_qua, mai_qua, jun_qua, jul_qua, ago_qua, set_qua, out_qua, nov_qua, dez_qua],
        [jan_ter, fev_ter, mar_ter, abr_ter, mai_ter, jun_ter, jul_ter, ago_ter, set_ter, out_ter, nov_ter, dez_ter],
        [jan_seg, fev_seg, mar_seg, abr_seg, mai_seg, jun_seg, jul_seg, ago_seg, set_seg, out_seg, nov_seg, dez_seg],

    ]

    fig = go.Figure(data=go.Heatmap(
        z=matriz, name="", text=matriz,
        y=[ 'Domingo', 'Sábado', 'Sexta', 'Quinta', 'Quarta', 'Terça' , 'Segunda'],
        x=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
        texttemplate="",
        hovertemplate="</br><b>Semana:</b> %{x}" +
                      "</br><b>Mês:</b> %{y}" +
                      "</br><b>Compras:</b> %{z:,.0d}",
        showscale=True,
        colorscale='Portland'))
    fig.update_layout(height=300, margin=dict(l=20, r=20, b=20, t=20),
                      paper_bgcolor="#F8F8FF", font={'size': 16})

    return fig