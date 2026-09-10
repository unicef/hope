import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { LoadingComponent } from '@components/core/LoadingComponent';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CreateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/CreateProgramCycle';
import UpdateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/UpdateProgramCycle';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import AddIcon from '@mui/icons-material/Add';
import { Dialog } from '@mui/material';
import type { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';

interface AddNewProgramCycleProps {
  program: Partial<ProgramDetail>;
}

const AddNewProgramCycle = ({
  program,
}: AddNewProgramCycleProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const { businessAreaSlug, programCode } = useBaseUrl();

  const canCreateProgramCycle =
    program.status === ProgramStatusEnum.ACTIVE &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  // The backend refuses to create a cycle while any cycle is still open, and a new
  // cycle has to start after the latest end date - so the only cycle that can be
  // missing an end date is the most recently created one. Read it here rather than
  // taking it from the table, whose page is filtered, sorted and paginated.
  const latestCycleParams = createApiParams(
    { businessAreaSlug, programCode },
    { ordering: '-created_at', limit: 1, offset: 0 },
  );
  const { data: latestCycleData, isFetching: isFetchingLatestCycle } =
    useQuery<PaginatedProgramCycleListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsCyclesList,
        latestCycleParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsCyclesList(latestCycleParams),
      enabled: open,
    });

  const handleClose = async () => {
    await queryClient.invalidateQueries({
      queryKey: restQueryKey(RestService.restBusinessAreasProgramsCyclesList),
      exact: false,
    });
    setOpen(false);
    setStep(0);
  };

  const handleNext = (): void => {
    setStep(step + 1);
  };

  const handleSubmit = (): void => {
    setOpen(false);
    setStep(0);
  };

  const latestCycle = latestCycleData?.results?.[0];
  const cycleNeedingEndDate =
    latestCycle && !latestCycle.endDate ? latestCycle : undefined;

  const stepsToRender = cycleNeedingEndDate
    ? [
        <UpdateProgramCycle
          program={program}
          programCycle={cycleNeedingEndDate}
          onClose={handleClose}
          onSubmit={handleNext}
          step={'1/2'}
          key={'updateProgramCycle'}
        />,
        <CreateProgramCycle
          program={program}
          onClose={handleClose}
          onSubmit={handleSubmit}
          step={'2/2'}
          key={'createProgramCycle'}
        />,
      ]
    : [
        <CreateProgramCycle
          program={program}
          onClose={handleClose}
          onSubmit={handleSubmit}
          key={'createProgramCycle'}
        />,
      ];

  return (
    <>
      <ButtonTooltip
        variant="outlined"
        color="primary"
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
        data-cy="button-add-new-programme-cycle"
        disabled={!canCreateProgramCycle}
        title="Require active programme and all cycles need to have an end date"
      >
        {t('ADD NEW PROGRAMME CYCLE')}
      </ButtonTooltip>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        {isFetchingLatestCycle ? (
          <LoadingComponent />
        ) : (
          stepsToRender[Math.min(step, stepsToRender.length - 1)]
        )}
      </Dialog>
    </>
  );
};

export default withErrorBoundary(AddNewProgramCycle, 'AddNewProgramCycle');
