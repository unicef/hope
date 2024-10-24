import { FC, useEffect } from 'react';

export const RapidProFlowsLoader: FC<{
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
