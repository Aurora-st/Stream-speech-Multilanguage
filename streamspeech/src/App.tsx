import { useState } from "react"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import { AppLayout } from "@/components/app-layout"
import { DashboardPage } from "@/src/pages/DashboardPage"
import { RecorderPage } from "@/src/pages/RecorderPage"

export default function App() {
  const [toast, setToast] = useState<string | null>(null)

  const handleError = (message: string) => {
    setToast(message)
    setTimeout(() => setToast(null), 4000)
  }

  return (
    <BrowserRouter>
      <AppLayout toast={toast}>
        <Routes>
          <Route path="/" element={<RecorderPage onError={handleError} />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  )
}
