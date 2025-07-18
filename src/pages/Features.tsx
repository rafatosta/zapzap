import zapDark from "/screenshot/2.png"

function Features() {
    return (
        <div className="relative flex h-screen w-full max-w-5xl flex-col items-center justify-center gap-12">

            <div className="relative flex flex-col items-center gap-6">
                <h1 className="relative text-center text-3xl leading-[125%] font-bold text-shadow-lg/30 text-gray-900 dark:text-gray-200">
                    ZapZap – A better way to use WhatsApp on Linux
                </h1>
            </div>

            <div className="relative flex flex-row items-center gap-6">
                <img className="w-1/2" src={zapDark}></img>

                <div className="p-5 group overflow-hidden rounded-xl border border-gray-200 bg-gray-50 outline-offset-2 focus:outline-2 dark:border-gray-700 dark:bg-gray-800">
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
        </div>
    );
}

export default Features;