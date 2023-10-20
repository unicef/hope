import { Button } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useCreateProgramMutation } from '../../../__generated__/graphql';
import { ProgramForm } from '../../forms/ProgramForm';

export const CreateProgram = (): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, { loading }] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const submitFormHandler = async (values): Promise<void> => {
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
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const renderSubmit = (submit): ReactElement => {
    return (
      <>
        <Button onClick={() => setOpen(false)}>Cancel</Button>
        <LoadingButton
          loading={loading}
          onClick={submit}
          type='submit'
          color='primary'
          variant='contained'
          data-cy='button-save'
        >
          {t('Save')}
        </LoadingButton>
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
};
