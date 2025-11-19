from __future__ import annotations

import subprocess
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from typing import Callable

from sistemas import (
    cholesky,
    fatoracao_LU,
    gauss_com_pivo_completo,
    gauss_com_pivo_parcial,
    gauss_jacobi,
    gauss_seidel,
    gauss_sem_pivo,
)

ZERO_FUNC_FIELDS = [
    ("f(x):", "fx"),
    ("a:", "a"),
    ("b:", "b"),
    ("precisão:", "precisao"),
    ("iterações:", "iteracoes"),
    ("g(x):", "gx"),
]

METODOS_SISTEMA: dict[str, Callable[[list[list[float]], list[float]], list[float]]] = {
    "Eliminação de Gauss (Gauss sem pivoteamento)": gauss_sem_pivo,
    "Pivoteamento parcial (Gauss com pivoteamento parcial)": gauss_com_pivo_parcial,
    "Pivoteamento completo (Gauss com pivoteamento completo)": gauss_com_pivo_completo,
    "Fatoração LU": fatoracao_LU,
    "Fatoração de Cholesky": cholesky
}

METODOS_ITERATIVOS_FUNCOES = {
    "Método iterativo de Gauss Jacobi": gauss_jacobi,
    "Método iterativo de Gauss Seidel": gauss_seidel,
}
METODOS_ITERATIVOS = tuple(METODOS_ITERATIVOS_FUNCOES)

METODOS_DISPONIVEIS = list(METODOS_SISTEMA) + list(METODOS_ITERATIVOS_FUNCOES)

CONDICOES_PARADA = [
    ("Erro absoluto", "erro_absoluto"),
    ("Erro relativo", "erro_relativo"),
]
CONDICOES_PARADA_VALORES = {valor for _, valor in CONDICOES_PARADA}


@dataclass
class CamposIterativos:
    tolerancia: tk.Entry
    iteracoes: tk.Entry
    condicao_parada: tk.StringVar


def limpar_container(container: tk.Misc) -> None:
    for widget in container.winfo_children():
        widget.destroy()


def executar_zero_func(container: tk.Misc, entradas: dict[str, tk.Entry]) -> None:
    valores = [entradas[key].get().strip() for _, key in ZERO_FUNC_FIELDS]

    try:
        with open("entrada.txt", "w", encoding="utf-8") as entrada:
            entrada.write("\n".join(valores) + "\n")
    except OSError as exc:
        messagebox.showerror("Erro", f"Falha ao escrever entrada.txt:\n{exc}")
        return

    try:
        subprocess.run(["./Calculadora0Func.exe"], check=True)
    except subprocess.CalledProcessError as exc:
        messagebox.showerror("Erro", f"Falha ao executar Calculadora0Func.exe (código {exc.returncode}).")
        return

    try:
        with open("saida.txt", "r", encoding="utf-8") as saida:
            linhas = [linha.strip() for linha in saida if linha.strip()]
    except OSError as exc:
        messagebox.showerror("Erro", f"Falha ao ler saida.txt:\n{exc}")
        return

    resultados = [
        f"Bissecao: {linhas[0] if len(linhas) > 0 else '(sem resultado)'}",
        f"MIL: {linhas[1] if len(linhas) > 1 else '(sem resultado)'}",
        f"Newton: {linhas[2] if len(linhas) > 2 else '(sem resultado)'}",
        f"Secante: {linhas[3] if len(linhas) > 3 else '(sem resultado)'}",
        f"Regula Falsi: {linhas[4] if len(linhas) > 4 else '(sem resultado)'}",
    ]

    messagebox.showinfo("Raízes encontradas", "\n".join(resultados))
    show_tela_inicial(container)


def show_tela_inicial(container: tk.Misc) -> None:
    limpar_container(container)

    tk.Label(container, text="Escolha uma opção:", font=("Arial", 14, "bold")).pack(pady=(30, 20))
    tk.Button(
        container,
        text="zero de funções",
        width=20,
        height=2,
        command=lambda: show_tela_zero_func(container),
    ).pack(pady=5)
    tk.Button(
        container,
        text="Sistemas lineares",
        width=20,
        height=2,
        command=lambda: show_tela_ordem(container),
    ).pack(pady=5)


def show_tela_zero_func(container: tk.Misc) -> None:
    limpar_container(container)

    form = tk.Frame(container)
    form.pack(fill="both", expand=True)

    tk.Label(form, text="Insira os dados", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))

    entradas: dict[str, tk.Entry] = {}
    for idx, (label_text, key) in enumerate(ZERO_FUNC_FIELDS, start=1):
        tk.Label(form, text=label_text, anchor="w").grid(row=idx, column=0, sticky="w", padx=40, pady=5)
        entry = tk.Entry(form, width=24)
        entry.grid(row=idx, column=1, padx=(0, 40), pady=5)
        entradas[key] = entry

    tk.Button(form, text="Calcular", command=lambda: executar_zero_func(container, entradas)).grid(
        row=len(ZERO_FUNC_FIELDS) + 1,
        column=0,
        columnspan=2,
        pady=(10, 0),
    )
    tk.Button(form, text="Voltar", command=lambda: show_tela_inicial(container)).grid(
        row=len(ZERO_FUNC_FIELDS) + 2,
        column=0,
        columnspan=2,
        pady=(10, 15),
    )


def show_tela_ordem(container: tk.Misc) -> None:
    limpar_container(container)

    tk.Label(container, text="Qual é a ordem do sistema linear?", font=("Arial", 14, "bold")).pack(pady=(20, 10))
    ordem_var = tk.StringVar()
    entry_ordem = tk.Entry(container, width=10, justify="center", textvariable=ordem_var)
    entry_ordem.pack(pady=10)
    entry_ordem.focus_set()

    tk.Label(container, text="Qual método você quer usar?", font=("Arial", 14, "bold")).pack(pady=(20, 10))
    sistema_var = tk.StringVar(value=METODOS_DISPONIVEIS[0])
    tk.OptionMenu(container, sistema_var, *METODOS_DISPONIVEIS).pack(padx=10, pady=15)

    def avancar() -> None:
        try:
            ordem = int(ordem_var.get())
            if ordem <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe um número inteiro positivo para a ordem.")
            return

        show_tela_sistema(container, ordem, sistema_var.get())

    tk.Button(container, text="Avançar", command=avancar).pack(pady=5)
    tk.Button(container, text="Voltar", command=lambda: show_tela_inicial(container)).pack(pady=20)


def show_tela_sistema(container: tk.Misc, ordem: int, metodo: str) -> None:
    limpar_container(container)

    tk.Label(
        container,
        text=f"Preencha a matriz A ({ordem}x{ordem}) e o vetor b ({ordem}x1)",
        font=("Arial", 14, "bold"),
    ).pack(pady=(20, 10))
    tk.Label(container, text=f"Método selecionado: {metodo}", font=("Arial", 11)).pack(pady=(0, 10))

    matriz_container = tk.Frame(container)
    matriz_container.pack(pady=10)

    frame_a = tk.LabelFrame(matriz_container, text="Matriz A")
    frame_a.grid(row=0, column=0, padx=(0, 20))

    entradas_a: list[list[tk.Entry]] = []
    for i in range(ordem):
        linha: list[tk.Entry] = []
        for j in range(ordem):
            entry = tk.Entry(frame_a, width=6, justify="center")
            entry.grid(row=i, column=j, padx=5, pady=5)
            linha.append(entry)
        entradas_a.append(linha)

    frame_b = tk.LabelFrame(matriz_container, text="Vetor b")
    frame_b.grid(row=0, column=1)

    entradas_b: list[tk.Entry] = []
    for i in range(ordem):
        entry = tk.Entry(frame_b, width=6, justify="center")
        entry.grid(row=i, column=0, padx=5, pady=5)
        entradas_b.append(entry)

    campos_iterativos: CamposIterativos | None = None
    if metodo in METODOS_ITERATIVOS:
        iterativo_frame = tk.LabelFrame(container, text="Parâmetros do método iterativo")
        iterativo_frame.pack(fill="x", padx=30, pady=(5, 0))

        tk.Label(iterativo_frame, text="Tolerância:", anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        entrada_tolerancia = tk.Entry(iterativo_frame, width=12, justify="center")
        entrada_tolerancia.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(iterativo_frame, text="Número máximo de iterações:", anchor="w").grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=5,
        )
        entrada_iteracoes = tk.Entry(iterativo_frame, width=12, justify="center")
        entrada_iteracoes.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        condicao_var = tk.StringVar(value=CONDICOES_PARADA[0][1])
        tk.Label(iterativo_frame, text="Condição de parada:", anchor="w").grid(
            row=2,
            column=0,
            sticky="w",
            padx=10,
            pady=5,
        )
        for idx, (titulo, valor) in enumerate(CONDICOES_PARADA):
            tk.Radiobutton(
                iterativo_frame,
                text=titulo,
                variable=condicao_var,
                value=valor,
            ).grid(row=2, column=1 + idx, sticky="w", padx=5, pady=5)

        campos_iterativos = CamposIterativos(
            tolerancia=entrada_tolerancia,
            iteracoes=entrada_iteracoes,
            condicao_parada=condicao_var,
        )

    botoes_frame = tk.Frame(container)
    botoes_frame.pack(pady=10)

    tk.Button(
        botoes_frame,
        text="Calcular",
        command=lambda: calcula_sistema(container, entradas_a, entradas_b, metodo, campos_iterativos),
    ).pack(pady=(0, 10))
    tk.Button(
        botoes_frame,
        text="Voltar",
        command=lambda: show_tela_ordem(container),
    ).pack()


def _extrair_dados_sistema(
    entradas_a: list[list[tk.Entry]],
    entradas_b: list[tk.Entry],
) -> tuple[list[list[float]], list[float]]:
    matriz: list[list[float]] = []
    for i, linha in enumerate(entradas_a):
        linha_valores: list[float] = []
        for j, campo in enumerate(linha):
            valor_bruto = campo.get().strip()
            if not valor_bruto:
                raise ValueError(f"Informe todos os valores da matriz A (faltando o elemento A[{i + 1},{j + 1}]).")
            try:
                linha_valores.append(float(valor_bruto))
            except ValueError as exc:
                raise ValueError(f"Valor inválido na matriz A[{i + 1},{j + 1}]: {valor_bruto!r}") from exc
        matriz.append(linha_valores)

    vetor: list[float] = []
    for i, campo in enumerate(entradas_b):
        valor_bruto = campo.get().strip()
        if not valor_bruto:
            raise ValueError(f"Informe todos os valores do vetor b (faltando o elemento b[{i + 1}]).")
        try:
            vetor.append(float(valor_bruto))
        except ValueError as exc:
            raise ValueError(f"Valor inválido no vetor b[{i + 1}]: {valor_bruto!r}") from exc

    return matriz, vetor


def _extrair_parametros_iterativos(campos: CamposIterativos) -> tuple[float, int, str]:
    tolerancia_bruta = campos.tolerancia.get().strip()
    if not tolerancia_bruta:
        raise ValueError("Informe a tolerância para o método iterativo.")
    try:
        tolerancia = float(tolerancia_bruta)
    except ValueError as exc:
        raise ValueError("Tolerância inválida: utilize um número real.") from exc
    if tolerancia <= 0:
        raise ValueError("A tolerância deve ser maior que zero.")

    iteracoes_brutas = campos.iteracoes.get().strip()
    if not iteracoes_brutas:
        raise ValueError("Informe o número máximo de iterações.")
    try:
        iteracoes = int(iteracoes_brutas)
    except ValueError as exc:
        raise ValueError("Número máximo de iterações inválido: utilize um inteiro.") from exc
    if iteracoes <= 0:
        raise ValueError("O número máximo de iterações deve ser maior que zero.")

    condicao_escolhida = campos.condicao_parada.get()
    if condicao_escolhida not in CONDICOES_PARADA_VALORES:
        raise ValueError("Selecione uma condição de parada.")

    return tolerancia, iteracoes, condicao_escolhida


def calcula_sistema(
    container: tk.Misc,
    entradas_a: list[list[tk.Entry]],
    entradas_b: list[tk.Entry],
    metodo: str,
    campos_iterativos: CamposIterativos | None = None,
) -> None:
    funcao_iterativa = METODOS_ITERATIVOS_FUNCOES.get(metodo)
    funcao_direta = METODOS_SISTEMA.get(metodo)

    parametros_iterativos: tuple[float, int, str] | None = None
    if funcao_iterativa is not None:
        if campos_iterativos is None:
            messagebox.showerror("Erro", "Preencha os parâmetros do método iterativo.")
            return
        try:
            parametros_iterativos = _extrair_parametros_iterativos(campos_iterativos)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return
    elif funcao_direta is None:
        messagebox.showinfo("Aviso", f"O método \"{metodo}\" ainda não está disponível.")
        return

    try:
        matriz_a, vetor_b = _extrair_dados_sistema(entradas_a, entradas_b)
    except ValueError as exc:
        messagebox.showerror("Erro", str(exc))
        return

    inicio = time.perf_counter()
    resultado: list[float] | None = None
    iteracoes_realizadas: int | None = None

    try:
        if funcao_iterativa is not None and parametros_iterativos is not None:
            tolerancia, iteracoes, condicao_parada = parametros_iterativos
            resultado, iteracoes_realizadas = funcao_iterativa(
                matriz_a,
                vetor_b,
                tolerancia,
                iteracoes,
                condicao_parada,
            )
        elif funcao_direta is not None:
            resultado = funcao_direta(matriz_a, vetor_b)
        else:
            raise NotImplementedError(f"O método \"{metodo}\" ainda não está disponível.")
    except NotImplementedError as exc:
        messagebox.showinfo("Aviso", str(exc))
        return
    except ValueError as exc:
        messagebox.showerror("Erro", str(exc))
        return
    except ZeroDivisionError:
        messagebox.showerror("Erro", "Divisão por zero detectada durante o cálculo.")
        return
    duracao = time.perf_counter() - inicio

    linhas_resultado = [f"x{i + 1} = {valor:.6g}" for i, valor in enumerate(resultado)]
    if iteracoes_realizadas is not None:
        linhas_resultado.append(f"Iterações: {iteracoes_realizadas}")
    linhas_resultado.append(f"Tempo: {duracao * 1000:.3f} ms")
    messagebox.showinfo("Resultado", "\n".join(linhas_resultado))
    show_tela_inicial(container)


def iniciar_app() -> None:
    root = tk.Tk()
    root.title("Trabalho 2 CN")
    root.geometry("700x600")
    root.resizable(False, False)

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    show_tela_inicial(container)
    root.mainloop()
