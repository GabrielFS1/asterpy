# Processamento Aster

## Recursos
- [Instalação](Instalação)
    - [Criando venv](Criando-o-venv)
    - [Instalando Bibliotecas](Instalando-Bibliotecas)
- [Execução](Execução)
    - [Primeira Execução](Primeira-Execução)
    - [Parametros Editáveis](Parametros-Editáveis)

## Instalação
* Você precisará ter o [Python](https://www.python.org/downloads/) versão 3.9 instalado em sua máquina.


### Clone o repositório
Usando o Prompt de comando vá para a pasta desejada e use o comadno git clone para clonar o código

```git clone https://github.com/GabrielFS1/asterpy.git```

### Criando o venv
Com todos arquivos baixados prossiga para a instalação das bibliotecas. Abra o Prompt de comando do windows digitando cmd na barra de pesquisa e vá até a pasta `asterpy` utilizando `cd nomeDaPasta` até a que se chegue a pasta **asterpy**.

Estando no diretório crie o venv usando 
```python -m venv venv```

Em caso de falha de permissões utilizar esse comando no **PowerShell** com permissão de administrador.

```set-executionpolicy RemoteSigned```

Para ativar o ambiente virtual no qual serão instaladas as bibliotecas digite ```.\venv\Scripts\activate```. Sera possível ver a escrita (venv) antes da especificação do diretório.

### Instalando Bibliotecas

Estando dentro do venv digite o comando 

```
python -m pip install -r requirements.txt
```

## Execução
### Primeira Execução

Para iniciar a execução do programa digite o seguinte comando no cmd

```python main.py```

Na primeira execução o programa criará todas as pastas necessárias. As imagens brutas devem ser descompactadas na pasta **00_Arquivos**, no qual a pasta com as figuras deve conter o nome da cena. Ao executar o programa um menu com três opções será mostrada no qual podem ser selecionadas as seguintes opções:

- (1) Processa todas as imagem na pasta _00_Arquivos_ em sequência.
- (2) Irá processar a imagem selecionada, a opção também serve para refazer todos os arquivos da cena determinada
- (0) Finaliza o programa.

### Parametros Editáveis

No ínicio do programa é possível editar os parmetros que determinam o diretório onde os arquivos serão salvos e a resolução da composição VNIR, que servirá de auxilio para o recorte do histograma. O código pelo qual devem ser feitas essas alterações se econtram após a importação das bibliotecas e isolados pelos simbolos **#**.
```
############################################

# Define o dirétório padrão onde as pastas ficarão salvas
path = ('')

# Resolução da composição coloridas das bandas VNIR
resolution_merge = 60

###########################################
```

### Recorte do histograma
A tela principal do programa é exibida em janelas sendo, o histograma interativo que permite determinar o alcançe dos valores; a imagem recortada sendo atualizada em tempo real junto com a janela de zoom e para as cenas que tenhas as bandas VNIR a composição colorida (3N, 2 e 1) será exibida.

- A partir da página do histograma é possível mover as linhas tracejadas, além disso clicando no X presente no lando superior direito é possível finalizar a execução do programa.
- Ao clicar e arrastar o mouse na imagem dó índice recortado ou da composição colorida irá mover o ponto de zoom simultaneamente nas duas janelas de zoom.
- Para salvar a imagem após finalizar o recorte do ajuste, clique com o botão direito do mouse na imagem do índice, disposta a esquerda.

### Tabela de dados
Cada valor definido para o recorte do histograma é armazenada em um banco de dados contido no arquivo _aster_dados.db_. Uma alternativa para converter esse dados em um formato acessível, como excel é baixando o programa open source [DB Browser(SQLite)](https://sqlitebrowser.org/dl/) e exportando a tambela como CSV.


## Download Imagens
Para realizar o download das imagens ASTER é necessário acessar o site https://search.earthdata.nasa.gov/search e pesquisar pelo produto aster desejado. Na busca é possível colocar alguns filtros como porcentagem de nuvens, periodo diurno, entre outros. Para selecionar a área, você pode fazer upload de um shape ou desenhar um polígono no mapa.
