import { useBaseUrl } from '@hooks/useBaseUrl';
import { FC } from 'react';

export const NewDashboardPage: FC = () => {
  const { businessArea } = useBaseUrl();
  const dashboardUrl = `${window.location.origin}/api/rest/dashboard/${businessArea}/`;
  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <iframe
        src={dashboardUrl}
        style={{
          width: '100%',
          height: '100vh',
          border: 'none',
        }}
        title="Dashboard"
      />
    </div>
  );
};
