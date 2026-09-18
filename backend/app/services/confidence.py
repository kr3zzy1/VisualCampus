def score_image(title: str, query: str, university: str, category: str, source_domain: str):
    text=(title+" "+query).lower(); uni=university.lower()
    reasons=[]; score=18
    tokens=[t for t in uni.split() if len(t)>3]
    if any(t in text for t in tokens): score+=38; reasons.append("Название университета найдено в поисковом контексте")
    if category.replace("_"," ") in text: score+=18; reasons.append("Поисковый контекст соответствует категории")
    if source_domain.endswith("wikimedia.org"): score+=14; reasons.append("Источник публикует страницу файла и лицензионные метаданные")
    if score < 55: reasons.append("Не удалось полностью подтвердить принадлежность по метаданным")
    return min(score, 95), reasons
