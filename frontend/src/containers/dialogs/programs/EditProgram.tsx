import { Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/AllLogEntries';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { decodeIdString, handleValidationErrors } from '../../../utils/utils';
import {
  ProgramNode,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';

interface EditProgramProps {
  program: ProgramNode;
}

export function EditProgram({ program }: EditProgramProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(program.id),
          count: 5,
          businessArea,
        },
      },
    ],
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
    },
  });
  const submitFormHandler = async (values, setFieldError): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            id: program.id,
            ...values,
            startDate: values.startDate,
            endDate: values.endDate,
            budget: parseFloat(values.budget).toFixed(2),
          },
          version: program.version,
        },
      });
      showMessage(t('Programme edited.'), {
        pathname: `/${businessArea}/programs/${response.data.updateProgram.program.id}`,
      });
      setOpen(false);
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'updateProgram',
        e,
        setFieldError,
        showMessage,
      );
      nonValidationErrors.map((x) => showMessage(x.message));
    }
  };

  const renderSubmit = (submit): ReactElement => {
    return (
      <>
        <Button onClick={() => setOpen(false)}>Cancel</Button>
        <Button
          onClick={submit}
          type='submit'
          color='primary'
          variant='contained'
          data-cy='button-save'
        >
          {t('Save')}
        </Button>
      </>
    );
  };

  return (
    <span>
      <Button
        variant='outlined'
        color='primary'
        startIcon={<EditIcon />}
        onClick={() => setOpen(true)}
      >
        {t('EDIT PROGRAMME')}
      </Button>
      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        program={program}
        open={open}
        onClose={() => setOpen(false)}
        title={t('Edit Programme Details')}
      />
    </span>
  );
}
