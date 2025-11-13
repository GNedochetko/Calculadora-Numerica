# Trabalho de Cálculo Numérico – Zeros de Funções e Sistemas Lineares

Aplicativo desktop em Python/Tkinter que reúne dois módulos principais usados na disciplina de Cálculo Numérico:

- **Zeros de funções** – prepara a entrada de dados, chama o executável `Calculadora0Func.exe` (escrito em C++) e exibe os resultados produzidos pelos métodos da apostila (Bisseção, MIL, Newton, Secante e Regula Falsi).
- **Sistemas lineares** – fornece uma interface para montar a matriz `A` e o vetor `b`, e resolve o sistema utilizando algoritmos implementados em `sistemas.py`.

## Recursos disponíveis
- GUI única para escolher entre zeros de funções e sistemas lineares.
- Persistência temporária dos dados via `entrada.txt`/`saida.txt`, permitindo reutilizar o executável legado.
- Métodos diretos para sistemas lineares:
  - Eliminação de Gauss sem pivoteamento.
  - Gauss com pivoteamento parcial.
  - Gauss com pivoteamento completo.
  - Fatoração LU (sem pivoteamento, com validação do determinante).
  - Fatoração de Cholesky (inclui checagem de simetria e definição positiva).
- Medição do tempo de execução e apresentação amigável dos resultados.
- Tratamento de erros comuns (entradas inválidas, matrizes singulares, ausência de método selecionado etc.).

> **Observação:** as opções “Método iterativo de Gauss Jacobi” e “Método iterativo de Gauss Seidel” já aparecem na interface (menu suspenso), porém ainda não estão mapeadas em `METODOS_SISTEMA`, logo o app avisará que não há implementação quando essas opções são escolhidas.

## Pré-requisitos
- Python 3.10+ com Tkinter disponível (vem por padrão nas builds oficiais).
- Executável `Calculadora0Func.exe` com permissão de execução e os arquivos `entrada.txt`/`saida.txt` na raiz do projeto (o fluxo do módulo de zeros depende disso).

## Como executar
1. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```
2. Entre na pasta do projeto e execute:
   ```bash
   python app.py
   ```
3. A janela “Trabalho 2 CN” será aberta, oferecendo as duas opções principais.

## Uso do módulo “Zero de funções”
1. Clique em **zero de funções** na tela inicial.
2. Preencha os campos exibidos (função `f(x)`, intervalo `[a, b]`, precisão, máximo de iterações e função auxiliar `g(x)` quando necessário).
3. Pressione **Calcular**:
   - Os valores são gravados em `entrada.txt`.
   - O programa chama `./Calculadora0Func.exe`.
   - Os resultados são lidos de `saida.txt` e mostrados em um único diálogo.
4. Clique em **OK** para retornar à tela inicial.

Se o executável não estiver presente, for inacessível ou retornar código de erro, a interface mostrará uma mensagem explicativa.

## Uso do módulo “Sistemas lineares”
1. Clique em **Sistemas lineares**.
2. Informe a ordem da matriz (inteiro positivo) e escolha um método.
3. Preencha a matriz `A` e o vetor `b`.
4. Clique em **Calcular**:
   - Os dados são validados.
   - O método escolhido é invocado (funções em `sistemas.py` trabalham apenas com listas nativas; não há dependências externas).
   - O resultado exibe cada incógnita `xᵢ` arredondada e o tempo em milissegundos.
5. Utilize **Voltar** para trocar o método ou ajustar a ordem.

### Implementação dos métodos (`sistemas.py`)
- **`gauss_sem_pivo`**: eliminação direta com detecção de pivôs nulos.
- **`gauss_com_pivo_parcial`**: troca de linhas baseada no maior valor absoluto da coluna pivô.
- **`gauss_com_pivo_completo`**: troca de linhas e colunas; mantém vetor de permutação.
- **`fatoracao_LU`**: decomposição Doolittle (L unitária) com solução via `Ly=b`, `Ux=y`.
- **`cholesky`**: valida simetria/definição positiva, constrói `L` e resolve `LLᵀx=b`.
- Funções utilitárias `_copiar_matriz`, `_copiar_vetor` e `determinante` são usadas para evitar mutações indesejadas e fazer verificações prévias.

Cada rotina trata:
- Matrizes singulares (pivô menor que `EPSILON = 1e-12`).
- Sistemas incompatíveis ou com infinitas soluções.
- Normalização de resultados próximos de zero para diminuir ruído numérico.

## Estrutura do projeto
```
.
├── app.py               # ponto de entrada da GUI
├── view.py              # telas Tkinter, validações e ligação com os métodos numéricos
├── sistemas.py          # algoritmos de álgebra linear numérica
├── Calculadora0Func.cpp # código-fonte do executável legado (não é construído automaticamente)
├── Calculadora0Func.exe # binário utilizado pelo módulo de zeros de função
├── entrada.txt          # arquivo de entrada temporário para o executável externo
└── saida.txt            # arquivo de saída temporário para o executável externo
```

## Dicas e possíveis melhorias
- Integrar diretamente os métodos iterativos (Jacobi/Seidel) para que o menu deixe de ser apenas ilustrativo.
- Escrever testes unitários para `sistemas.py` cobrindo casos degenerados.
- Adicionar validação simbólica das funções `f(x)`/`g(x)` para reduzir erros de digitação antes de chamar o executável em C++.
- Permitir salvar e carregar sistemas ou funções em arquivos JSON para repetir experimentos rapidamente.

## Licença
Não há uma licença explícita neste repositório; adicione uma (por exemplo, MIT) se desejar compartilhar o projeto publicamente.
