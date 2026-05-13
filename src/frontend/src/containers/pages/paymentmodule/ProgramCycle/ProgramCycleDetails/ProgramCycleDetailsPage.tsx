import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlansFilters } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansFilters';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { ProgramCycleDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsHeader';
import { ProgramCycleDetailsSection } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsSection';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getFilterFromQueryParams, showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useLocation, useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import {
  Box,
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
};

export const ProgramCycleDetailsPage = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const { programCycleId } = useParams();
  const location = useLocation();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [createGroupOpen, setCreateGroupOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');

  const { mutateAsync: createGroup, isPending: creatingGroup } = useMutation({
    mutationFn: (name: string) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        requestBody: { name, cycle: programCycleId } as any,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroupsList', businessArea, programId],
      });
    },
  });

  const handleCreateGroup = async (): Promise<void> => {
    try {
      await createGroup(newGroupName.trim());
      showMessage('Payment Plan Group created');
      setCreateGroupOpen(false);
      setNewGroupName('');
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
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
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          mt: 2,
          mb: 2,
          px: 2,
        }}
      >
        {hasPermissions(PERMISSIONS.PM_CREATE_PAYMENT_PLAN_GROUP, permissions) && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setCreateGroupOpen(true)}
          >
            Create Payment Plan Group
          </Button>
        )}
      </Box>
      <Dialog
        open={createGroupOpen}
        onClose={() => setCreateGroupOpen(false)}
        maxWidth="xs"
        fullWidth
      >
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
          <Button
            onClick={handleCreateGroup}
            variant="contained"
            disabled={!newGroupName.trim() || creatingGroup}
          >
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
