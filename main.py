import streamlit

from functions import *
st.set_page_config(layout="wide")

df = load_google_sheet()


with st.sidebar:
    st.markdown("<h2 style='font-size:150%; text-align: center; color: black; padding: 0px 0px 0px 0px;'" +
                ">Painel de Controle</h2>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("<h3 style='font-size:100%; text-align: center; color: black; padding: 0px 0px 20px 0px;'" +
                ">Controle de Datas</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        semana_min = df['DATA_ENTRADA'].min()
        semana_min_float = st.date_input("Data de Entrada:", semana_min)

        semana_min_float = pd.Timestamp(semana_min_float)

    with col2:
        semana_max = df['DATA_SAIDA'].max()
        semana_max_float = st.date_input("Data de Saída:", semana_max)
        semana_max_float = pd.Timestamp(semana_max_float)

    mask_semana = (df['DATA_ENTRADA'] >= semana_min_float) & (df['DATA_SAIDA'] <= semana_max_float)
    df = df.loc[mask_semana]

    with st.expander('Mais Datas'):
        semana_max = df['SEMANA_ANO'].max()
        semana_min = df['SEMANA_ANO'].min()
        col11, col22 = st.columns([1, 1])
        with col1:
            semana_min = col11.number_input('Semana | Mínimo:',
                                            min_value=semana_min, max_value=semana_max,
                                            value=semana_min, step=1, key=23)
        with col2:
            semana_max = col22.number_input('Semana | Máximo:',
                                            min_value=semana_min, max_value=semana_max,
                                            value=semana_max, step=1, key=33)

        df = df[(df['SEMANA_ANO'] >= semana_min) & (df['SEMANA_ANO'] <= semana_max)]

        dias_reserva_max = df['DIAS_RESERVA'].max()
        dias_reserva_min = df['DIAS_RESERVA'].min()
        col11, col22 = st.columns([1, 1])
        with col1:
            dias_reserva_min = col11.number_input('Dias Reserva | Mínimo:',
                                            min_value=dias_reserva_min, max_value=dias_reserva_max,
                                            value=dias_reserva_min, step=1, key=232)
        with col2:
            dias_reserva_max = col22.number_input('Dias Reserva | Máximo:',
                                            min_value=dias_reserva_min, max_value=dias_reserva_max,
                                            value=dias_reserva_max, step=1, key=332)

        df = df[(df['DIAS_RESERVA'] >= dias_reserva_min) & (df['DIAS_RESERVA'] <= dias_reserva_max)]

        semana_tolist = df['SEMANA'].unique().tolist()
        selected_mes = st.multiselect("Selecione o Dia da Semana da Reserva:",
                                      options=semana_tolist, default=semana_tolist, key=19)
        df = df[df['SEMANA'].isin(selected_mes)]

        mes_tolist = df['MES'].unique().tolist()
        selected_mes = st.multiselect("Selecione o Mês da Reserva:",
                                      options=mes_tolist, default=mes_tolist, key=49)
        df = df[df['MES'].isin(selected_mes)]



        st.markdown('---')


    st.markdown('---')

    st.markdown("<h3 style='font-size:100%; text-align: center; color: black; padding: 0px 0px 20px 0px;'" +
                ">Controle de Valores (R$)</h3>", unsafe_allow_html=True)

    valor_total_max = df['VALOR_TOTAL'].max()
    valor_total_min = df['VALOR_TOTAL'].min()
    col11, col22 = st.columns([1, 1])
    with col1:
        valor_min = col11.number_input('Total | Mínimo:',
                                            min_value=valor_total_min, max_value=valor_total_max,
                                            value=valor_total_min, step=1.0, key=261)
    with col2:
        valor_max = col22.number_input('Total | Máximo:',
                                            min_value=valor_total_min, max_value=valor_total_max,
                                            value=valor_total_max, step=1.0, key=262)

    df = df[(df['VALOR_TOTAL'] >= valor_min) & (df['VALOR_TOTAL'] <= valor_max)]


    valor_diaria_max = df['VALOR_DIARIA'].max()
    valor_diaria_min = df['VALOR_DIARIA'].min()
    col11, col22 = st.columns([1, 1])
    with col1:
        diaria_min = col11.number_input('Diária | Mínimo:',
                                            min_value=valor_diaria_min, max_value=valor_diaria_max,
                                            value=valor_diaria_min, step=1.0, key=263)
    with col2:
        diaria_max = col22.number_input('Diária | Máximo:',
                                            min_value=valor_diaria_min, max_value=valor_diaria_max,
                                            value=valor_diaria_max, step=1.0, key=264)

    df = df[(df['VALOR_DIARIA'] >= diaria_min) & (df['VALOR_DIARIA'] <= diaria_max)]


    valor_comissao_max = df['VALOR_COMISSAO'].max()
    valor_comissao_min = df['VALOR_COMISSAO'].min()
    col11, col22 = st.columns([1, 1])
    with col1:
        comissao_min = col11.number_input('Comissão | Mínimo:',
                                            min_value=valor_comissao_min, max_value=valor_comissao_max,
                                            value=valor_comissao_min, step=1.0, key=265)
    with col2:
        comissao_max = col22.number_input('Comissão | Máximo:',
                                            min_value=valor_comissao_min, max_value=valor_comissao_max,
                                            value=valor_comissao_max, step=1.0, key=266)

    df = df[(df['VALOR_DIARIA'] >= diaria_min) & (df['VALOR_DIARIA'] <= diaria_max)]

    st.markdown('---')

    st.markdown("<h3 style='font-size:100%; text-align: center; color: black; padding: 0px 0px 20px 0px;'" +
                ">Controle de Informações da Reserva</h3>", unsafe_allow_html=True)


    search_descricao = st.text_input('Pesquisar Descrição:')

    if len(search_descricao) == 0:
        df = df
    else:
        df = df[df['DESCRICAO'].str.contains(search_descricao, case=False)]

    origem_tolist = df['ORIGEM'].unique().tolist()
    selected_origem = st.multiselect("Selecione a Origem da Reserva:",
                                  options=origem_tolist, default=origem_tolist, key=98)
    df = df[df['ORIGEM'].isin(selected_origem)]

    pagamento_tolist = df['FORMA_PAGAMENTO'].unique().tolist()
    selected_pagamento = st.multiselect("Selecione a Forma de Pagamento:",
                                  options=pagamento_tolist, default=pagamento_tolist, key=99)
    df = df[df['FORMA_PAGAMENTO'].isin(selected_pagamento)]

    st.markdown('---')

tab1, tab2 = st.tabs(["📊 DASHBOARD", "📂 BASE DE DADOS"])

with tab1:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        search_cod_imovel = st.text_input('Pesquisar Código Imóvel:')
    with col2:
        search_proprietario = st.text_input('Pesquisar Proprietário:')
    with col3:
        search_inquilino = st.text_input('Pesquisar Inquilino:')

    if len(search_cod_imovel) == 0:
        df = df
    else:
        df = df[df['COD_IMOVEL'].str.contains(search_cod_imovel, case=False)]
    if len(search_proprietario) == 0:
        df = df
    else:
        df = df[df['PROPRIETARIO'].str.contains(search_proprietario, case=False)]
    if len(search_inquilino) == 0:
        df = df
    else:
        df = df[df['INQUILINO'].str.contains(search_inquilino, case=False)]

    with st.expander('Controle Avançado'):

        st.markdown('---')

        imovel_tolist = df['COD_IMOVEL'].unique().tolist()
        selected_imovel = st.multiselect("Selecione o Código do Imóvel:",
                                      options=imovel_tolist, default=imovel_tolist, key=58)
        df = df[df['COD_IMOVEL'].isin(selected_imovel)]

        st.markdown('---')

        proprietario_tolist = df['PROPRIETARIO'].unique().tolist()
        selected_proprietario = st.multiselect("Selecione o Proprietário do Imóvel:",
                                      options=proprietario_tolist, default=proprietario_tolist, key=88)
        df = df[df['PROPRIETARIO'].isin(selected_proprietario)]

        st.markdown('---')

        inquilino_tolist = df['INQUILINO'].unique().tolist()
        selected_inquilino = st.multiselect("Selecione o Inquilino do Imóvel:",
                                      options=inquilino_tolist, default=inquilino_tolist, key=78)
        df = df[df['INQUILINO'].isin(selected_inquilino)]

        st.markdown("---")

    st.markdown('---')

    valor_total_soma = int(df['VALOR_TOTAL'].sum())
    media_valor_diaria = int(df['VALOR_DIARIA'].mean())
    comissao_media = float(df['COMISSAO'].mean().round(1))

    dias_reserva_soma = int(df['DIAS_RESERVA'].sum())
    locacao_contagem = int(df['ID_LOCACAO'].count())
    imoveis_contagem = (df.groupby('COD_IMOVEL').count().reset_index(drop=False)).shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Imóveis Total", imoveis_contagem)
    col2.metric("Reservas Total", locacao_contagem)
    col3.metric("Dias com Reserva", dias_reserva_soma)

    col1, col2, col3 = st.columns(3)
    col1.metric("Comissão Média (%)", comissao_media)
    col2.metric("Diária Média (R$)", media_valor_diaria)
    col3.metric("Aluguel Total (R$)", valor_total_soma)



    valor_comissao_soma = int(df['VALOR_COMISSAO'].sum())
    valor_comissao_diaria_media = int(df['VALOR_COMISSAO_DIARIA'].mean())
    comissao_reserva = int(valor_comissao_soma / locacao_contagem)


    col1, col2, col3 = st.columns(3)
    col1.metric("Comissão por Reserva (R$)", comissao_reserva)
    col2.metric("Comissão Diária Média (R$)", valor_comissao_diaria_media)
    col3.metric("Comissão Total (R$)", valor_comissao_soma)


    st.markdown('---')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<h2 style='font-size:120%; text-align: center; color: black; padding: 10px 0px 10px 0px;'" +
                    ">Clientes por total de pedidos</h2>", unsafe_allow_html=True)

        uf_usuario = df.groupby('COD_IMOVEL', as_index=False)['ID_LOCACAO'].count().sort_values('ID_LOCACAO',
                                                                                                ascending=False).reset_index(
            drop=True)
        fig4 = bar_plot_horiz(uf_usuario.head(5), 'COD_IMOVEL', 'ID_LOCACAO',
                              '#FFD700', 'ID_LOCACAO', 'auto', 'black', dict(l=10, r=10, b=10, t=10))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("<h2 style='font-size:120%; text-align: center; color: black; padding: 10px 0px 10px 0px;'" +
                    ">Clientes por total de pedidos</h2>", unsafe_allow_html=True)

        uf_usuario = df.groupby('COD_IMOVEL', as_index=False)['VALOR_TOTAL'].sum().sort_values('VALOR_TOTAL',
                                                                                                ascending=False).reset_index(
            drop=True)
        fig5 = bar_plot_horiz(uf_usuario.head(5), 'COD_IMOVEL', 'VALOR_TOTAL',
                              '#FFD700', 'VALOR_TOTAL', 'auto', 'black', dict(l=10, r=10, b=10, t=10))
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})



    col1, col2 = st.columns([1, 1])
    with col1:
        fig7 = linha(df)
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

    with col2:
        fig8 = linha_valor_diaria(df)
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns([1, 1])
    with col1:

        fig9 = plot_hotmap1(df)
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})

    with col2:
        fig10 = plot_hotmap2(df)
        st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})

with tab2:
    st.dataframe(df)




