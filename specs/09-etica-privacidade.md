# 09 — Ética e privacidade

Imagens do corpo e dados de saúde são dados pessoais sensíveis pela LGPD (Lei 13.709/2018). Os riscos são controláveis com as regras abaixo.

## Requisitos

| ID | Requisito | Nível |
|---|---|---|
| ETI-01 | O app processa o vídeo **apenas localmente**, quadro a quadro; nenhum quadro é salvo em disco ou enviado a servidor (APP-11). Só coordenadas do esqueleto existem em memória | DEVE |
| ETI-02 | Aviso na abertura do app e no README: a ferramenta **não faz diagnóstico nem prescreve exercícios**; é apoio à prática orientada por fisioterapeuta; interrompa se sentir dor | DEVE |
| ETI-03 | UI-PRMD e KIMORE usados conforme suas condições de uso, citados no README e no relatório; dados brutos não redistribuídos no repositório | DEVE |
| ETI-04 | Termo de consentimento por escrito assinado por cada integrante que gravar vídeos (modelo em `docs/termo-consentimento.md`) | DEVE |
| ETI-05 | Vídeos próprios guardados fora do git, em pasta compartilhada restrita ao grupo, e **excluídos ao fim do projeto**; registrar data da exclusão | DEVE |
| ETI-06 | Apenas coordenadas/ângulos extraídos dos vídeos próprios podem ser mantidos (anonimizados por ID) | DEVE |
| ETI-07 | Análise de viés: desempenho separado saudáveis × pacientes (KIMORE) e limitações de diversidade (idade, biotipo, condição clínica) documentadas no relatório | DEVE |
| ETI-08 | Frames ou fotos usadas na apresentação/relatório só com autorização do integrante que aparece | DEVE |

## Critérios de aceite

- Termos assinados antes da primeira gravação.
- Busca no repositório não encontra arquivos de vídeo/imagem de integrantes (exceto os autorizados por ETI-08).
- Aviso visível no app antes de abrir a câmera.
