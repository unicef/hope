import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlansFilters } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansFilters';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { ProgramCycleDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsHeader';
import { ProgramCycleDetailsSection } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsSection';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useLocation, useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
  isFollowUp: false,
};

export const ProgramCycleDetailsPage = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const { programCycleId } = useParams();
  const location = useLocation();
  const permissions = usePermissions();
  const [createGroupOpen, setCreateGroupOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');

  const handleCreateGroup = (): void => {
    // TODO: POST /api/rest/business-areas/{businessArea}/payment-plan-groups/ with { name: newGroupName, cycle: programCycleId }
    // endpoint not yet available — wire up when backend is ready
    setCreateGroupOpen(false);
    setNewGroupName('');
  };

  const { data, isLoading } = useQuery<ProgramCycleList>({
    queryKey: ['programCyclesDetails', businessArea, programCycleId, programId],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsCyclesRetrieve({
        businessAreaSlug: businessArea,
        id: programCycleId,
        programCode: programId,
      });
    },
  });

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (isLoading) return null;

  return (
    <>
      <ProgramCycleDetailsHeader programCycle={data} />
      <ProgramCycleDetailsSection programCycle={data} />
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddIcon />}
        onClick={() => setCreateGroupOpen(true)}
        sx={{ mb: 2, ml: 2 }}
      >
        Create Payment Plan Group
      </Button>
      <Dialog open={createGroupOpen} onClose={() => setCreateGroupOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Create Payment Plan Group</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Group Name"
            fullWidth
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateGroupOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateGroup} variant="contained" disabled={!newGroupName.trim()}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
      <TableWrapper>
        <PaymentPlansFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={(f) => {
            setAppliedFilter(f);
            setShouldScroll(true);
          }}
        />
      </TableWrapper>
      <div ref={tableRef}>
        <TableWrapper>
          <PaymentPlansTable
            programCycle={data}
            filter={appliedFilter}
            canViewDetails={hasPermissions(
              PERMISSIONS.PM_VIEW_DETAILS,
              permissions,
            )}
          />
        </TableWrapper>
      </div>
    </>
  );
};
export default withErrorBoundary(
  ProgramCycleDetailsPage,
  'ProgramCycleDetailsPage',
);
