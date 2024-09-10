import { Button, Dialog } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramQuery } from '@generated/graphql';
import AddIcon from '@mui/icons-material/Add';
import { CreateProgramCycle } from '@containers/tables/ProgramCycle/NewProgramCycle/CreateProgramCycle';
import { UpdateProgramCycle } from '@containers/tables/ProgramCycle/NewProgramCycle/UpdateProgramCycle';
import { ProgramCycle } from '@api/programCycleApi';
import { useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface AddNewProgramCycleProps {
  program: ProgramQuery['program'];
  programCycles?: ProgramCycle[];
}

export const AddNewProgramCycle = ({
  program,
  programCycles,
}: AddNewProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();

  const handleClose = async () => {
    await queryClient.invalidateQueries({
      queryKey: ['programCycles', businessArea, program.id],
    });
    setOpen(false);
  };

  const handleNext = (): void => {
    setStep(step + 1);
  };

  const handleSubmit = (): void => {
    setOpen(false);
  };

  const lastProgramCycle = programCycles[programCycles.length - 1];

  const stepsToRender = [];
  if (lastProgramCycle.end_date) {
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
