import { Button } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForChoicesDocument,
  useCreateProgramMutation,
  useProgramQuery,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { ProgramForm } from '../../forms/ProgramForm';
import { PageHeader } from '../../../components/core/PageHeader';
import { PaperContainer } from '../../../components/targeting/PaperContainer';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { decodeIdString } from '../../../utils/utils';
import { LoadingComponent } from '../../../components/core/LoadingComponent';

export const EditProgramPage = (): ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const { data, loading: loadingProgram } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate, { loading }] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id,
        },
        data: { program: updateProgram.program },
      });
    },
  });

  if (!data) return null;
  if (loadingProgram) return <LoadingComponent />;
  const { program } = data;

  const submitFormHandler = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            id,
            ...values,
            startDate: values.startDate,
            endDate: values.endDate,
            budget: parseFloat(values.budget).toFixed(2),
          },
          version: program.version,
        },
      });
      showMessage(t('Programme edited.'), {
        pathname: `/${baseUrl}/details/${response.data.updateProgram.program.id}`,
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const renderSubmit = (submit): ReactElement => {
    return (
      <>
        <Button onClick={() => console.log('cancel')}>Cancel</Button>
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
      <PageHeader title={t('Create Program')} />
      <PaperContainer>
        <ProgramForm
          onSubmit={submitFormHandler}
          renderSubmit={renderSubmit}
          title={t('Set-up a new Programme')}
        />
      </PaperContainer>
    </>
  );
};
