import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Delete,
  EditRounded,
  FileCopy,
  RefreshRounded,
} from '@mui/icons-material';
import { Box, Button, IconButton } from '@mui/material';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { t } from 'i18next';
import { ReactElement, useState } from 'react';
import { Link } from 'react-router-dom';
import { useProgramContext } from '../../../programContext';
import { DeleteTargetPopulation } from '../../dialogs/targetPopulation/DeleteTargetPopulation';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { LockTargetPopulationDialog } from '../../dialogs/targetPopulation/LockTargetPopulationDialog';
import { showApiErrorMessages } from '@utils/utils';

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationDetail;
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
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();

  const { mutateAsync: rebuild, isPending: loadingRebuild } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      id,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      id: string;
    }) =>
      RestService.restBusinessAreasProgramsTargetPopulationsRebuildRetrieve({
        businessAreaSlug,
        programSlug,
        id,
      }),
    onSuccess: () => showMessage(t('Payment Plan has been rebuilt.')),
    onError: (e) => showApiErrorMessages(e, showMessage),
  });

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
            onClick={() =>
              rebuild({
                businessAreaSlug: businessArea,
                programSlug: programId,
                id: targetPopulation.id,
              })
            }
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
