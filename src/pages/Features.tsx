import zapDark from "/screenshot/2.png";
import zapLight from "/screenshot/1.png";

import {
    FaUserFriends,
    FaBell,
    FaBoxOpen,
    FaPalette,
    FaLock,
    FaSyncAlt,
} from "react-icons/fa";

function Features() {
    return (
        <div className="relative flex  w-full max-w-5xl flex-col items-center justify-center gap-12">

            <div className="relative flex flex-col items-center gap-6">
                <h1 className="relative text-center text-3xl leading-[125%] font-bold text-shadow-lg">
                    ZapZap – A better way to use WhatsApp on Linux
                </h1>
            </div>


            <div className="relative flex flex-row items-center gap-6">
                {/* Imagem adaptada ao tema */}
                <>
                    <img className="w-1/2 dark:hidden" src={zapLight} alt="ZapZap light screenshot" />
                    <img className="w-1/2 hidden dark:block" src={zapDark} alt="ZapZap dark screenshot" />
                </>

                <div className="p-5 group overflow-hidden rounded-xl outline-offset-2 focus:outline-2">
                    <div className="flex flex-col items-center gap-4 text-justify">
                        <span>
                            <span className="text-primary font-medium">ZapZap</span> is a <span className="text-primary font-medium">modern</span> and <span className="text-primary font-medium">efficient</span> WhatsApp web wrapper built for <span className="text-primary font-medium">Linux users</span> who want more <span className="text-primary font-medium">control</span>, <span className="text-primary font-medium">flexibility</span>, and <span className="text-primary font-medium">native integration</span>.
                            With <span className="text-primary font-medium">multi-account support</span>, <span className="text-primary font-medium">system tray notifications</span>, <span className="text-primary font-medium">spell checking</span>, <span className="text-primary font-medium">drag-and-drop media sharing</span>, and <span className="text-primary font-medium">automatic theme adaptation</span>, ZapZap brings a
                            <span className="text-primary font-medium"> native-like experience</span> to your desktop.
                        </span>
                        <span>
                            Stay <span className="text-primary font-medium">productive</span> with <span className="text-primary font-medium">background mode</span>, receive <span className="text-primary font-medium">native notifications</span>, and enjoy a <span className="text-primary font-medium">clean, focused interface</span> — all without compromising on
                            <span className="text-primary font-medium"> usability</span> or <span className="text-primary font-medium">style</span>.
                        </span>
                    </div>
                </div>
            </div>

            <h1 className="text-xl font-bold leading-snug  text-center text-shadow-lg">
                Feature highlights
            </h1>

            {/* Feature highlights */}
            <div className="grid grid-cols-2 gap-4 mt-6 text-sm">
                <Feature icon={<FaUserFriends />} label="Multi-account" />
                <Feature icon={<FaBell />} label="Native notifications" />
                <Feature icon={<FaBoxOpen />} label="Media sharing" />
                <Feature icon={<FaPalette />} label="Theme support" />
                <Feature icon={<FaLock />} label="Privacy-respecting" />
                <Feature icon={<FaSyncAlt />} label="Background mode" />
            </div>
        </div>
    );
}


function Feature({ icon, label }: { icon: React.ReactNode; label: string }) {
    return (
        <div className="flex items-center gap-2">
            <div className="text-primary w-5 h-5">{icon}</div>
            <span>{label}</span>
        </div>
    );
}

export default Features;