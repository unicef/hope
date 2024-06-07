import { useEffect } from 'react';

export const RapidProFlowsLoader: React.FC<{
  open: boolean;
  verificationChannel: string;
  loadRapidProFlows: () => void;
}> = ({ open, verificationChannel, loadRapidProFlows }) => {
  useEffect(() => {
    if (open && verificationChannel === 'RAPIDPRO') {
      loadRapidProFlows();
    }
  }, [open, verificationChannel, loadRapidProFlows]);

  return null;
};
