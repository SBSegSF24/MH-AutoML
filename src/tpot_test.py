import time
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from tpot import TPOTClassifier
from datetime import datetime
import os
import argparse

def formatar_tempo(tempo_segundos):
    horas = int(tempo_segundos / 3600)
    minutos = int((tempo_segundos % 3600) / 60)
    segundos = int(tempo_segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"



def run_tpot(dataset_file):
    dataset = pd.read_csv(dataset_file)
    X = dataset.drop('class', axis=1)
    y = dataset['class']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)

    pipeline_optimizer = TPOTClassifier(verbosity=3, n_jobs=-1, generations=5, population_size=50)
    start_time = time.time()
    try:
        pipeline_optimizer.fit(X_train, y_train)
        end_time = time.time()
        total_time = formatar_tempo(end_time - start_time)

        y_pred = pipeline_optimizer.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results = {
            'dataset': dataset_file,
            'tempo': total_time,
            'acuracia': accuracy,
            'precisao': precision,
            'recall': recall,
            'f1': f1
        }

        return results

    except Exception as e:
        print(f'Erro ao executar a ferramenta TPOT no dataset {dataset_file}: {e}')
        return None

def processar_todos_csv_pasta(pasta, output_dir):
    resultados = []

    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith(".csv"):
                dataset_file = os.path.join(root, file)
                print(f"Processando arquivo: {dataset_file}")
                resultado = run_tpot(dataset_file)
                if resultado:
                    resultados.append(resultado)

    resultados_df = pd.DataFrame(resultados)
    resultados_df.to_csv(os.path.join(output_dir, "resultados_tpot.csv"), index=False)
    print(f"Resultados salvos em CSV no diretório {output_dir}.")

if __name__ == "__main__":
    

    processar_todos_csv_pasta('datasets', '/app/output')
