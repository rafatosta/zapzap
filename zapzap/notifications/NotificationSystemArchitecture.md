# Notification System Architecture

Este projeto implementa um **sistema unificado de notificações** para aplicações Qt/PyQt6, com suporte a **Flatpak** e **execução nativa no desktop Linux**, abstraindo as diferenças entre os mecanismos de notificação disponíveis em cada ambiente.

---

## Visão Geral

A classe **NotificationService** atua como uma **fachada** responsável por identificar o ambiente de execução e delegar o envio de notificações ao backend apropriado.

```text
NotificationService
 ├── PortalNotificationBackend        (Flatpak)
 ├── FreedesktopNotificationBackend   (Desktop nativo)
 └── DBusNotificationManager          (Legado / python-dbus)
```

---

## Backends Disponíveis

### PortalNotificationBackend (Flatpak)

- Utiliza o **XDG Desktop Portal**
- Interface D-Bus: `org.freedesktop.portal.Notification`
- Comunicação via **QDBus (PyQt6)**
- Compatível com aplicações sandboxed (Flatpak)

**Limitações conhecidas:**
- Não permite ícones personalizados via arquivo
- Permite ícones temáticos ou `desktop-entry`
- Suporte a ações (`ActionInvoked`)
- Compatível com GNOME, KDE e outros desktops modernos

**Fluxo de uso:**

Flatpak → XDG Desktop Portal → PortalNotificationBackend

---

### FreedesktopNotificationBackend (Desktop nativo)

- Utiliza o padrão clássico de notificações do Linux
- Interface D-Bus: `org.freedesktop.Notifications`
- Projetado para execução fora do sandbox

**Status atual:**
- Backend implementado, porém **não funcional no momento**
- Motivo: diferenças de assinatura D-Bus e inconsistências entre servidores de notificação

**Fluxo esperado:**

Desktop nativo → org.freedesktop.Notifications → FreedesktopNotificationBackend

---

### DBusNotificationManager (Legado)

- Implementação baseada em **python-dbus**
- Criada antes da migração completa para **QDBus (PyQt6)**

**Status:**
- Mantido apenas por compatibilidade
- Não recomendado para novos desenvolvimentos
- Dependência externa (`python-dbus`)

---

## Estratégia de Seleção de Backend

A seleção do backend é feita automaticamente pelo `NotificationService`:

```text
Ambiente de execução | Backend utilizado
Flatpak              | PortalNotificationBackend
Desktop nativo       | FreedesktopNotificationBackend
Legado / fallback    | DBusNotificationManager
```

---

## Objetivos da Arquitetura

- Unificar o uso de notificações em diferentes ambientes
- Garantir compatibilidade com Flatpak (sandbox)
- Reduzir dependências externas
- Centralizar a lógica de decisão no `NotificationService`
- Permitir evolução independente de cada backend

---

## Observações Importantes

- O **XDG Desktop Portal** impõe restrições intencionais por segurança
- Ícones personalizados via caminho de arquivo **não são suportados no portal**
- Para Flatpak, recomenda-se o uso de:
  - `desktop-entry`
  - ícones temáticos (`icon-name`)
- O backend freedesktop ainda está em processo de estabilização

---

## Estado Atual do Projeto

- PortalNotificationBackend: estável
- FreedesktopNotificationBackend: em desenvolvimento
- DBusNotificationManager: legado

---

## Notas Finais

Esta arquitetura foi pensada para oferecer **robustez**, **portabilidade** e **compatibilidade** com o ecossistema moderno do Linux, respeitando as limitações de segurança impostas por ambientes sandboxed como o Flatpak.
