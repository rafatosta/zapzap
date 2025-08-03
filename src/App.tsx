
import Home from "./pages/Home";
import Features from "./pages/Features";
import Background from "./components/Background";
import WhyZapZap from "./pages/WhyZapZap";
import About from "./pages/About";
import Donate from "./pages/Donate";
import { Navbar } from "./components/Navbar";
import Download from "./pages/Download";



export default function App() {

  return (

    <>
      <Navbar />
      <main className="
        flex flex-col items-center justify-center min-h-screen
      bg-white px-4 dark:bg-gray-900 
      text-gray-900 dark:text-gray-100
      gap-20
      "
      >
        {/*Background geral */}
        <Background />

        {/* Páginas */}
        <Home />
        <Features />
        <WhyZapZap />
        <Download />
        <Donate />
        <About />

      </main>
    </>

  );
}
