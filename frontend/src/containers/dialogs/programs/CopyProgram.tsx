import { Button, IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForChoicesDocument,
  ProgramQuery,
  useCopyProgramMutation,
} from '../../../__generated__/graphql';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { ProgramForm } from '../../forms/ProgramForm';

interface CopyProgramProps {
  program: ProgramQuery['program'];
}

export const CopyProgram = ({
  program,
}: CopyProgramProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate, { loading }] = useCopyProgramMutation();

  const {
    id,
    name,
    scope,
    startDate,
    endDate,
    description,
    budget,
    administrativeAreasOfImplementation,
    populationGoal,
    frequencyOfPayments,
    sector,
    cashPlus,
    individualDataNeeded,
  } = program;

  const initialValues: { [key: string]: string | boolean | number } = {
    id,
    name: `Copy of ${name}`,
    scope,
    startDate,
    endDate,
    description: description || '',
    budget: budget || 0,
    administrativeAreasOfImplementation:
      administrativeAreasOfImplementation || '',
    populationGoal: populationGoal || 0,
    frequencyOfPayments: frequencyOfPayments || 'REGULAR',
    sector,
    cashPlus: cashPlus || false,
    individualDataNeeded: individualDataNeeded ? 'YES' : 'NO',
  };

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
        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage('Programme created.', {
        pathname: `/${baseUrl}/details/${response.data.copyProgram.program.id}`,
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
    <>
      <IconButton onClick={() => setOpen(true)}>
        <FileCopy />
      </IconButton>
      <ProgramForm
        onSubmit={submitFormHandler}
        renderSubmit={renderSubmit}
        open={open}
        onClose={() => setOpen(false)}
        title={t('Copy Programme')}
        initialValues={initialValues}
      />
    </>
  );
};
