import os
import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def main():
    """
    Função para treinar o modelo de clusterização e salvar os modelos para uso na API.
    """

    try:
        df = pd.read_csv('data/livros.csv')
    except FileNotFoundError:
        print("Erro: Arquivo 'data/livros.csv' não encontrado.")
        print("Por favor, execute o web scraper primeiro.")
        return
    
    # Feature Engineering
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df['avaliacao_num'] = df['avaliacao'].map(rating_map)

    # Seleciona as features do modelo
    features = df[['preco', 'avaliacao_num']].dropna()

    # Normalização das features para melhor desempenho do kmeans
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    print("Features escalonadas com sucesso.")

    kmeans = KMeans(n_clusters=5, random_state=42, n_init='auto')
    kmeans.fit(features_scaled)
    print("Modelo K-Means treinado com sucesso.")

    # Criar a pasta para armazenar os modelos
    output_dir = 'models'
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, 'kmeans_model.joblib')
    scaler_path = os.path.join(output_dir, 'scaler.joblib')

    joblib.dump(kmeans, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"Modelo salvo em: {model_path}")
    print(f"Scaler salvo em: {scaler_path}")
    print("\nTreinamento concluído!")

if __name__ == "__main__":
    main()
    