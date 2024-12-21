import { ReactElement, useState } from 'react';
import { Link } from 'react-router-dom';
import { Box, Button, IconButton } from '@mui/material';
import {
  EditRounded,
  Delete,
  FileCopy,
  RefreshRounded,
} from '@mui/icons-material';
import { Action, PaymentPlanQuery } from '@generated/graphql';
import { DeleteTargetPopulation } from '../../dialogs/targetPopulation/DeleteTargetPopulation';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { LockTargetPopulationDialog } from '../../dialogs/targetPopulation/LockTargetPopulationDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from '../../../programContext';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { t } from 'i18next';
import { useSnackbar } from '@hooks/useSnackBar';

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: PaymentPlanQuery['paymentPlan'];
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function OpenTargetPopulationHeaderButtons({
  targetPopulation,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InProgressTargetPopulationHeaderButtonsPropTypes): ReactElement {
  const [openLock, setOpenLock] = useState(false);
  const { showMessage } = useSnackbar();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const { baseUrl } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();

  const { mutatePaymentPlanAction: rebuild, loading: loadingRebuild } =
    usePaymentPlanAction(Action.TpRebuild, targetPopulation.id, () =>
      showMessage(t('Payment Plan has been rebuilt.')),
    );

  return (
    <Box display="flex" alignItems="center">
      {canDuplicate && (
        <IconButton
          onClick={() => setOpenDuplicate(true)}
          data-cy="button-target-population-duplicate"
          disabled={!isActiveProgram}
        >
          <FileCopy />
        </IconButton>
      )}
      {canRemove && (
        <IconButton
          data-cy="button-delete"
          onClick={() => setOpenDelete(true)}
          disabled={!isActiveProgram}
        >
          <Delete />
        </IconButton>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            data-cy="button-edit"
            variant="outlined"
            color="primary"
            startIcon={<EditRounded />}
            component={Link}
            to={`/${baseUrl}/target-population/edit-tp/${targetPopulation.id}`}
            disabled={!isActiveProgram}
          >
            Edit
          </Button>
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            data-cy="button-rebuild"
            variant="outlined"
            color="primary"
            disabled={loadingRebuild || !isActiveProgram}
            startIcon={<RefreshRounded />}
            onClick={() => rebuild()}
          >
            Rebuild
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setOpenLock(true)}
            data-cy="button-target-population-lock"
            disabled={!isActiveProgram}
          >
            Lock
          </Button>
        </Box>
      )}
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <DeleteTargetPopulation
        open={openDelete}
        setOpen={setOpenDelete}
        targetPopulationId={targetPopulation.id}
      />
      <LockTargetPopulationDialog
        open={openLock}
        setOpen={setOpenLock}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
}
