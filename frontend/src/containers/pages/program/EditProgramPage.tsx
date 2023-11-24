import { Button } from '@material-ui/core';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import {
  useProgramQuery,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { decodeIdString } from '../../../utils/utils';
import { ProgramForm } from '../../forms/ProgramForm';
import { BaseSection } from '../../../components/core/BaseSection';

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

  const handleSubmit = async (values): Promise<void> => {
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

  const renderActions = (submitHandler): ReactElement => {
    return (
      <>
        <Button component={Link} to={`/${baseUrl}/details/${id}`}>
          {t('Cancel')}
        </Button>
        <LoadingButton
          loading={loading}
          onClick={submitHandler}
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
  const detailsDescription = t(
    'To edit an existing Programme, please complete all required fields on the form below and save.',
  );

  return (
    <>
      <PageHeader title={`${t('Edit Programme')}: (${program.name})`} />
      {/* //TODO: fix */}
      <BaseSection title={t('Details')} description={detailsDescription}>
        <ProgramForm values={{}} />
      </BaseSection>
    </>
  );
};
