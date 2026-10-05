#Lucas Dos Santos Oliveira rm:571718
#Diego Caio de Ulhôa Augusto rm:572190

"""FeedSmart - Sistema de Gestão de Feedbacks de Usuários (CP5)."""

import json
import os
from datetime import datetime

TIPOS = ("estudante", "gerente", "final", "administrador")
CATEGORIAS = (("Detrator", 0, 6), ("Neutro", 7, 8), ("Promotor", 9, 10))
LIMITE_MEDIA_BAIXA = 6      # produto abaixo disso precisa de melhorias
LIMITE_ENGAJADO = 5         # usuário acima disso é engajado
ARQ_JSON, ARQ_USU, ARQ_FEED = "dados.json", "usuarios.txt", "feedbacks.txt"


def titulo(txt):
    """Exibe um título com moldura."""
    print(f"\n{'=' * 45}\n  {txt}\n{'=' * 45}")


def ler_texto(prompt, minimo=2):
    """Lê texto com tamanho mínimo, repetindo até ser válido.

    Args:
        prompt (str): mensagem exibida ao usuário no input().
        minimo (int): quantidade mínima de caracteres.
    Returns:
        str: texto validado.
    """
    while True:
        valor = input(prompt).strip()
        if len(valor) >= minimo:
            return valor
        print(f"[ERRO] Digite ao menos {minimo} caracteres.")


def ler_inteiro(prompt, minimo, maximo):
    """Lê um inteiro entre minimo e maximo, repetindo até ser válido.

    Args:
        prompt (str): mensagem exibida ao usuário no input().
        minimo (int): menor valor aceito.
        maximo (int): maior valor aceito.
    Returns:
        int: número validado.
    """
    while True:
        try:
            valor = int(input(prompt))
            if minimo <= valor <= maximo:
                return valor
            print(f"[ERRO] Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print("[ERRO] Entrada inválida: digite um número inteiro.")


def ler_data(prompt):
    """Lê data DD/MM/AAAA (Enter = hoje) e retorna como texto.

    Args:
        prompt (str): mensagem exibida ao usuário no input().
    Returns:
        str: data no formato DD/MM/AAAA.
    """
    while True:
        valor = input(prompt).strip()
        if not valor:
            return datetime.now().strftime("%d/%m/%Y")
        try:
            return datetime.strptime(valor, "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError:
            print("[ERRO] Data inválida. Use DD/MM/AAAA.")


def novo_id(lista):
    """Retorna o próximo ID disponível de uma lista de dicionários."""
    return max((x["id"] for x in lista), default=0) + 1


def cadastrar_usuario(usuarios):
    """Cadastra usuário (nome, idade, profissão, tipo) na lista."""
    titulo("CADASTRAR USUÁRIO")
    nome = ler_texto("Nome: ")
    idade = ler_inteiro("Idade: ", 1, 120)
    profissao = ler_texto("Profissão: ")
    for i, t in enumerate(TIPOS, 1):
        print(f"  {i}) {t}")
    tipo = TIPOS[ler_inteiro("Tipo de usuário: ", 1, len(TIPOS)) - 1]
    usuarios.append({"id": novo_id(usuarios), "nome": nome, "idade": idade,
                     "profissao": profissao, "tipo": tipo})
    print(f"[OK] Usuário #{usuarios[-1]['id']} cadastrado!")


def listar_usuarios(usuarios):
    """Lista os usuários em formato de tabela."""
    titulo("USUÁRIOS")
    if not usuarios:
        print("Nenhum usuário cadastrado.")
    for u in usuarios:
        print(f"{u['id']:<4}{u['nome']:<20}{u['idade']:<5}{u['profissao']:<18}{u['tipo']}")


def registrar_feedback(usuarios, feedbacks):
    """Registra feedback (produto, texto, nota 0-10, data) de um usuário existente."""
    titulo("REGISTRAR FEEDBACK")
    if not usuarios:
        print("[ERRO] Cadastre um usuário primeiro.")
        return
    listar_usuarios(usuarios)
    uid = ler_inteiro("\nID do usuário: ", 1, 10**6)
    usuario = None
    for u in usuarios:
        if u["id"] == uid:
            usuario = u
    if usuario is None:
        print("[ERRO] Usuário não encontrado.")
        return
    feedbacks.append({"id": novo_id(feedbacks), "usuario_id": uid,
                      "produto": ler_texto("Produto: "), "texto": ler_texto("Comentário: ", 3),
                      "nota": ler_inteiro("Nota (0 a 10): ", 0, 10),
                      "data": ler_data("Data DD/MM/AAAA (Enter = hoje): ")})
    print(f"[OK] Obrigado, {usuario['nome']}! Feedback registrado.")


def media(notas):
    """Calcula a média de uma lista de notas (0 se vazia)."""
    if len(notas) == 0:
        return 0.0
    return sum(notas) / len(notas)


def categoria(nota):
    """Retorna a categoria (Detrator/Neutro/Promotor) da nota."""
    for nome, minimo, maximo in CATEGORIAS:
        if minimo <= nota <= maximo:
            return nome
    return "?"


def agrupar_por_produto(feedbacks):
    """Retorna dicionário {produto: [feedbacks]}."""
    grupos = {}
    for f in feedbacks:
        chave = f["produto"].lower()
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(f)
    return grupos


def notas_de(lista):
    """Retorna só as notas de uma lista de feedbacks."""
    notas = []
    for f in lista:
        notas.append(f["nota"])
    return notas


def gerar_relatorio(feedbacks):
    """Exibe total, média geral, feedbacks por produto e contagem por categoria."""
    titulo("RELATÓRIO")
    if not feedbacks:
        print("Sem feedbacks para analisar.")
        return
    print(f"Total: {len(feedbacks)} | Média geral: {media(notas_de(feedbacks)):.2f}")
    grupos = agrupar_por_produto(feedbacks)
    for prod in grupos:
        itens = grupos[prod]
        print(f"\n{prod.title()} - {len(itens)} feedback(s), média {media(notas_de(itens)):.2f}")
        for i in itens:
            print(f"   [{i['nota']:>2}] {i['data']} - {i['texto']}")
    print("\nPor categoria:")
    for nome, minimo, maximo in CATEGORIAS:
        qtd = 0
        for f in feedbacks:
            if categoria(f["nota"]) == nome:
                qtd += 1
        print(f"  {nome:<9}: {qtd}")


def analise_avancada(usuarios, feedbacks):
    """Exibe ranking de produtos, NPS, média por tipo de usuário e matriz produto x nota."""
    titulo("ANÁLISE AVANÇADA")
    if not feedbacks:
        print("Sem feedbacks para analisar.")
        return
    grupos = agrupar_por_produto(feedbacks)
    ranking = []
    matriz = []
    for prod in grupos:
        ranking.append((media(notas_de(grupos[prod])), prod))
    ranking.sort(reverse=True)
    print("Ranking de produtos:")
    for pos, (m, prod) in enumerate(ranking, 1):
        print(f"  {pos}o {prod.title():<20}{m:.2f}")
        linha = [0] * 11
        for f in grupos[prod]:
            linha[f["nota"]] += 1
        matriz.append(linha)
    promotores = detratores = 0
    for f in feedbacks:
        if categoria(f["nota"]) == "Promotor":
            promotores += 1
        elif categoria(f["nota"]) == "Detrator":
            detratores += 1
    print(f"\nNPS: {(promotores - detratores) / len(feedbacks) * 100:.0f}")
    print("\nMédia por tipo de usuário:")
    for tipo in TIPOS:
        notas = []
        for f in feedbacks:
            for u in usuarios:
                if u["id"] == f["usuario_id"] and u["tipo"] == tipo:
                    notas.append(f["nota"])
        if notas:
            print(f"  {tipo:<14}{media(notas):.2f} ({len(notas)})")
    print("\nMatriz produto x nota (0..10):")
    print(" " * 16 + " ".join(f"{n:>2}" for n in range(11)))
    for i in range(len(ranking)):
        print(f"{ranking[i][1][:15]:<16}" + " ".join(f"{c:>2}" for c in matriz[i]))


def gerar_insights(usuarios, feedbacks):
    """DESAFIO EXTRA: analisa os feedbacks e gera insights automáticos.

    Regras:
      - produto com média abaixo de 6 -> precisa de melhorias;
      - produto com média 9 ou mais -> destaque positivo;
      - usuário com mais de 5 feedbacks -> perfil engajado;
      - usuário cadastrado sem feedbacks -> oportunidade de engajamento;
      - mais de 30% de detratores -> alerta geral.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.
    """
    titulo("INSIGHTS AUTOMÁTICOS")
    if not feedbacks:
        print("Sem feedbacks para gerar insights.")
        return
    insights = []
    grupos = agrupar_por_produto(feedbacks)
    for prod in grupos:
        m = media(notas_de(grupos[prod]))
        if m < LIMITE_MEDIA_BAIXA:
            insights.append(f"[ATENÇÃO] Produto {prod.title()} tem média {m:.1f} (abaixo de {LIMITE_MEDIA_BAIXA}) - precisa de melhorias.")
        elif m >= 9:
            insights.append(f"[DESTAQUE] Produto {prod.title()} tem média {m:.1f} - excelente aceitação.")
    for u in usuarios:
        qtd = 0
        for f in feedbacks:
            if f["usuario_id"] == u["id"]:
                qtd += 1
        if qtd > LIMITE_ENGAJADO:
            insights.append(f"[ENGAJAMENTO] Usuário {u['nome']} enviou {qtd} feedbacks - perfil engajado.")
        elif qtd == 0:
            insights.append(f"[OPORTUNIDADE] Usuário {u['nome']} ainda não enviou feedbacks.")
    detratores = 0
    for f in feedbacks:
        if categoria(f["nota"]) == "Detrator":
            detratores += 1
    percentual = detratores / len(feedbacks) * 100
    if percentual > 30:
        insights.append(f"[ALERTA] {percentual:.0f}% dos feedbacks são de detratores (nota até 6).")
    if not insights:
        print("Nenhum ponto de atenção encontrado. Tudo certo!")
    for i, texto in enumerate(insights, 1):
        print(f"{i}. {texto}")


def salvar_dados(usuarios, feedbacks):
    """Salva os dados em JSON e em TXT (campos separados por ';')."""
    try:
        with open(ARQ_JSON, "w", encoding="utf-8") as f:
            json.dump({"usuarios": usuarios, "feedbacks": feedbacks}, f, ensure_ascii=False, indent=2)
        with open(ARQ_USU, "w", encoding="utf-8") as f:
            for u in usuarios:
                f.write(f"{u['id']};{u['nome']};{u['idade']};{u['profissao']};{u['tipo']}\n")
        with open(ARQ_FEED, "w", encoding="utf-8") as f:
            for x in feedbacks:
                f.write(f"{x['id']};{x['usuario_id']};{x['produto']};{x['nota']};{x['data']};{x['texto']}\n")
        print("[OK] Dados salvos em JSON e TXT.")
    except OSError as e:
        print(f"[ERRO] Falha ao salvar: {e}")


def carregar_dados():
    """Carrega do JSON (ou dos TXT se não houver JSON). Retorna (usuarios, feedbacks)."""
    try:
        if os.path.exists(ARQ_JSON):
            with open(ARQ_JSON, encoding="utf-8") as f:
                d = json.load(f)
            print("[OK] Dados carregados do JSON.")
            return d["usuarios"], d["feedbacks"]
        if os.path.exists(ARQ_USU) and os.path.exists(ARQ_FEED):
            usuarios = []
            feedbacks = []
            with open(ARQ_USU, encoding="utf-8") as f:
                for linha in f:
                    p = linha.strip().split(";")
                    usuarios.append({"id": int(p[0]), "nome": p[1], "idade": int(p[2]),
                                     "profissao": p[3], "tipo": p[4]})
            with open(ARQ_FEED, encoding="utf-8") as f:
                for linha in f:
                    p = linha.strip().split(";", 5)
                    feedbacks.append({"id": int(p[0]), "usuario_id": int(p[1]), "produto": p[2],
                                      "nota": int(p[3]), "data": p[4], "texto": p[5]})
            print("[OK] Dados carregados dos TXT.")
            return usuarios, feedbacks
        print("Nenhum arquivo salvo encontrado. Começando do zero")
    except (OSError, ValueError, KeyError, IndexError) as e:
        print(f"[ERRO] Arquivo ilegível ({e}). Começando do zero.")
    return [], []

def main():
        """Laço principal do menu interativo."""
        usuarios, feedbacks = carregar_dados()
        while True:
            titulo("FEEDSMART - Menu")
            print(" 1) Cadastrar usuário\n 2) Listar usuários\n 3) Registrar feedback\n 4) Relatório\n"
                  " 5) Análise avançada\n 6) Insights automáticos\n 7) Salvar dados\n 8) Carregar dados\n 0) Sair")
            try:
                op = ler_inteiro("\nOpção: ", 0, 8)
            except (KeyboardInterrupt, EOFError):
                break
            if op == 1:
                cadastrar_usuario(usuarios)
            elif op == 2:
                listar_usuarios(usuarios)
            elif op == 3:
                registrar_feedback(usuarios, feedbacks)
            elif op == 4:
                gerar_relatorio(feedbacks)
            elif op == 5:
                analise_avancada(usuarios, feedbacks)
            elif op == 6:
                gerar_insights(usuarios, feedbacks)
            elif op == 7:
                salvar_dados(usuarios, feedbacks)
            elif op == 8:
                usuarios, feedbacks = carregar_dados()
            else:
                if input("Salvar antes de sair? (s/n): ").strip().lower() == "s":
                    salvar_dados(usuarios, feedbacks)
                print("Até logo!")
                break

if __name__ == "__main__":
        main()

