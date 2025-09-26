import { useTranslation } from "react-i18next";
import { Dropdown, DropdownItem, Avatar } from "flowbite-react";

type Language = {
  code: "en" | "pt";
  label: string;
  flag: string; // emoji ou caminho para imagem
};

const languages: Language[] = [
  { code: "pt", label: "Português", flag: "🇧🇷" },
  { code: "en", label: "English", flag: "🇺🇸" },
];

function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const currentLang =
    languages.find((lng) => lng.code === i18n.language) || languages[0];

  const changeLanguage = (lng: "en" | "pt") => {
    i18n.changeLanguage(lng);
  };

  return (
    <Dropdown
      inline
      label={
        <div className="flex items-center gap-2">
          <span>{currentLang.flag}</span>
          <span className="hidden sm:inline">{currentLang.label}</span>
        </div>
      }
    >
      {languages.map((lng) => (
        <DropdownItem key={lng.code} onClick={() => changeLanguage(lng.code)}>
          <span className="flex items-center gap-2">
            <span>{lng.flag}</span>
            {lng.label}
          </span>
        </DropdownItem>
      ))}
    </Dropdown>
  );
}

export default LanguageSwitcher;
