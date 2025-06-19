



# Groq AI
  
Módulo para interagir com os modelos do Groq AI a partir do Rocketbot.  

*Read this in other languages: [English](Manual_GroqAI.md), [Português](Manual_GroqAI.pr.md), [Español](Manual_GroqAI.es.md)*
  
![banner](imgs/Banner_GroqAI.png o jpg)
## Como instalar este módulo
  
Para instalar o módulo no Rocketbot Studio, pode ser feito de duas formas:
1. Manual: __Baixe__ o arquivo .zip e descompacte-o na pasta módulos. O nome da pasta deve ser o mesmo do módulo e dentro dela devem ter os seguintes arquivos e pastas: \__init__.py, package.json, docs, example e libs. Se você tiver o aplicativo aberto, atualize seu navegador para poder usar o novo módulo.
2. Automático: Ao entrar no Rocketbot Studio na margem direita você encontrará a seção **Addons**, selecione **Install Mods**, procure o módulo desejado e aperte instalar.  

## Como usar este módulo

Para usar este módulo, precisamos obter a chave API do Groq. Siga estes passos:

1. Primeiro, crie uma conta Groq ou faça login em [console.groq.com](https://console.groq.com/keys).

2. Uma vez na página de chaves API, clique no botão "Create API Key" para criar uma nova chave.

3. Uma janela será aberta onde você precisará:
   - Inserir um nome de referência para a chave (máximo de 50 caracteres)
   - Completar a validação do Cloudflare

4. Clique no botão "Submit" para gerar a chave.

5. A chave API será exibida na tela. Use o botão "Copy" para copiá-la.

**Importante**: Certifique-se de salvar a chave em um local seguro, pois você não poderá vê-la novamente depois de fechar esta janela.
## Descrição do comando

### Conectar com Groq AI
  
Estabelece conexão com Groq AI
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|API Key|Sua chave de API do Groq AI|gsk_abc123...|
|Atribuir à variável|Nome da variável para armazenar a conexão|resultadoGroqAi|

### Obter Modelos
  
Recupera os modelos disponíveis do GroqAI
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Atribuir à variável|Nome da variável para armazenar a lista de modelos|resultadoModelos|

### Gerar Texto
  
Gera texto usando o GroqAI
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Prompt|Texto de entrada para gerar texto|O que é Rocketbot?|
|Modelo|ID do modelo a ser usado|compound-beta-mini|
|Temperatura (opcional)|Controla a aleatoriedade da geração de texto (0.0 a 2)|0.8|
|Máximo de tokens (opcional)|Número máximo de tokens a serem gerados|100|
|Sequência de parada (opcional)|Sequência opcional para parar a geração de texto|ferramenta RPA|
|Atribuir à variável|Nome da variável para armazenar o texto gerado|resultadoTexto|

### OCR para Imagem
  
Processa uma imagem com o OCR do GroqAI
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo|Nome do modelo OCR a ser usado|meta-llama/llama-4-scout-17b-16e-instruct|
|Arquivo ou URL|Permite fazer o upload de um arquivo local ou entrar uma url para um arquivo online|Caminho ou URL do arquivo|
|Mensagem (opcional)|Instrução personalizada para o modelo sobre o que procurar ou extrair da imagem|Por favor, descreva o que você vê nesta imagem.|
|Temperatura (opcional)|Valor entre 0 e 2. Valores mais baixos são mais precisos, valores mais altos são mais criativos. Padrão 0.7|0.7|
|Atribuir à variável|Nome da variável para armazenar o resultado do OCR|resultadoOCR|

### Transcrição de Áudio
  
Transcreve arquivos de áudio usando o serviço Speech-to-Text do GroqAI
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo|ID do modelo a usar (ex whisper-large-v3)|whisper-large-v3|
|Arquivo ou URL|Caminho do arquivo de áudio ou URL (formatos flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm)|Selecione um arquivo ou cole uma URL|
|Idioma (opcional)|Código ISO-639-1 do idioma (ex pt, en, es, pr)|es, en, pt, pr|
|Temperatura (opcional)|Valor entre 0 e 1 (padrão 0)|0.2|
|Atribuir à variável|Nome da variável onde será salva a transcrição|transcription|
