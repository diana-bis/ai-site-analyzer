import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import DashboardPage from "./pages/DashboardPage";
import AnalysisDetailsPage from "./pages/AnalysisDetailsPage";

// Declarative Mode only
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<UploadPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analysis/:id" element={<AnalysisDetailsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
