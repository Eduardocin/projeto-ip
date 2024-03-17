import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nbformat
import copy
import statsmodels.api as sm


class MultiData():
    def __init__(self, datadict):
        self.datas = copy.deepcopy(datadict)
        self.names = [df for df in datadict]
        for name in self.names:
            self.datas[name] = self.change_to_DataTable(self.datas[name], name)
        

    # Acessar os dataframes por índice
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.datas[self.names[key]]
        else:
            return self.datas[key]

    
    # Formatação para printar os nomes dos dataframes
    def __str__(self):
        return f'{" | ".join(self.names)}'
    

    def autoplot(self, index, tamanho=(8,8), n=0):
        df = self[index]
        if not n:
            n = len(df.columns.values)
        # Decorações
        self.decorate(n=n, tamanho=tamanho)
        decorado = True
        

        # Selecionando as colunas a plotar
        pick = df.copy(deep=True)
        top = pick.max()
        bot = pick.min()
        offsets = top - bot
        offsets.apply(lambda x: abs(x))
        offsets.sort_values(ascending=True, inplace=True)
        pick = offsets.index.values[:n]
        
        # Plotando
        self.plot_selection(df, pick, decorado)


    def plot_selection(self, df, pick=[], decorado=False):
        if not decorado:
            self.decorate(n=len(pick))
        
        if len(pick) == 0:
            pick = df.columns.values
        
        for i in df.columns:
            if i in pick:
                plt.plot(df.index.values, df[i], label=i)
        plt.title(f'{df.name.replace("_", " ")}')
        plt.legend(bbox_to_anchor=(1.1,0.9))
        plt.grid(which='both', alpha=0.5)
        plt.show()
    
    
    def decorate(self, n, tamanho=(8,8)):
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('#949997')
        plt.minorticks_on()
        plt.rcParams["figure.figsize"] = tamanho
        self.ax.set_prop_cycle('color', plt.cm.nipy_spectral(np.linspace(0, 1, n)))
        
        
    def change_to_DataTable(self, df, name):
        df_copy = DataTable(columns = df.columns, data = copy.deepcopy(df.values), name=name)
        return df_copy
    
    
    def projection_var(self, training_years, columns): # Forecasting exclusivam
          # Criando um dataframe com as colunas que o usuário escolheu
        df = pd.DataFrame()
        for column in columns:
              self[column[0]][column[1]]
              pd.concat([df, column], axis=1)
        training_data = df[:training_years] ## splicing do dataframe
        
        if training_years == len(df):
              pass # Para o futuro
        
        # Código de projeção
        model = sm.tsa.VAR(np.asarray(training_data, dtype='float'))
        model_fit = model.fit()
        prediction = pd.DataFrame(model_fit.forecast(model.endog, steps=(len(df)-training_years))) ## gerado o dataframe com a projeção dos próximos anos
        prediction.index = [training_data.index[-1] + pd.offsets.DateOffset(years=i) for i in range(len(prediction))]
        prediction.rename(columns={i: name for i, name in enumerate(columns)}, inplace=True)
        forecast = pd.concat([training_data, prediction])
        forecast.rename(column={name: (name + ' projetado') for name in forecast.columns.values})
        pd.concat([forecast, df], axis=1)
        self.plot_selection(df=forecast)
    
    
class DataTable(pd.DataFrame):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self['ANO'] = pd.to_datetime(self['ANO'], format='%Y')
        if self.index.name != 'ANO' and ('ANO' in self.columns):
            self.set_index('ANO', drop=True, inplace=True)
        else:
            self.index = pd.to_datetime(pd.Series([ano for ano in range(1970, 2023)]))
            self.index.name='ANO'

