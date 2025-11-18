import { ButtonTooltip } from '@components/core/ButtonTooltip';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CreateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/CreateProgramCycle';
import UpdateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/UpdateProgramCycle';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import AddIcon from '@mui/icons-material/Add';
import { Dialog } from '@mui/material';
import { RestService } from '@restgenerated/index';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

interface AddNewProgramCycleProps {
  lastProgramCycle?: ProgramCycleList;
}

const AddNewProgramCycle = ({
  lastProgramCycle,
}: AddNewProgramCycleProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { selectedProgram } = useProgramContext();

  const { data: program } = useQuery<ProgramDetail>({
    queryKey: ['program', businessArea, selectedProgram.slug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        slug: selectedProgram.slug,
      }),
  });

  if (!program) {
    return null;
  }

  const canCreateProgramCycle =
    selectedProgram.status === ProgramStatusEnum.ACTIVE &&
    hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_CREATE, permissions);

  const handleClose = async () => {
    await queryClient.invalidateQueries({
      queryKey: ['programCycles', businessArea, program.slug],
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

  const stepsToRender = [];
  if (lastProgramCycle.endDate) {
    stepsToRender.push(
      <CreateProgramCycle
        program={program}
        onClose={handleClose}
        onSubmit={handleSubmit}
        key={'createProgramCycle'}
      />,
    );
  } else {
    stepsToRender.push(
      <UpdateProgramCycle
        program={program}
        programCycle={lastProgramCycle}
        onClose={handleClose}
        onSubmit={handleNext}
        step={'1/2'}
        key={'updateProgramCycle'}
      />,
    );
    stepsToRender.push(
      <CreateProgramCycle
        program={program}
        onClose={handleClose}
        onSubmit={handleSubmit}
        step={'2/2'}
        key={'createProgramCycle'}
      />,
    );
  }

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
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        {stepsToRender.map((stepComponent, index) => {
          if (index === step) {
            return stepComponent;
          }
        })}
      </Dialog>
    </>
  );
};

export default withErrorBoundary(AddNewProgramCycle, 'AddNewProgramCycle');
