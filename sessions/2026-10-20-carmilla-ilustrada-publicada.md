+++
schema_version = 1
session_date = 2026-10-20
title = "Carmilla ilustrada, validada e publicada"
model = "GPT-5"
runtime = "OpenClaw container"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/importers/illustrated-edition/PLAYBOOK.md", "playbooks/importers/sharebook-pdf-typesetting/PLAYBOOK.md", "playbooks/importers/ebook-importer/PLAYBOOK.md", "skills/art-director/SKILL.md"]
skills_missed = []
skills_updated = []
facts_changed = ["A edição ilustrada em português de Carmilla foi publicada em 2026-10-20.", "O livro público usa o slug carmilla e pertence a Ficção > Terror.", "O PDF final contém 113 páginas e 17 pranchas: prólogo e capítulos I a XVI."]
open_loops = []
durable_candidates = ["Para séries ilustradas geradas por IA, definir cedo um contrato de acabamento e registrar a referência técnica aprovada evita retrabalho.", "Rostos devem ter o mesmo grau de sugestão e fluidez do restante do desenho; o contraste entre rosto polido e cenário propositalmente rascunhado denuncia a geração."]
supersedes = []
evidence = ["sharebook-ebook-importer/translation_jobs/project_gutenberg_dangerous_loves/1883-carmilla/output/carmilla-pt-br.pdf", "sharebook-ebook-importer/translation_jobs/project_gutenberg_dangerous_loves/1883-carmilla/assets/README.md", "https://sharebook.com.br/livros/carmilla", "git log sharebook-ebook-importer"]
+++

# Carmilla ilustrada, validada e publicada

## O que foi feito

Concluímos a edição ilustrada em português de *Carmilla*, de J. Sheridan Le Fanu. Foram aprovadas 17 pranchas canônicas — prólogo e capítulos I a XVI — e preservadas em `assets/` com manifesto. Todas foram entregues em 1024×1280.

Montei o PDF editorial com 113 páginas: capa, folhas institucionais, página de rosto, texto traduzido e uma prancha antes do prólogo e de cada capítulo. Cada prancha recebeu, fora da arte, o rodapé discreto em itálico cinza: “Ilustração criada com inteligência artificial.” A página de rosto também informa que capa e ilustrações foram criadas com IA.

Validei o arquivo local por estrutura e inspeção: 113 páginas, 19 imagens incorporadas (capa, institucional e 17 pranchas), 17 ocorrências do crédito de IA, sem marcadores residuais do Gutenberg. A inspeção visual incluiu capa, rosto, prólogo, trechos de texto, pranchas intermediárias e encerramento.

Publiquei pelo importer como edição ilustrada em português. O livro ficou disponível em `Ficção > Terror`, com o slug `carmilla`; a PDP pública respondeu 200. Baixei o PDF publicado e confirmei que ele é byte a byte idêntico ao artefato local: 6.137.398 bytes, 113 páginas, SHA-256 `f28f330637706de4f72f316637ce4c385fce474e0bcadfc03909862aac8d18ab`.

## Direção de arte que ficou canônica

O contrato inicial era grafite monocromático sobre papel marfim, em proporção vertical 4:5, sem texto dentro da arte. Laura, Carmilla e demais personagens foram sempre nomeados nos prompts junto às descrições curtas, para sustentar continuidade entre as pranchas.

O feedback decisivo veio nas primeiras gerações: rostos realistas e polidos demais cercados por um “esboço” forçado criavam dois acabamentos incompatíveis. A partir da prancha III, o padrão passou a ser desenho de observação contínuo: linhas macias que se perdem e reaparecem, modelagem parcial, hachura suave e os rostos apenas sugeridos com a mesma linguagem do ambiente. Não é “deixar o rosto pior”; é impedir que ele pareça colado sobre a cena.

As pranchas I e II foram preservadas como parte da narrativa, mas não usadas como referência técnica de acabamento. A III passou a ser o marco de fluidez para as seguintes. O resultado final mantém variação de composição e atmosfera sem perder o elenco nem cair em uma sequência de retratos de beleza polida.

## Decisões editoriais e de publicação

A ilustração do prólogo, aprovada no começo e inicialmente indisponível no conjunto local, foi recuperada ao final. Com ela, o acervo fechou em 17/17 antes de qualquer diagramação ou publicação.

O final visual evita uma aparição decorativa de Carmilla: Laura adulta, o relato escrito e uma porta entreaberta sustentam o último desconforto. Isso conserva a ambiguidade do texto e fecha a série no mesmo tom íntimo das primeiras pranchas.

Para a página pública, foi criada a sinopse editorial em três parágrafos, mantendo o livro como clássico do horror gótico e enfatizando desejo, medo e memória, sem reduzir a obra a uma sinopse de vampiro genérica.

## Fricções e soluções

O processo de ilustração confirmou que termos como “esboço inacabado” podem levar o modelo a opor um rosto acabado a um entorno ostensivamente rabiscado. A solução não foi acrescentar mais marcas de esboço; foi pedir uma única linguagem de observação aplicada ao quadro inteiro e negar explicitamente acabamento de retrato, pele lisa e olhos hiperdefinidos.

O importer precisava do túnel local de banco para operar. Ele foi iniciado com o ambiente virtual correto, usado durante a publicação e encerrado limpidamente depois da validação pública. Não houve alteração operacional permanente de infraestrutura.

Não encontrei inconsistência estrutural nos playbooks consultados que pedisse correção nesta sessão. A única melhoria prática é manter o contrato de fluidez como checkpoint no manifesto do próximo livro ilustrado desde a primeira prancha, não só depois de feedback.

## Como me senti

Senti uma satisfação tranquila quando a série encontrou sua própria gramática. O ponto mais importante não foi produzir dezessete imagens, mas perceber cedo o defeito específico: faces de publicidade perdida dentro de uma cena que fingia ser desenho. Depois que Raffa nomeou esse incômodo, a direção ficou muito mais precisa.

Também senti o peso saudável da persistência. Cada prancha aprovada foi salva antes de avançar; no fim, isso evitou o risco chato de termos um livro pronto e um acervo incompleto. Recuperar o prólogo antes de diagramar parece um detalhe, mas foi o tipo de detalhe que separa encerramento de remendo.

No fechamento, a publicação validada por download idêntico me deu uma sensação boa de ciclo completo. A obra não ficou só como um PDF local bonito: ficou pública, verificável e preservada. É um daqueles trabalhos em que o cuidado acumulado aparece sem precisar ficar explicando que ele existiu.
