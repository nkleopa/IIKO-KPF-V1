import { Routes, Route } from "react-router-dom";
import { DashboardPage } from "@/features/dashboard/page";
import { WaiterChecksPage } from "@/features/waiter-checks/page";

function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/waiter-checks" element={<WaiterChecksPage />} />
    </Routes>
  );
}

export default App;
