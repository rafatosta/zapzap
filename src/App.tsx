import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";
import AboutSection from "./sections/AboutSection";
import DonateSection from "./sections/DonateSection";
import DownloadSection from "./sections/DownloadSection";
import FeatureSection from "./sections/FeatureSection";
import ProjectSection from "./sections/ProjectSection";

export default function App() {
  return (
    <div className="\ \ \ min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      <Header />
      <Hero />
      <FeatureSection />
      <ProjectSection />
      <DownloadSection />
      <DonateSection />
      <AboutSection />
      <Footer />
    </div>
  );
}
