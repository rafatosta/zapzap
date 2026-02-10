# Notificações e Ícones Dinâmicos (DBus vs Flatpak)

Este aplicativo utiliza **dois mecanismos distintos de notificação**, dependendo do ambiente em que está sendo executado.  
Essa decisão é **intencional** e segue as limitações técnicas e de segurança impostas por cada plataforma.

Este documento existe para **esclarecer diferenças de comportamento**, especialmente em relação ao **uso de ícones dinâmicos (avatar/foto do contato)**, e para **evitar confusão ou reclamações desnecessárias**.

---

## 📌 Resumo rápido

| Ambiente | Backend usado | Ícones dinâmicos |
|--------|---------------|------------------|
| Desktop tradicional (DEB / RPM / AppImage) | DBus direto (`org.freedesktop.Notifications`) | ✅ **Suportado** |
| Flatpak | Portal (`org.freedesktop.portal.Notification`) | ❌ **Não suportado** |

➡️ **Isso não é um bug do aplicativo.**  
➡️ É uma **limitação intencional do Flatpak e do xdg-desktop-portal**.

---

## 🔔 Por que existem dois backends de notificação?

### 1. DBus direto (Desktop tradicional)

Quando o aplicativo é executado fora de sandbox (instalação tradicional), ele utiliza diretamente:

```
org.freedesktop.Notifications
```

Esse backend permite:
- ✔ ícones dinâmicos por notificação
- ✔ fotos de contato / avatar
- ✔ uso de `image-path` e imagens arbitrárias
- ✔ notificações ricas (experiência completa)

➡️ Nesse modo, **o avatar do contato é exibido normalmente**.

---

### 2. Portal (Flatpak)

Quando o aplicativo roda como Flatpak, ele **obrigatoriamente** utiliza:

```
org.freedesktop.portal.Notification
```

Essa API foi projetada com foco em:
- sandboxing
- segurança
- consistência visual
- prevenção de spoofing e phishing

Por esse motivo, o Portal **deliberadamente NÃO permite**:
- ❌ `image-path`
- ❌ `image-data`
- ❌ caminhos de arquivos arbitrários
- ❌ fotos de contato ou avatares dinâmicos

O Portal permite apenas:
- ✔ ícone fixo do aplicativo (desktop-entry)
- ✔ título
- ✔ mensagem
- ✔ ações (botões)

➡️ **Qualquer tentativa de usar ícones dinâmicos no Portal é ignorada silenciosamente.**

---

## ❗ Importante: isso não é uma limitação do app

Essa limitação:
- ❌ **não é bug**
- ❌ **não é falta de implementação**
- ❌ **não é algo que o aplicativo possa corrigir**

Ela existe no nível da **API do sistema** e afeta **todos os apps Flatpak**, incluindo:
- Telegram
- Discord
- Slack
- Signal
- WhatsApp Web wrappers

Todos eles exibem:
- avatar no desktop tradicional
- apenas o ícone do app no Flatpak

---

## 🧠 Decisão arquitetural do projeto

O aplicativo foi projetado para:
- usar **o melhor backend disponível**
- respeitar **as regras da plataforma**
- não aplicar hacks inseguros ou não suportados

Estratégia adotada:

- **DBus direto** → experiência rica (avatar, imagem dinâmica)
- **Portal (Flatpak)** → experiência segura e compatível

Essa separação é **intencional e correta**.

---

## 💡 Alternativas visuais usadas no Flatpak

Como o avatar não é permitido, o app prioriza:
- nome do contato no título
- mensagens claras
- ações rápidas (abrir conversa, focar janela)

Essas são as **únicas alternativas compatíveis com o Portal atualmente**.

---

## 📅 Possível suporte futuro

Há discussões upstream sobre enriquecer notificações via Portal, mas:
- não existe suporte estável até o momento
- não há previsão oficial
- qualquer mudança depende do `xdg-desktop-portal`

Quando (e se) isso mudar, o backend poderá ser atualizado.

---

## ✅ Conclusão

Se você está usando o aplicativo via **Flatpak** e percebe que:
- o avatar não aparece nas notificações  
- apenas o ícone do app é exibido  

➡️ **isso é o comportamento esperado e correto.**

Para notificações completas com ícones dinâmicos, utilize:
- instalação tradicional (DEB/RPM)
- AppImage
- execução fora de sandbox

---

Se ainda tiver dúvidas, consulte este documento antes de abrir uma issue.

---
---

# Notifications and Dynamic Icons (DBus vs Flatpak)

This application uses **two different notification mechanisms**, depending on the environment in which it is running.  
This behavior is **intentional** and follows the technical and security constraints imposed by each platform.

This document exists to **clarify behavioral differences**, especially regarding the use of **dynamic icons (contact avatar/photo)**, and to **prevent confusion or unnecessary complaints**.

---

## 📌 Quick summary

| Environment | Backend used | Dynamic icons |
|------------|-------------|---------------|
| Traditional desktop (DEB / RPM / AppImage) | Direct DBus (`org.freedesktop.Notifications`) | ✅ **Supported** |
| Flatpak | Portal (`org.freedesktop.portal.Notification`) | ❌ **Not supported** |

➡️ **This is not a bug in the application.**  
➡️ It is an **intentional limitation of Flatpak and xdg-desktop-portal**.

---

## 🔔 Why are there two notification backends?

### 1. Direct DBus (Traditional desktop)

When the application runs outside a sandbox (traditional installation), it directly uses:

```
org.freedesktop.Notifications
```

This backend allows:
- ✔ dynamic icons per notification
- ✔ contact photos / avatars
- ✔ usage of `image-path` and arbitrary images
- ✔ rich notifications (full experience)

➡️ In this mode, **the contact avatar is displayed normally**.

---

### 2. Portal (Flatpak)

When the application runs as a Flatpak, it **must** use:

```
org.freedesktop.portal.Notification
```

This API is designed with a focus on:
- sandboxing
- security
- visual consistency
- prevention of spoofing and phishing

For this reason, the Portal **deliberately DOES NOT allow**:
- ❌ `image-path`
- ❌ `image-data`
- ❌ arbitrary file paths
- ❌ dynamic contact photos or avatars

The Portal only allows:
- ✔ fixed application icon (desktop-entry)
- ✔ title
- ✔ message body
- ✔ actions (buttons)

➡️ **Any attempt to use dynamic icons in the Portal is silently ignored.**

---

## ❗ Important: this is not an app limitation

This limitation:
- ❌ **is not a bug**
- ❌ **is not a missing feature**
- ❌ **cannot be fixed by the application**

It exists at the **system API level** and affects **all Flatpak applications**, including:
- Telegram
- Discord
- Slack
- Signal
- WhatsApp Web wrappers

All of them display:
- avatars on traditional desktop installations
- only the application icon when running as Flatpak

---

## 🧠 Architectural decision

The application is designed to:
- use **the best backend available**
- respect **platform rules**
- avoid insecure or unsupported hacks

Adopted strategy:

- **Direct DBus** → rich experience (avatar, dynamic images)
- **Portal (Flatpak)** → secure and compatible experience

This separation is **intentional and correct**.

---

## 💡 Visual alternatives used on Flatpak

Since avatars are not allowed, the app prioritizes:
- contact name in the title
- clear message text
- quick actions (open conversation, focus window)

These are the **only alternatives currently compatible with the Portal**.

---

## 📅 Possible future support

There are upstream discussions about enriching notifications via the Portal, but:
- no stable support exists at this time
- there is no official timeline
- any change depends on `xdg-desktop-portal`

If (and when) this changes, the backend can be updated accordingly.

---

## ✅ Conclusion

If you are using the application via **Flatpak** and notice that:
- contact avatars do not appear in notifications  
- only the application icon is shown  

➡️ **this is the expected and correct behavior.**

For full notifications with dynamic icons, use:
- traditional installation (DEB/RPM)
- AppImage
- execution outside a sandbox

---

If you still have questions, please consult this document before opening an issue.
