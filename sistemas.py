from __future__ import annotations

from math import sqrt

EPSILON = 1e-12 #pra transformar numeros muito pertos de 0 em 0

#funções de copiar matriz e vetor para não causar conflitos
def _copiar_matriz(matriz: list[list[float]]) -> list[list[float]]:
    return [linha[:] for linha in matriz]


def _copiar_vetor(vetor: list[float]) -> list[float]:
    return vetor[:]

#calcula o determinante (usado em LU e Cholesky)
def determinante(matriz: list[list[float]], ordem: int) -> float:
    matriz_trabalho = _copiar_matriz(matriz)
    sinal = 1 #sinal deve ser trocado quando uma linha for trocada

    #faz uma eliminação de gauss para que a matriz fique triangular superior
    for coluna_pivo in range(ordem - 1):
        linha_max = max(range(coluna_pivo, ordem), key=lambda linha: abs(matriz_trabalho[linha][coluna_pivo]))
        if abs(matriz_trabalho[linha_max][coluna_pivo]) < EPSILON:
            return 0.0 #caso onde uma coluna inteira é apenas 0

        if linha_max != coluna_pivo:
            matriz_trabalho[coluna_pivo], matriz_trabalho[linha_max] = (
                matriz_trabalho[linha_max],
                matriz_trabalho[coluna_pivo],
            )
            sinal *= -1 #precisou trocar as linhas 

        pivo = matriz_trabalho[coluna_pivo][coluna_pivo]
        for linha in range(coluna_pivo + 1, ordem):
            fator = matriz_trabalho[linha][coluna_pivo] / pivo
            matriz_trabalho[linha][coluna_pivo] = 0.0
            for coluna in range(coluna_pivo + 1, ordem):
                matriz_trabalho[linha][coluna] -= fator * matriz_trabalho[coluna_pivo][coluna]

    resultado = float(sinal)
    for i in range(ordem):
        resultado *= matriz_trabalho[i][i] #multiplica a diagonal principal para achar o det

    return 0.0 if abs(resultado) < EPSILON else resultado

#calcula o metodo de eliminação de gauss sem pivoteamento
def gauss_sem_pivo(matriz_a: list[list[float]], vetor_b: list[float]) -> list[float]:
    matriz = _copiar_matriz(matriz_a)
    vetor = _copiar_vetor(vetor_b)
    ordem = len(vetor)

    for coluna_pivo in range(ordem - 1):
        pivo = matriz[coluna_pivo][coluna_pivo]
        if abs(pivo) < EPSILON: #pivo é nulo
            existe_candidato = any(abs(matriz[linha][coluna_pivo]) > EPSILON for linha in range(coluna_pivo + 1, ordem))
            #tem como trocar o pivô
            if existe_candidato: 
                raise ValueError(
                    f"Pivô nulo na linha {coluna_pivo + 1}. Utilize um método com pivoteamento."
                )
            #nesse caso não tem nem como trocar o pivô
            raise ValueError("Matriz singular detectada: pivô nulo sem candidatos para troca.")
        
        #calculo para deixar a matriz triangular superior
        for linha in range(coluna_pivo + 1, ordem):
            fator = matriz[linha][coluna_pivo] / pivo
            matriz[linha][coluna_pivo] = 0.0
            for coluna in range(coluna_pivo + 1, ordem):
                matriz[linha][coluna] -= fator * matriz[coluna_pivo][coluna]
            vetor[linha] -= fator * vetor[coluna_pivo]

    solucoes = [0.0] * ordem
    #percorre a matriz de trás para frente fazendo a retrosubstituição
    for i in range(ordem - 1, -1, -1):
        pivo = matriz[i][i]
        #soma todos os elementos da linha multiplicados pela solução (a partir do x calculado da vez)
        soma = sum(matriz[i][j] * solucoes[j] for j in range(i + 1, ordem))
        numerador = vetor[i] - soma
        if abs(pivo) < EPSILON:
            if abs(numerador) > EPSILON:
                raise ValueError("Sistema incompatível: linha sem pivô com termo independente não nulo.")
            raise ValueError("Sistema possui infinitas soluções (matriz singular).")

        solucoes[i] = numerador / pivo
        if abs(solucoes[i]) < EPSILON:
            solucoes[i] = 0.0

    return solucoes

#calcula com o metodo de eliminação de gauss com pivoteamento parcial
def gauss_com_pivo_parcial(matriz_a: list[list[float]], vetor_b: list[float]) -> list[float]:
    matriz = _copiar_matriz(matriz_a)
    vetor = _copiar_vetor(vetor_b)
    ordem = len(vetor)

    for coluna_pivo in range(ordem - 1):
        #acha o maior valor em modulo da coluna da vez
        linha_max = max(range(coluna_pivo, ordem), key=lambda linha: abs(matriz[linha][coluna_pivo]))
        #caso seja diferente da que já estava, realiza a troca
        if linha_max != coluna_pivo:
            matriz[coluna_pivo], matriz[linha_max] = matriz[linha_max], matriz[coluna_pivo]
            vetor[coluna_pivo], vetor[linha_max] = vetor[linha_max], vetor[coluna_pivo]
        #a partir daqui segue a mesma lógica do método sem pivoteamento
        pivo = matriz[coluna_pivo][coluna_pivo]
        if abs(pivo) < EPSILON:
            raise ValueError("Matriz singular detectada mesmo com pivoteamento parcial.")

        for linha in range(coluna_pivo + 1, ordem):
            fator = matriz[linha][coluna_pivo] / pivo
            matriz[linha][coluna_pivo] = 0.0
            for coluna in range(coluna_pivo + 1, ordem):
                matriz[linha][coluna] -= fator * matriz[coluna_pivo][coluna]
            vetor[linha] -= fator * vetor[coluna_pivo]

    solucoes = [0.0] * ordem
    for i in range(ordem - 1, -1, -1):
        pivo = matriz[i][i]
        soma = sum(matriz[i][j] * solucoes[j] for j in range(i + 1, ordem))
        numerador = vetor[i] - soma
        if abs(pivo) < EPSILON:
            if abs(numerador) > EPSILON:
                raise ValueError("Sistema incompatível: linha sem pivô com termo independente não nulo.")
            raise ValueError("Sistema possui infinitas soluções (matriz singular).")

        solucoes[i] = numerador / pivo
        if abs(solucoes[i]) < EPSILON:
            solucoes[i] = 0.0

    return solucoes

#calcula com o metodo de eliminação de gauss com pivoteamento completo
def gauss_com_pivo_completo(matriz_a: list[list[float]], vetor_b: list[float]) -> list[float]:
    matriz = _copiar_matriz(matriz_a)
    vetor = _copiar_vetor(vetor_b)
    ordem = len(vetor)
    permutacao_colunas = list(range(ordem)) #lista para armazenar a permutação das colunas caso seja necessario

    for coluna_pivo in range(ordem - 1):
        valor_maximo = 0.0
        linha_max = coluna_pivo
        coluna_max = coluna_pivo

        for linha in range(coluna_pivo, ordem):
            for coluna in range(coluna_pivo, ordem):
                valor_atual = abs(matriz[linha][coluna])
                if valor_atual > valor_maximo:
                    valor_maximo = valor_atual
                    linha_max = linha
                    coluna_max = coluna

        if linha_max != coluna_pivo:
            matriz[coluna_pivo], matriz[linha_max] = matriz[linha_max], matriz[coluna_pivo]
            vetor[coluna_pivo], vetor[linha_max] = vetor[linha_max], vetor[coluna_pivo]

        if coluna_max != coluna_pivo:
            for linha in range(ordem):
                matriz[linha][coluna_pivo], matriz[linha][coluna_max] = (
                    matriz[linha][coluna_max],
                    matriz[linha][coluna_pivo],
                )
            permutacao_colunas[coluna_pivo], permutacao_colunas[coluna_max] = (
                permutacao_colunas[coluna_max],
                permutacao_colunas[coluna_pivo],
            )

        if valor_maximo < EPSILON:
            raise ValueError("Matriz singular detectada mesmo com pivoteamento completo.")

        pivo = matriz[coluna_pivo][coluna_pivo]
        if abs(pivo) < EPSILON:
            raise ValueError("Matriz singular detectada mesmo com pivoteamento completo.")

        for linha in range(coluna_pivo + 1, ordem):
            fator = matriz[linha][coluna_pivo] / pivo
            matriz[linha][coluna_pivo] = 0.0
            for coluna in range(coluna_pivo + 1, ordem):
                matriz[linha][coluna] -= fator * matriz[coluna_pivo][coluna]
            vetor[linha] -= fator * vetor[coluna_pivo]

    solucoes_desordenadas = [0.0] * ordem
    for i in range(ordem - 1, -1, -1):
        pivo = matriz[i][i]
        soma = sum(matriz[i][j] * solucoes_desordenadas[j] for j in range(i + 1, ordem))
        numerador = vetor[i] - soma
        if abs(pivo) < EPSILON:
            if abs(numerador) > EPSILON:
                raise ValueError("Sistema incompatível: linha sem pivô com termo independente não nulo.")
            raise ValueError("Sistema possui infinitas soluções (matriz singular).")

        solucoes_desordenadas[i] = numerador / pivo
        if abs(solucoes_desordenadas[i]) < EPSILON:
            solucoes_desordenadas[i] = 0.0

    solucoes = [0.0] * ordem
    for indice_atual, indice_original in enumerate(permutacao_colunas):
        solucoes[indice_original] = solucoes_desordenadas[indice_atual]

    return solucoes


def fatoracao_LU(matriz_a: list[list[float]], vetor_b: list[float]) -> list[float]:
    matriz = _copiar_matriz(matriz_a)
    vetor = _copiar_vetor(vetor_b)
    ordem = len(vetor)

    if determinante(matriz, ordem) == 0.0:
        raise ValueError("O determinante da matriz A é 0, portanto não se pode aplicar fatoração LU.")

    L = [[0.0] * ordem for _ in range(ordem)]
    U = _copiar_matriz(matriz)
    for i in range(ordem):
        L[i][i] = 1.0

    for k in range(ordem):
        pivo = U[k][k]
        if abs(pivo) < EPSILON:
            raise ValueError("Fatoração LU falhou: pivô nulo encontrado.")
        for i in range(k + 1, ordem):
            fator = U[i][k] / pivo
            L[i][k] = fator
            U[i][k] = 0.0
            for j in range(k + 1, ordem):
                U[i][j] -= fator * U[k][j]

    y = [0.0] * ordem
    for i in range(ordem):
        soma = sum(L[i][j] * y[j] for j in range(i))
        pivo = L[i][i]
        if abs(pivo) < EPSILON:
            raise ValueError("Fatoração LU falhou: elemento da diagonal de L é nulo.")
        y[i] = (vetor[i] - soma) / pivo

    solucoes = [0.0] * ordem
    for i in range(ordem - 1, -1, -1):
        soma = sum(U[i][j] * solucoes[j] for j in range(i + 1, ordem))
        pivo = U[i][i]
        if abs(pivo) < EPSILON:
            raise ValueError("Fatoração LU falhou: elemento da diagonal de U é nulo.")
        valor = (y[i] - soma) / pivo
        solucoes[i] = 0.0 if abs(valor) < EPSILON else valor

    return solucoes

def cholesky(matriz_a: list[list[float]], vetor_b: list[float]) -> list[float]:
    matriz = _copiar_matriz(matriz_a)
    vetor = _copiar_vetor(vetor_b)
    ordem = len(vetor)

    for i in range(ordem):
        for j in range(i + 1, ordem):
            if abs(matriz[i][j] - matriz[j][i]) > EPSILON:
                raise ValueError("Não se pode fazer Cholesky porque A não é simétrica.")

    for k in range(1, ordem + 1):
        matriz_aux = [[matriz[l][c] for c in range(k)] for l in range(k)]
        if determinante(matriz_aux, k) <= 0.0:
            raise ValueError("Não se pode fazer Cholesky porque A não é definida positiva")
    
    G = [[0.0] * ordem for _ in range(ordem)]
    for i in range(ordem):
        for j in range(i + 1):
            soma = sum(G[i][k] * G[j][k] for k in range(j))
            if i == j:
                valor = matriz[i][i] - soma
                if valor <= 0.0:
                    raise ValueError("Não se pode fazer Cholesky porque A não é definida positiva.")
                G[i][i] = sqrt(valor)
            else:
                denominador = G[j][j]
                if abs(denominador) < EPSILON:
                    raise ValueError("Decomposição de Cholesky falhou: elemento diagonal nulo.")
                G[i][j] = (matriz[i][j] - soma) / denominador

    y = [0.0] * ordem
    for i in range(ordem):
        soma = sum(G[i][j] * y[j] for j in range(i))
        denominador = G[i][i]
        if abs(denominador) < EPSILON:
            raise ValueError("Triangulação inferior inválida: elemento diagonal nulo.")
        y[i] = (vetor[i] - soma) / denominador

    solucoes = [0.0] * ordem
    for i in range(ordem - 1, -1, -1):
        soma = sum(G[k][i] * solucoes[k] for k in range(i + 1, ordem))
        denominador = G[i][i]
        if abs(denominador) < EPSILON:
            raise ValueError("Triangulação superior inválida: elemento diagonal nulo.")
        valor = (y[i] - soma) / denominador
        solucoes[i] = 0.0 if abs(valor) < EPSILON else valor

    return solucoes
