import {
  FaUserFriends,
  FaLock,
  FaBell,
  FaLaptop,
  FaBoxOpen,
  FaTerminal,
  FaSyncAlt
} from "react-icons/fa";
import { MdSpeed } from "react-icons/md";
import { SiFlatpak } from "react-icons/si";

import { Element } from 'react-scroll';
import { PageContainer } from "../components/PageContainer";

const FEATURES = [
  {
    icon: <FaLaptop className="text-primary w-10 h-10" />,
    title: "Simple",
    description: "ZapZap has a lightweight and intuitive interface — you already know how to use it.",
  },
  {
    icon: <FaUserFriends className="text-primary w-10 h-10" />,
    title: "Multi-account",
    description: "Use multiple WhatsApp accounts at the same time with no hassle.",
  },
  {
    icon: <FaSyncAlt className="text-primary w-10 h-10" />,
    title: "Themed",
    description: "ZapZap adapts to your system theme — light or dark mode.",
  },
  {
    icon: <MdSpeed className="text-primary w-10 h-10" />,
    title: "Productive",
    description: "Stay connected with background mode and fewer distractions.",
  },
  {
    icon: <FaBell className="text-primary w-10 h-10" />,
    title: "Organized",
    description: "Receive native notifications for your desktop environment.",
  },
  {
    icon: <FaBoxOpen className="text-primary w-10 h-10" />,
    title: "Powerful",
    description: "Easily drag and drop images, videos, and documents.",
  },
  {
    icon: <FaLock className="text-primary w-10 h-10" />,
    title: "Private",
    description: "ZapZap respects your privacy — no ads or trackers.",
  },
  {
    icon: <SiFlatpak className="text-primary w-10 h-10" />,
    title: "Portable",
    description: "Available as Flatpak, AppImage, Fedora Copr, and AUR.",
  },
  {
    icon: <FaTerminal className="text-primary w-10 h-10" />,
    title: "Open Source",
    description: "With open-source code, you can contribute or just follow along.",
  },
];

export default function WhyZapZap() {
  return (
    <Element name="why">
      <PageContainer>
        <h2 className="relative text-center text-3xl leading-[125%] text-shadow-lg font-bold">Why choose ZapZap?</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10">
          {FEATURES.map(({ icon, title, description }) => (
            <div key={title} className="flex flex-col items-center gap-4">
              <div>{icon}</div>
              <h3 className="text-lg font-semibold text-primary">{title}</h3>
              <p className="text-gray-600 dark:text-gray-200 text-center">{description}</p>
            </div>
          ))}
        </div>
      </PageContainer>
    </Element>
  );
}
