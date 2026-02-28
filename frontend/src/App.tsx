import { BrowserRouter, Route, Routes } from "react-router-dom";
import { DocumentListPage } from "./pages/DocumentListPage";
import { DocumentDetailPage } from "./pages/DocumentDetailPage";
import { DocumentPreviewPage } from "./pages/DocumentPreviewPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <Routes>
          <Route path="/" element={<DocumentListPage />} />
          <Route path="/documents/:id" element={<DocumentDetailPage />} />
          <Route path="/documents/:id/preview" element={<DocumentPreviewPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
