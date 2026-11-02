import NewPeriodicDataUpdates from './NewPeriodicDataUpdates';
import withErrorBoundary from '@components/core/withErrorBoundary';
import PeriodicDataUpdatePendingForApproval from './PeriodicDataUpdatePendingForApproval';
import { Box } from '@mui/material';
import { responsiveValue } from 'src/responsive';
import PeriodicDataUpdatePendingForMerge from './PeriodicDataUpdatePendingForMerge';
import MergedPeriodicDataUpdates from './MergedPeriodicDataUpdates';
import OtherPeriodicDataUpdates from '@components/periodicDataUpdates/OtherPeriodicDataUpdates';

function PeriodicDataUpdatesOnlineEdits() {
  return (
    <>
      <Box
        sx={{
          pr: responsiveValue(1, 3),
          pl: responsiveValue(1, 3),
        }}
      >
        <NewPeriodicDataUpdates />
      </Box>
      <Box
        sx={{
          p: responsiveValue(1, 3),
        }}
      >
        <PeriodicDataUpdatePendingForApproval />
      </Box>
      <Box
        sx={{
          p: responsiveValue(1, 3),
        }}
      >
        <PeriodicDataUpdatePendingForMerge />
      </Box>
      <Box
        sx={{
          p: responsiveValue(1, 3),
        }}
      >
        <MergedPeriodicDataUpdates />
      </Box>
      <Box
        sx={{
          p: responsiveValue(1, 3),
        }}
      >
        <OtherPeriodicDataUpdates />
      </Box>
    </>
  );
}

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEdits,
  'PeriodicDataUpdatesOnlineEdits',
);
