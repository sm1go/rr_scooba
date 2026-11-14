import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'
import { AuthProvider, useAuth } from './lib/auth'
import { I18nProvider } from './i18n/i18n'
import { A11yProvider } from './lib/a11y'
import Layout from './components/Layout'
import JobsPage from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Apply from './pages/Apply'
import Help from './pages/Help'
import Applications from './pages/Applications'
import Saved from './pages/Saved'
import Profile from './pages/Profile'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import EmployerJobs from './pages/employer/EmployerJobs'
import EmployerJobForm from './pages/employer/EmployerJobForm'
import EmployerApplications from './pages/employer/EmployerApplications'
import EmployerCompany from './pages/employer/EmployerCompany'
import AdvisorQueue from './pages/advisor/AdvisorQueue'
import { AdvisorJobs, AdvisorJobCheck, AdvisorApplyFor } from './pages/advisor/AdvisorJobs'
import AdvisorFollowUp from './pages/advisor/AdvisorFollowUp'

function Guard({ roles, children }: { roles?: string[]; children: ReactNode }) {
  const { user, ready } = useAuth()
  const loc = useLocation()
  if (!ready) return null
  if (!user) {
    return <Navigate to={`/sign-in?back=${encodeURIComponent(loc.pathname + loc.search)}`} replace />
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <I18nProvider>
      <A11yProvider>
        <AuthProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<JobsPage />} />
              <Route path="/jobs/:id" element={<JobDetail />} />
              <Route path="/jobs/:id/apply"
                     element={<Guard roles={['resident']}><Apply /></Guard>} />
              <Route path="/help" element={<Help />} />
              <Route path="/applications"
                     element={<Guard roles={['resident']}><Applications /></Guard>} />
              <Route path="/saved"
                     element={<Guard roles={['resident']}><Saved /></Guard>} />
              <Route path="/profile"
                     element={<Guard roles={['resident']}><Profile /></Guard>} />
              <Route path="/sign-in" element={<SignIn />} />
              <Route path="/sign-up" element={<SignUp />} />

              <Route path="/employer"
                     element={<Guard roles={['employer']}><EmployerJobs /></Guard>} />
              <Route path="/employer/jobs/new"
                     element={<Guard roles={['employer']}><EmployerJobForm /></Guard>} />
              <Route path="/employer/jobs/:id"
                     element={<Guard roles={['employer']}><EmployerJobForm /></Guard>} />
              <Route path="/employer/applications"
                     element={<Guard roles={['employer']}><EmployerApplications /></Guard>} />
              <Route path="/employer/company"
                     element={<Guard roles={['employer']}><EmployerCompany /></Guard>} />

              <Route path="/advisor"
                     element={<Guard roles={['advisor']}><AdvisorQueue /></Guard>} />
              <Route path="/advisor/jobs"
                     element={<Guard roles={['advisor']}><AdvisorJobs /></Guard>} />
              <Route path="/advisor/jobs/new"
                     element={<Guard roles={['advisor']}><EmployerJobForm /></Guard>} />
              <Route path="/advisor/jobs/:id/edit"
                     element={<Guard roles={['advisor']}><EmployerJobForm /></Guard>} />
              <Route path="/advisor/jobs/:id/check"
                     element={<Guard roles={['advisor']}><AdvisorJobCheck /></Guard>} />
              <Route path="/advisor/jobs/:id/apply-for"
                     element={<Guard roles={['advisor']}><AdvisorApplyFor /></Guard>} />
              <Route path="/advisor/follow-up"
                     element={<Guard roles={['advisor']}><AdvisorFollowUp /></Guard>} />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </AuthProvider>
      </A11yProvider>
    </I18nProvider>
  )
}
