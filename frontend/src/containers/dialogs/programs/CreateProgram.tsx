import { Button } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/AllPrograms';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { handleValidationErrors } from '../../../utils/utils';
import { useCreateProgramMutation } from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';

export function CreateProgram(): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const submitFormHandler = async (values, setFieldError): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            ...values,
            startDate: values.startDate,
            endDate: values.endDate,
            businessAreaSlug: businessArea,
          },
        },
      });
      showMessage('Programme created.', {
        pathname: `/${businessArea}/programs/${response.data.createProgram.program.id}`,
        historyMethod: 'push',
      });
    } catch (error) {
      const { nonValidationErrors } = handleValidationErrors(
        'createProgram',
        error,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Programme create action failed.'));
      }
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
    <div>
      <Button
        variant='contained'
        color='primary'
        onClick={() => setOpen(true)}
        data-cy='button-new-program'
      >
        {t('New Programme')}
      </Button>

      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        open={open}
        onClose={() => setOpen(false)}
        title={t('Set-up a new Programme')}
      />
    </div>
  );
}
