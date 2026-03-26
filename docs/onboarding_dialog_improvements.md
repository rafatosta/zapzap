# Melhorias sugeridas para `OnboardingDialog.py`

Este documento propõe melhorias para um futuro `OnboardingDialog.py`, considerando os dois modos de execução do ZapZap: **local** e **Flatpak**.

## 1) Detectar o ambiente de forma explícita

- Usar `SetupManager._is_flatpak` para customizar o fluxo de onboarding para sandbox.
- Opcionalmente, exibir o tipo de empacotamento com `EnvironmentManager.identify_packaging()` para debug e telemetria local.

## 2) Fluxo de onboarding separado por ambiente

### Ambiente local

- Mostrar onboarding curto (2-3 passos):
  1. Conta inicial
  2. Notificações
  3. Atalhos e configurações
- Evitar conteúdo sobre permissões de sandbox que não se aplica.

### Ambiente Flatpak

- Incluir passo dedicado: "Permissões do sandbox".
- Explicar claramente limitações de acesso a arquivos/arrastar-e-soltar.
- Reaproveitar o comando já usado no app:
  - `flatpak override --user --filesystem=home com.rtosta.zapzap`
- Oferecer botões:
  - "Copiar comando"
  - "Abrir Flatseal"
  - "Continuar sem permissões"

## 3) Persistência do estado de onboarding

- Criar chaves no `SettingsManager`:
  - `onboarding/completed`
  - `onboarding/version`
  - `onboarding/last_environment`
- Reabrir onboarding apenas quando:
  - versão do onboarding mudar, ou
  - ambiente mudar (local <-> Flatpak).

## 4) Mensagens orientadas a ação

- Cada etapa deve terminar com ação executável (botão/toggle).
- Evitar texto longo; usar bullets curtos e um link "Saiba mais".
- Para Flatpak, deixar claro que permissões são opcionais, mas impactam recursos específicos.

## 5) Robustez técnica

- Nunca assumir presença de variáveis de ambiente; usar fallback seguro.
- Se `QDesktopServices.openUrl` falhar, manter alternativa de copiar URL/comando.
- Garantir idempotência: abrir onboarding múltiplas vezes não deve duplicar side-effects.

## 6) Reaproveitamento de componentes já existentes

- Extrair o popover de ajuda do Flatpak (atualmente no `Browser`) para um componente reutilizável do onboarding.
- Manter ícones/tema coerentes com os métodos `set_theme_light` e `set_theme_dark`.

## 7) Métricas locais (sem backend)

- Salvar somente métricas locais no `SettingsManager`:
  - passos concluídos
  - etapa em que o usuário saiu
- Isso permite melhorar UX sem coletar dados externos.

## 8) Critérios de aceite recomendados

1. Local: onboarding sem menções a sandbox.
2. Flatpak: onboarding mostra permissões e permite copiar comando.
3. Mudou ambiente: onboarding reabre automaticamente na próxima inicialização.
4. Reabrir manualmente onboarding não quebra estado da aplicação.
