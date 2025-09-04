import NewPeriodicDataUpdates from './NewPeriodicDataUpdates';
import withErrorBoundary from '@components/core/withErrorBoundary';
import PeriodicDataUpdatePendingForApproval from './PeriodicDataUpdatePendingForApproval';
import { Box } from '@mui/material';
import PeriodicDataUpdatePendingForMerge from './PeriodicDataUpdatePendingForMerge';
import MergedPeriodicDataUpdates from './MergedPeriodicDataUpdates';

function PeriodicDataUpdatesOnlineEdits() {
  return (
    <>
      <Box pr={3} pl={3}>
        <NewPeriodicDataUpdates />
      </Box>
      <Box p={3}>
        <PeriodicDataUpdatePendingForApproval />
      </Box>
      <Box p={3}>
        <PeriodicDataUpdatePendingForMerge />
      </Box>
      <Box p={3}>
        <MergedPeriodicDataUpdates />
      </Box>
    </>
  );
}

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEdits,
  'PeriodicDataUpdatesOnlineEdits',
);
