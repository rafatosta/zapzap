import { useEffect } from "react";

function HashScroll() {
    useEffect(() => {
        if (!window.location.hash) {
            return;
        }

        const id = window.location.hash.slice(1);

        const scrollToHash = () => {
            const element = document.getElementById(id);

            if (element) {
                element.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        };

        requestAnimationFrame(() => {
            setTimeout(scrollToHash, 100);
        });
    }, []);

    return null;
}

export default HashScroll;