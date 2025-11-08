import pandas as pd

# df = pd.read_excel("BancoVDE 2023.xlsx")  
# homicidios = df[df["evento"] == "Tentativa de homicídio"]
# homicidios.to_csv("homicidios2023.txt", sep=";", index=False)

class Limpa_arquivo:
    def load_homicidios(self,tabela_homicidios):
        
        df = pd.read_csv(tabela_homicidios, sep=";")

        # Remove colunas 100% vazias
        self.df = df.dropna(axis=1, how="all")

        # Salva de volta no TXT
        return self.df.to_csv("limpo.txt", sep=";", index=False)

    def load_datasus(tabela_datasus):
        df = pd.read_csv(tabela_datasus, sep=";", header=0)

        df = df.dropna(axis=1, how="all")

        df = df.replace("-",0)


        # Salva de volta no TXT
        return df

