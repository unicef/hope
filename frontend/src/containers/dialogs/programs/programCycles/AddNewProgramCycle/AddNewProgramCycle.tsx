import { Button, Dialog } from '@material-ui/core';
import { Add } from '@material-ui/icons';
import moment from 'moment';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  ProgramQuery,
  ProgramStatus,
  useCreateProgramCycleMutation,
  useUpdateProgramCycleMutation,
} from '../../../../../__generated__/graphql';
import { ALL_PROGRAM_CYCLES_QUERY } from '../../../../../apollo/queries/program/programcycles/AllProgramCycles';
import { useSnackbar } from '../../../../../hooks/useSnackBar';
import { today } from '../../../../../utils/utils';
import { AddNewProgramCycleOneStep } from './AddNewProgramCycleOneStep';
import { AddNewProgramCycleTwoSteps } from './AddNewProgramCycleTwoSteps';

interface AddNewProgramCycleProps {
  program: ProgramQuery['program'];
}

export const AddNewProgramCycle = ({
  program,
}: AddNewProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();

  const [
    mutateCreate,
    { loading: loadingCreate },
  ] = useCreateProgramCycleMutation();

  const [
    mutateUpdate,
    { loading: loadingUpdate },
  ] = useUpdateProgramCycleMutation();

  const validationSchemaNewProgramCycle = Yup.object().shape({
    newProgramCycleName: Yup.string()
      .required(t('Programme Cycle name is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    newProgramCycleStartDate: Yup.date()
      .required(t('Start Date is required'))
      .when(
        'previousProgramCycleEndDate',
        (previousProgramCycleEndDate, schema) =>
          previousProgramCycleEndDate &&
          schema.min(
            previousProgramCycleEndDate,
            `${t('Start date have to be greater than')} ${moment(
              previousProgramCycleEndDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
    newProgramCycleEndDate: Yup.date()
      .min(today, t('End Date cannot be in the past'))
      .when(
        'newProgramCycleStartDate',
        (newProgramCycleStartDate, schema) =>
          newProgramCycleStartDate &&
          schema.min(
            newProgramCycleStartDate,
            `${t('End date have to be greater than')} ${moment(
              newProgramCycleStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      )
      .max(program.endDate, t('End Date cannot be after Programme End Date')),
  });

  const validationSchemaPreviousProgramCycle = Yup.object().shape({
    previousProgramCycleEndDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'previousProgramCycleStartDate',
        (previousProgramCycleStartDate, schema) =>
          previousProgramCycleStartDate &&
          schema.min(
            previousProgramCycleStartDate,
            `${t('End date have to be greater than')} ${moment(
              previousProgramCycleStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
  });

  const handleCreate = async (values): Promise<void> => {
    try {
      await mutateCreate({
        variables: {
          programCycleData: {
            name: values.newProgramCycleName,
            startDate: values.newProgramCycleStartDate,
            endDate: values.newProgramCycleEndDate,
          },
        },
        refetchQueries: () => [{ query: ALL_PROGRAM_CYCLES_QUERY }],
        awaitRefetchQueries: true,
      });
      showMessage(t('Programme Cycle created.'), {
        dataCy: 'snackbar-program-cycle-create-success',
      });
      setOpen(false);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const programCycles = program.cycles.edges.map((x) => x.node);

  const getLastProgramCycle = (
    array,
  ): ProgramQuery['program']['cycles']['edges'][number]['node'] => {
    if (array.length > 0) {
      return array[array.length - 1];
    }
    return null;
  };

  const previousProgramCycle = getLastProgramCycle(programCycles);

  const handleUpdate = async (values): Promise<void> => {
    try {
      await mutateUpdate({
        variables: {
          programCycleData: {
            programCycleId: values.previousProgramCycleId,
            name: values.previousProgramCycleName,
            startDate: values.previousProgramCycleStartDate,
            endDate: values.previousProgramCycleEndDate,
          },
        },
        refetchQueries: () => [{ query: ALL_PROGRAM_CYCLES_QUERY }],
        awaitRefetchQueries: true,
      });
      showMessage(t('Programme Cycle updated.'), {
        dataCy: 'snackbar-program-cycle-update-success',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const showNewProgrammeCycleButton = program.status === ProgramStatus.Active;

  const showOneStepModal = Boolean(previousProgramCycle?.endDate);
  return (
    <>
      {showNewProgrammeCycleButton && (
        <Button
          startIcon={<Add />}
          variant='outlined'
          color='primary'
          data-cy='button-add-new-program-cycle'
          onClick={() => setOpen(true)}
        >
          {t('Add New Programme Cycle')}
        </Button>
      )}
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        {showOneStepModal ? (
          <AddNewProgramCycleOneStep
            open={open}
            setOpen={setOpen}
            loadingCreate={loadingCreate}
            handleCreate={handleCreate}
            previousProgramCycle={previousProgramCycle}
            validationSchemaNewProgramCycle={validationSchemaNewProgramCycle}
          />
        ) : (
          <AddNewProgramCycleTwoSteps
            open={open}
            setOpen={setOpen}
            loadingCreate={loadingCreate}
            loadingUpdate={loadingUpdate}
            previousProgramCycle={previousProgramCycle}
            handleCreate={handleCreate}
            handleUpdate={handleUpdate}
            validationSchemaPreviousProgramCycle={
              validationSchemaPreviousProgramCycle
            }
            validationSchemaNewProgramCycle={validationSchemaNewProgramCycle}
          />
        )}
      </Dialog>
    </>
  );
};
