import { SubNav } from '../../components/Layout'

export default function TalentNav() {
  return (
    <SubNav
      items={[
        { to: '/talent', label: '1. Work story' },
        { to: '/talent/sparks', label: '2. Send a Spark' },
      ]}
    />
  )
}
