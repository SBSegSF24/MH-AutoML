import pandas as pd
import autosklearn.classification
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import os
import timeit
import argparse

# Função para rodar o Auto-Sklearn em um arquivo CSV específico
def run_autosklearn(dataset_file):
    dataset = pd.read_csv(dataset_file)
    X = dataset.drop('class', axis=1)
    y = dataset['class']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)

    start_time = timeit.default_timer()

    try:
        automl = autosklearn.classification.AutoSklearnClassifier(
            memory_limit=None, time_left_for_this_task=3600, per_run_time_limit=300
        )
        automl.fit(X_train, y_train)

        m, s = divmod(timeit.default_timer() - start_time, 60)
        h, m = divmod(m, 60)
        time_str = "%02d:%02d:%02d" % (h, m, s)

        # Prever os rótulos para o conjunto de teste
        y_pred = automl.predict(X_test)

        # Calcular as métricas de desempenho
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='macro')
        precision = precision_score(y_test, y_pred, average='macro')
        recall = recall_score(y_test, y_pred, average='macro')

        # Salvar as métricas em um dicionário
        results = {
            'dataset': dataset_file,
            "tempo": time_str,
            "acuracia": accuracy,
            "precisao": precision,
            "recall": recall,
            "f1": f1
        }

        return results

    except Exception as e:
        print(f'Erro Auto-Sklearn dataset {dataset_file}: {e}')
        return None

# Função principal para processar todos os arquivos CSV na pasta
def processar_todos_csv_pasta(pasta):
    resultados = []
    
    # Itera sobre todos os arquivos na pasta
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith(".csv"):
                dataset_file = os.path.join(root, file)
                print(f"Processando arquivo: {dataset_file}")
                resultado = run_autosklearn(dataset_file)
                if resultado:
                    resultados.append(resultado)

    # Salva todos os resultados em um único DataFrame
    resultados_df = pd.DataFrame(resultados)
    resultados_df.to_csv("/app/output/resultados_autosklearn.csv", index=False)
    print("Resultados salvos em CSV no diretório /app/output.")

# Função para processar um único arquivo CSV
def processar_arquivo_csv(arquivo_csv):
    resultado = run_autosklearn(arquivo_csv)
    if resultado:
        resultados_df = pd.DataFrame([resultado])
        resultados_df.to_csv("/app/output/resultados_autosklearn.csv", index=False)
        print("Resultado salvo em CSV no diretório /app/output.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processa arquivos CSV com Auto-Sklearn.")
    parser.add_argument("input_path", type=str, help="Caminho para a pasta com datasets ou um único arquivo CSV.")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input_path):
        processar_todos_csv_pasta(args.input_path)
    elif os.path.isfile(args.input_path) and args.input_path.endswith(".csv"):
        processar_arquivo_csv(args.input_path)
    else:
        print("O caminho fornecido não é um arquivo CSV válido ou uma pasta.")
