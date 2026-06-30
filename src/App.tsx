import Download from "./sections/Download";
import Hero from "./sections/Hero";
import Features from "./sections/Features";
import Donate from "./sections/Donate";
import HashScroll from "./components/HashScroll";
import { Header } from "./components/Header";
import Footer from "./components/Footeer";


function App() {

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <HashScroll />

      <Header />
      <main>
        <Hero />
        <Features />
        <Download />
        <Donate />
      </main>
      <Footer />
    </div>
  )
}

export default App
