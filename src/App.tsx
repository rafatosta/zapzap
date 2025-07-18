
import Home from "./pages/Home";
import Features from "./pages/Features";
import Background from "./components/Background";
import WhyZapZap from "./pages/WhyZapZap";
import About from "./pages/About";



export default function App() {

  return (
    <main className="
        flex min-h-screen flex-col items-center justify-center 
      bg-white px-4 dark:bg-gray-900 
      text-gray-900 dark:text-gray-100
      "
    >
      {/*Background geral */}
      <Background />

      {/* Páginas */}
      <Home />
      <Features />
      <WhyZapZap />
      <About />

    </main>
  );
}
