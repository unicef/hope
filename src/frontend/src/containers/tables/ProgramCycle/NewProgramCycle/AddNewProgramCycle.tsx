import withErrorBoundary from '@components/core/withErrorBoundary';
import CreateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/CreateProgramCycle';
import UpdateProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/UpdateProgramCycle';
import { useBaseUrl } from '@hooks/useBaseUrl';
import AddIcon from '@mui/icons-material/Add';
import { Button, Dialog } from '@mui/material';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface AddNewProgramCycleProps {
  program: ProgramDetail;
  lastProgramCycle?: ProgramCycleList;
}

const AddNewProgramCycle = ({
  program,
  lastProgramCycle,
}: AddNewProgramCycleProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();

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
      <Button
        variant="outlined"
        color="primary"
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
        data-cy="button-add-new-programme-cycle"
      >
        {t('ADD NEW PROGRAMME CYCLE')}
      </Button>
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
