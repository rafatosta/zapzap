import { Button, Label, Select } from "flowbite-react";
import { useState } from "react";
import { FaCopy } from "react-icons/fa";
import { useTranslation } from "react-i18next";

interface PixOption {
  label: string;
  value: string;
}

interface PixModalContentProps {
  title?: string;
  description?: string;

  qrCodeUrl: string;

  pixOptions: PixOption[];
  defaultValue?: string;
  onCopy?: (value: string) => void;
}

export function PixModalContent({
  qrCodeUrl,
  pixOptions,
  defaultValue,
  onCopy,
}: PixModalContentProps) {
  const [selected, setSelected] = useState(
    defaultValue ?? pixOptions[0]?.value
  );

  const handleCopy = () => {
    if (onCopy) {
      onCopy(selected);
    } else {
      navigator.clipboard.writeText(selected);
    }
  };

  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center text-center">
      {/* Header */}
      <h2 className="text-2xl font-bold mb-2">{t("donationSection.pixModal.title")}</h2>
      <p className="text-gray-500 mb-6">{t("donationSection.pixModal.description")}</p>

      {/* QR Code */}
      <div className="mb-6 rounded-2xl bg-gray-100 p-4">
        <img
          src={qrCodeUrl}
          alt="QR Code Pix"
          className="w-48 h-48 object-contain"
        />
      </div>

      {/* Select */}
      <div className="w-full mb-6 text-left">
        <Label className="mb-2 block">{t("donationSection.pixModal.label")}</Label>
        <Select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {pixOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Actions */}
      <div className="w-full flex flex-col gap-3">
        <Button
          onClick={handleCopy}
          color="light"
          className="w-full"
        >
          <FaCopy className="mr-2 h-4 w-4" />
           {t("donationSection.pixModal.copy")}
        </Button>
      </div>
    </div>
  );
}