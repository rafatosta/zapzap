// src/i18n.js
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// importa os arquivos JSON diretamente (Vite suporta isso)
import en from "./locales/en/translation.json";
import pt from "./locales/pt/translation.json";

i18n
  .use(LanguageDetector) // detecta idioma do navegador/localStorage
  .use(initReactI18next) // conecta ao React
  .init({
    resources: {
      en: { translation: en },
      pt: { translation: pt },
    },
    fallbackLng: "en", // se não achar, usa inglês
    debug: true, // pode desligar em produção
    interpolation: {
      escapeValue: false, // React já faz proteção XSS
    },
    detection: {
      order: ["localStorage", "navigator"], // ordem de detecção
      caches: ["localStorage"], // salva escolha no localStorage
    },
  });

export default i18n;
