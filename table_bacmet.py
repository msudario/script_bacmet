import pandas as pd
import re
import argparse
import os

parser = argparse.ArgumentParser(
    description='Bu')
parser.add_argument('-csv', '--csv', metavar='', type=str, required=True,
                    help='path to the bacmet_gene_count.csv (from panvita results)')
parser.add_argument('-fasta', '--fasta', metavar='', type=str, required=True,
                    help='path to the bacmet_2.fasta (From panvita database)')
parser.add_argument('-txt', '--txt', metavar='', type=str, required=True,
                    help='path to the bacmet_2.txt (From panvita database)')
parser.add_argument('-o', '--output', metavar='', type=str, required=True,
                    help='path to where you want the output results')

args = parser.parse_args()

folder_input = os.path.expanduser(f'{args.csv}')
folder_input2 = os.path.expanduser(f'{args.fasta}')
folder_input3 = os.path.expanduser(f'{args.txt}')
folder_output = os.path.expanduser(f'{args.output}') + "resultados_do_script_bacmet.csv"

# Carrega os arquivos CSV em DataFrames do Pandas
database_bacmet = pd.read_csv(f'{folder_input}', sep=';')
database_bacmet_txt = pd.read_csv(f'{folder_input3}', sep='\t')

# Lista de genes do primeiro arquivo
genes = database_bacmet['Genes']

# criando uma lista de genes para usar
lista_de_genes = []
for cada_gene in genes:
    lista_de_genes.append(cada_gene)
    
    
""" BUSCANDO O COMPOUND NO .TXT """

def buscador_gene_compound():
    # Cria um dicionário para armazenar os resultados
    gene_to_compound = {}

    # Itera sobre cada gene na lista
    for cada_gene in lista_de_genes:
        filtro = database_bacmet_txt["Gene_name"] == cada_gene
        if filtro.any():
            valor_compound = database_bacmet_txt.loc[filtro, "Compound"].iloc[0]
            gene_to_compound[cada_gene] = valor_compound

    return gene_to_compound

# Chama a função e obtém o dicionário
resultado_gene_to_compound = buscador_gene_compound()


""" BUSCANDO O MECHANISM NO .CSV """

def buscador_gene_mechanism():
    lista_de_mecanismos = []
    with open(f'{folder_input2}', "r") as file:
            lista_de_linhas_com_identificador  = []
            for line in file:
                if line.startswith('>'):
                    lista_de_linhas_com_identificador.append(line.strip())
            
            for gene in lista_de_genes:
                padrao_mecanismo = rf"{gene}"
                
                for cada_linha_com_identificador in lista_de_linhas_com_identificador:
                    if re.search(padrao_mecanismo, cada_linha_com_identificador):
                        lista_de_mecanismos.append(cada_linha_com_identificador)
                        
                        
                        break  # Para sair do loop interno assim que a primeira ocorrência for encontrada
            return lista_de_mecanismos
                
resultados_buscador_de_mecanismos = buscador_gene_mechanism()


def extraindo_mechanism_do_buscador_de_mecanismos(resultados_buscador_de_mecanismos):
    lista_de_mecanismos2 = []
    padrao_mechanism = r' [A-Z].*?(?= OS=)'
    
    for cada_linha in resultados_buscador_de_mecanismos:
        match_padrao_mechanism = re.search(padrao_mechanism, cada_linha)
        
        if match_padrao_mechanism:
            conteudo_entre = match_padrao_mechanism.group(0).strip()
            lista_de_mecanismos2.append(conteudo_entre)
            
    return lista_de_mecanismos2

# Chamando a função para extrair mecanismos dos resultados
resultados_extraidos = extraindo_mechanism_do_buscador_de_mecanismos(resultados_buscador_de_mecanismos)


# Fazendo uma variavel para usar na tabela com os valores do dicionario
compounds = []
for valor in resultado_gene_to_compound.values():
    compounds.append(valor)
    
# Criar um DataFrame do pandas para a tabela
data = {
    "Gene": lista_de_genes,
    "Mechanism": resultados_extraidos,
    "Compound": compounds

}
df = pd.DataFrame(data)

# Salvar a tabela em um arquivo CSV
df.to_csv(folder_output, index=False)
