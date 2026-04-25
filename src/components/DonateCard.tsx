import { ReactNode, useState } from "react";
import { Card, Badge, Button, Modal, ModalHeader, ModalBody } from "flowbite-react";
import { HiExternalLink } from "react-icons/hi";
import { FaHeart } from "react-icons/fa";

type DonateCardAction =
    | {
        type: "link";
        url: string;
        target?: "_blank" | "_self";
    }
    | {
        type: "modal";
    };

interface DonateCardProps {
    title: string;
    description: string;
    features: string[];

    icon: React.ComponentType<{ className?: string }>;
    badge?: string;
    badgeColor?: string;

    buttonLabel: string;

    colors: {
        iconBg: string; // ex: "from-pink-500 to-red-500"
        buttonBg: string; // ex: "from-pink-500 to-red-500"
    };

    action: DonateCardAction;

    /** Slot para conteúdo futuro do modal */
    modalContent?: ReactNode;
}

export function DonateCard({
    title,
    description,
    features,
    icon: Icon,
    badge,
    badgeColor = "indigo",
    buttonLabel,
    colors,
    action,
    modalContent,
}: DonateCardProps) {
    const [open, setOpen] = useState(false);

    const isLink = action.type === "link";

    return (
        <>
            <Card className="group hover:-translate-y-2 hover:shadow-xl transition-all">
                <div className="p-8">
                    {/* Header */}
                    <div className="mb-4 flex items-start justify-between">
                        <div
                            className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${colors.iconBg} flex items-center justify-center transition-transform duration-300 group-hover:scale-110`}
                        >
                            <Icon className="h-8 w-8 text-white" />
                        </div>

                        {badge && (
                            <Badge color={badgeColor} className="ml-2">
                                {badge}
                            </Badge>
                        )}
                    </div>

                    {/* Conteúdo */}
                    <h3 className="mb-3 text-2xl font-bold">{title}</h3>

                    <p className="text-muted-foreground mb-6 leading-relaxed">
                        {description}
                    </p>

                    <div className="mb-6 flex flex-wrap gap-2">
                        {features.map((feature, idx) => (
                            <Badge color="indigo" key={idx} className="px-3 py-1">
                                {feature}
                            </Badge>
                        ))}
                    </div>

                    {/* Ação */}
                    {isLink ? (
                        <Button
                            as="a"
                            href={action.url}
                            target={action.target ?? "_blank"}
                            rel="noopener noreferrer"
                            className={`w-full gap-2 bg-gradient-to-r hover:shadow-xl ${colors.buttonBg}`}
                            size="lg"
                        >
                            <FaHeart className="h-5 w-5" />
                            {buttonLabel}
                            <HiExternalLink className="ml-auto h-4 w-4" />
                        </Button>
                    ) : (
                        <Button
                            onClick={() => setOpen(true)}
                            className={`w-full gap-2 bg-gradient-to-r hover:shadow-xl ${colors.buttonBg}`}
                            size="lg"
                        >
                            <FaHeart className="h-5 w-5" />
                            {buttonLabel}
                        </Button>
                    )}
                </div>
            </Card>

            {/* Modal (placeholder) */}
            <Modal show={open} onClose={() => setOpen(false)}>
                <ModalHeader>{title}</ModalHeader>
                <ModalBody>
                    {modalContent ?? (
                        <div className="text-center text-gray-500">
                            Conteúdo do modal ainda não definido.
                        </div>
                    )}
                </ModalBody>
            </Modal>
        </>
    );
}