import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home/Home";
import Memory from "../pages/Memory/Memory";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/memory" element={<Memory />} />
    </Routes>
  );
}
