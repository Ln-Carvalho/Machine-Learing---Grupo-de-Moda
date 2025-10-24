import pandas as pd
import sys

# --- 1. CONFIGURAÇÃO ---
# Nome do arquivo CSV que você anexou
arquivo_entrada = "prim_ver_24(n tratado).csv"

# Nome do arquivo que vamos criar
arquivo_saida = "dataset_tratado_pv24.csv"

print(f"Iniciando tratamento do arquivo: {arquivo_entrada}")

# --- 2. CARREGAR OS DADOS ---
try:
    # 'delimiter=';' é a chave aqui!
    # 'encoding="latin1"' é comum para arquivos vindos de Excel em português
    df = pd.read_csv(arquivo_entrada, delimiter=';', encoding="latin1")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(arquivo_entrada, delimiter=';', encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        print("Verifique se o arquivo está na mesma pasta que o script.")
        sys.exit()
except FileNotFoundError:
    print(f"ERRO: Arquivo '{arquivo_entrada}' não encontrado.")
    print("Certifique-se de que o arquivo CSV está na mesma pasta que este script.")
    sys.exit()

print(f"Arquivo original carregado com {df.shape[0]} linhas.")

# --- 3. FILTRAR APENAS "SACADA" ---
if 'GRIFFE' not in df.columns:
    print("ERRO: Coluna 'GRIFFE' não encontrada. Verifique o cabeçalho do CSV.")
    sys.exit()

df_filtrado = df[df['GRIFFE'] == 'SACADA'].copy()
print(f"Filtrado para {df_filtrado.shape[0]} linhas da GRIFFE 'SACADA'.")

if df_filtrado.empty:
    print("Aviso: Nenhum dado da 'SACADA' foi encontrado. Verifique o nome no arquivo.")
    sys.exit()

# --- 4. SELECIONAR E RENOMEAR COLUNAS ---
mapeamento_colunas = {
    'VENDA_QT_TOTAL': 'Y_Venda_Total_Colecao',
    'VENDA_QT_30_DIAS': 'X_Venda_30_Dias',
    'GRUPO_PRODUTO': 'X_Categoria',
    'FILIAL': 'X_Cluster_Loja',
    'DESC_COR': 'X_Cor_Agrupada',
    'PV_ORIGINAL': 'X_Preco_Cheio',
    'COLECAO': 'X_Tipo_Colecao',
    'PRODUTO': 'ID_Produto',
    'DESC_PRODUTO': 'Descricao_Produto'
}

colunas_necessarias = list(mapeamento_colunas.keys())
for col in colunas_necessarias:
    if col not in df_filtrado.columns:
        print(f"ERRO: Coluna necessária '{col}' não encontrada no arquivo.")
        sys.exit()

df_selecionado = df_filtrado[colunas_necessarias].copy()
df_selecionado.rename(columns=mapeamento_colunas, inplace=True)
print("Colunas selecionadas e renomeadas.")

# --- 5. LIMPEZA E TRATAMENTO DOS DADOS ---

# 5.1 Colunas Numéricas (Limpando vírgulas e preenchendo nulos)
colunas_numericas = ['Y_Venda_Total_Colecao', 'X_Venda_30_Dias', 'X_Preco_Cheio']

for col in colunas_numericas:
    # Converte para string, troca vírgula por ponto
    df_selecionado[col] = df_selecionado[col].astype(str).str.replace(',', '.')
    # Converte para numérico (erros viram NaN)
    df_selecionado[col] = pd.to_numeric(df_selecionado[col], errors='coerce')

# Preenche vendas nulas (NaN) com 0
df_selecionado['Y_Venda_Total_Colecao'] = df_selecionado['Y_Venda_Total_Colecao'].fillna(0)
df_selecionado['X_Venda_30_Dias'] = df_selecionado['X_Venda_30_Dias'].fillna(0)

# Para o Preço, preenche nulos com a mediana (valor do meio)
median_price = df_selecionado['X_Preco_Cheio'].median()
df_selecionado['X_Preco_Cheio'] = df_selecionado['X_Preco_Cheio'].fillna(median_price)
print(f"Limpeza de dados numéricos concluída. Preço nulo preenchido com {median_price:.2f}.")

# 5.2 Colunas Categóricas (Textos)
df_selecionado['X_Categoria'] = df_selecionado['X_Categoria'].str.upper().str.strip()

# Limpa 'X_Cluster_Loja' (ex: "SACADA BARRA SHOPPING-RJ" vira "SACADA BARRA SHOPPING")
df_selecionado['X_Cluster_Loja'] = df_selecionado['X_Cluster_Loja'].apply(
    lambda x: str(x).split('-')[0].strip()
)

# Padroniza 'X_Tipo_Colecao' (ex: "VER25" ou "PRIM25" vira "PV")
df_selecionado['X_Tipo_Colecao'] = 'PV'

# Padroniza 'X_Cor_Agrupada' (limpeza básica)
df_selecionado['X_Cor_Agrupada'] = df_selecionado['X_Cor_Agrupada'].str.upper().str.strip()

# **** ATENÇÃO AQUI ****
# Adicione seus agrupamentos de cor aqui
mapeamento_cores = {
    'PRETO INTENSO': 'PRETO',
    'OFF WHITE': 'BRANCO',
    'BRANCO OFF': 'BRANCO',
    # Adicione mais mapeamentos conforme sua regra de negócio
    # Ex: 'EST LISTRA FRESH YO': 'ESTAMPADO'
}
df_selecionado['X_Cor_Agrupada'] = df_selecionado['X_Cor_Agrupada'].replace(mapeamento_cores)
print("Limpeza de dados categóricos concluída.")

# --- 6. SALVAR O ARQUIVO TRATADO ---
try:
    # 'index=False' para não salvar o índice do pandas
    # 'encoding='utf-8-sig'' garante que o Excel leia os acentos corretamente
    df_selecionado.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
    
    print("\n--- SUCESSO! ---")
    print(f"Arquivo '{arquivo_saida}' foi criado com {df_selecionado.shape[0]} linhas tratadas.")
    print("\nVisualização das primeiras 5 linhas do arquivo final:")
    print(df_selecionado.head())

except Exception as e:
    print(f"\nErro ao salvar o arquivo: {e}")