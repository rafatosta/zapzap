import { DarkThemeToggle } from "flowbite-react";

import patternLight from "/pattern-light.svg"
import patternDark from "/pattern-dark.svg"


function Background() {
    return (
        <>
            <div className="fixed inset-0 size-full">
                <div className="relative h-full w-full select-none">
                    <img
                        className="absolute right-0 min-w-dvh dark:hidden"
                        alt="Pattern Light"
                        src={patternLight}
                    />
                    <img
                        className="absolute right-0 hidden min-w-dvh dark:block"
                        alt="Pattern Dark"
                        src={patternDark}
                    />
                </div>
            </div>
            <div className="fixed top-4 right-4">
                <DarkThemeToggle />
            </div>
        </>
    );
}

export default Background;