import { Button, Label, Select } from "flowbite-react";
import { useState } from "react";
import { HiDownload } from "react-icons/hi";
import { FaCopy } from "react-icons/fa";

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

  onDownload?: () => void;
  onCopy?: (value: string) => void;
}

export function PixModalContent({
  title = "Compartilhe a Chave Pix",
  description = "Compartilhe a Chave Pix para receber pagamentos",
  qrCodeUrl,
  pixOptions,
  defaultValue,
  onDownload,
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

  return (
    <div className="flex flex-col items-center text-center">
      {/* Header */}
      <h2 className="text-2xl font-bold mb-2">{title}</h2>
      <p className="text-gray-500 mb-6">{description}</p>

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
        <Label className="mb-2 block">Chave Pix</Label>
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
          onClick={onDownload}
          className="w-full bg-green-500 hover:bg-green-600"
        >
          <HiDownload className="mr-2 h-5 w-5" />
          Baixar
        </Button>

        <Button
          onClick={handleCopy}
          color="light"
          className="w-full"
        >
          <FaCopy className="mr-2 h-4 w-4" />
          Pix Copia e Cola
        </Button>
      </div>
    </div>
  );
}