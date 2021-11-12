# Processamento Aster

## Recursos
- [Instalação](Instalação)
    - [Configurando o VS code](Configurando-o-VS-code)
    - [Instalando Bibliotecas](Instalando-Bibliotecas)
- [Execução](Execução)
    - [Primeira Execução](Primeira-Execução)
    - [Parametros Editáveis](Parametros-Editáveis)

## Instalação
*Você precisará do software [Visual Studio Code](https://code.visualstudio.com/Download) instalado. Além da linguagem de programação [Python](https://www.python.org/downloads/) versão 3.9.
* Baixe o [repositório](https://gitlab.com/GabrielFS1/processamento-aster) com os programas e bibliotecas requeridos e descompacte na pasta onde ficarão as imagens do processamento.


### Configurando o VS code
Com todos arquivos baixados prossiga para a instalação das bibliotecas. Inicialmente abra o Visual Studio Code e instale a extensão Python presionando **Ctrl + Shift + X** e digitando _python_, baixe a primeira extensão mostrada.

Para ir até o diretório no qual as pasta foram descompactadas. **File** > **Open Folder** e selecione a pasta com os arquivos.

Abra o terminal usando **Ctrl + '** e digite os comandos abaixo:

### Instalando Bibliotecas
```
python -m pip install -r requirements.txt
python -m pip install wheel
python -m pip install GDAL-3.2.2-cp39-cp39-win_amd64.whl
python -m pip install rasterio‑1.2.1‑cp39‑cp39‑win_amd64.whl GDAL‑3.2.2‑cp39‑cp39‑win_amd64.whl
python -m pip install Cartopy‑0.19.0.post1‑cp39‑cp39‑win_amd64.whl
```

## Execução
### Primeira Execução

Para iniciar a execução do programa digite o seguinte comando no terminal

```python aster.py```

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



