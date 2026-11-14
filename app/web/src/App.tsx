import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Describe from './pages/company/Describe'
import Editor from './pages/company/Editor'
import Inbox from './pages/company/Inbox'
import Meetings from './pages/company/Meetings'
import Conversation from './pages/company/Conversation'
import Closure from './pages/company/Closure'
import Story from './pages/talent/Story'
import Browse from './pages/talent/Browse'
import Overview from './pages/organiser/Overview'
import { DraftProvider } from './state/company'

export default function App() {
  return (
    <DraftProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="company" element={<Describe />} />
          <Route path="company/card" element={<Editor />} />
          <Route path="company/sparks" element={<Inbox />} />
          <Route path="company/meetings" element={<Meetings />} />
          <Route path="company/meetings/:id" element={<Conversation />} />
          <Route path="company/meetings/:id/closure" element={<Closure />} />
          <Route path="talent" element={<Story />} />
          <Route path="talent/sparks" element={<Browse />} />
          <Route path="organiser" element={<Overview />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </DraftProvider>
  )
}
