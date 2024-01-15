import sqlite3
import pandas as pd
from datetime import datetime


def formatar_data(data=None):
    if data:
        try:
        # Tentativa de conversão para o formato ano/mes/dia
            data_formatada = datetime.strptime(data, '%Y/%m/%d').strftime('%Y/%m/%d')
        except ValueError:
            try:
                # Tentativa de conversão para o formato dia/mes/ano
                data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%Y/%m/%d')
            except ValueError:
                # Tentativa de conversão para o formato dia mês ano
                try:
                    data_formatada = datetime.strptime (data, '%d %m %Y').strftime ('%Y/%m/%d')
                except ValueError:
                    data_formatada = datetime.strptime (data, '%d%m%Y').strftime ('%Y/%m/%d')
        return data_formatada
    else:
        return data


def adicionar_gastos(cursor, data, descricao, valor, categoria, pessoa, tipo):
    insert_query = """
    INSERT INTO gastos (data, descricao, valor, categoria, pessoa, tipo)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    cursor.execute(insert_query, (data, descricao, valor, categoria, pessoa, tipo))


def visualizar_gastos(conn, pessoa=None, tipo=None, data_inicial=None, data_final=None, categoria=None):
    select_query = "SELECT * FROM gastos WHERE 1=1"

    if pessoa:
        select_query += f" AND pessoa = '{pessoa}'"

    if tipo:
        select_query += f" AND tipo = '{tipo}'"

    if data_inicial and data_final:
        select_query += f" AND data BETWEEN '{data_inicial}' AND '{data_final}'"

    if categoria:
        select_query += f" AND categoria = '{categoria}'"

    return pd.read_sql_query(select_query, conn)


def calculos_de_despesas_receitas(cursor, operacao, data_inicial, data_final, tipo=None, categoria=None, pessoa=None):

    if operacao == '1':

        query = "SELECT SUM(valor) FROM gastos WHERE 1=1"
        params = []

        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        if pessoa:
            query += " AND pessoa = ?"
            params.append(pessoa)

        if data_inicial and data_final:
            query += " AND data BETWEEN ? AND ?"
            params.append(data_inicial)
            params.append(data_final)

        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        return total

    if operacao == '2':
        query = """
            SELECT categoria, SUM(valor) AS total_por_categoria
            FROM gastos
            WHERE tipo = ?
            GROUP BY categoria
            """

        cursor.execute (query, (tipo,))
        results = cursor.fetchall ()

        total_geral = sum (result[1] for result in results)  # Calcula o total geral

        # Calcula a porcentagem para cada categoria
        porcentagens = {}
        for categoria, total in results:
            porcentagem = (total / total_geral) * 100 if total_geral != 0 else 0
            porcentagens[categoria] = porcentagem

        return porcentagens


def excluir_gastos(cursor, lista_de_ids, data_inicial=None, data_final=None):
    delete_by_ids_query = """
    DELETE FROM gastos
    WHERE id IN ({});
    """.format(', '.join('?' * len(lista_de_ids)))

    params = lista_de_ids  # Passando somente os IDs como parâmetro

    if data_inicial:
        delete_by_ids_query += " AND data >= ?"  # Ajuste da query para a data inicial
        params.append(data_inicial)

    if data_final:
        delete_by_ids_query += " AND data <= ?"  # Ajuste da query para a data final
        params.append(data_final)

    cursor.execute(delete_by_ids_query, params)  # Passando os parâmetros corretamente


conn = sqlite3.connect('DATA.db')

cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS gastos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa TEXT,
    data TEXT,
    descricao TEXT,
    valor REAL,
    categoria TEXT,
    tipo TEXT
);
"""


cursor.execute(create_table_query)

print('Bem vindo ao seu gestor de gastos!!!!')
while True:
    print('Como posso te ajudar?')

    print("""Insira o numero da sua solicitação.\n1-Visualizar.\n2-Adicionar gastos.
3-Remover gastos\n4-calculo das receitas e das despesas.
5-Finalizar.\n""")

    opcao = input('\n\nInsira aqui: ')

    if opcao == '1':
        data_inicial = formatar_data (input ('Qual a data inicial?: '))
        data_final = formatar_data (input ('Qual a data final?: '))
        pessoa = input ('Pessoa: ')
        tipo = input('Tipo: ')
        categoria = input('Categoria: ')
        print (f"Data Inicial: {data_inicial}, Data Final: {data_final}, Pessoa: {pessoa}, Tipo: {tipo}")
        print (visualizar_gastos (conn,  pessoa, tipo, data_inicial, data_final, categoria))
    elif opcao == '2':
        data = formatar_data(input('Data: '))
        descricao = input('Descrição: ')
        valor = input('Valor: ')
        categoria = input('Categoria: ')
        pessoa = input('Pessoa: ')
        tipo = input('Tipo: ')
        adicionar_gastos(cursor, data, descricao, valor, categoria, pessoa, tipo)
        print('\n\nOperação realizada com sucesso!!!\n\n')
    elif opcao == '3':
        ids_a_deletar = input('Quais os ids a serem deletados?: ')
        lista_de_ids = [str(id)for id in ids_a_deletar.split(',')]
        data_inicial = formatar_data (input ('Qual a data inicial?: '))
        data_final = formatar_data (input ('Qual a data final?: '))
        if data_inicial.strip() and data_final.strip():
            data_inicial, data_final = None, None
        excluir_gastos(cursor, lista_de_ids, data_inicial, data_final)
        print('\n\nOperação realizada com sucesso!!!\n\n')
    elif opcao == '4':
        operacao = input ('Qual será a operação?: \n1- total\n2- porcentagem\n')
        data_inicial = formatar_data (input ('Qual a data inicial?: '))
        data_final = formatar_data (input ('Qual a data final?: '))
        categoria = input('Categoria: ')
        pessoa = input('Pessoa: ')
        tipo = input('Tipo: ')
        print(calculos_de_despesas_receitas(cursor,operacao, data_inicial, data_final, tipo, categoria, pessoa))
        print('\n\nOperação realizada com sucesso!!!\n')
    elif opcao == '5':
        print('\nSaindo, obrigado e até mais!!')
        break

conn.commit()
conn.close()