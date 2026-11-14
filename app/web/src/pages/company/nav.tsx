import { SubNav } from '../../components/Layout'

export default function CompanyNav() {
  return (
    <SubNav
      items={[
        { to: '/company', label: '1. Describe your need' },
        { to: '/company/card', label: '2. Challenge Card' },
        { to: '/company/sparks', label: '3. Sparks' },
        { to: '/company/meetings', label: '4. Meetings' },
      ]}
    />
  )
}
