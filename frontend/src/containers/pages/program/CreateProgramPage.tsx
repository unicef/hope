import { Button } from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import {
  AllProgramsForChoicesDocument,
  useCreateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { BaseSection } from '../../../components/core/BaseSection';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { PageHeader } from '../../../components/core/PageHeader';
import { ProgramPartnerCard } from '../../../components/programs/CreateProgram/ProgramPartnerCard';
import { ProgramPartnersSection } from '../../../components/programs/CreateProgram/ProgramPartnersSection';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { ProgramForm } from '../../forms/ProgramForm';

export const CreateProgramPage = (): ReactElement => {
  const [step, setStep] = useState(0);
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate, { loading }] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const handleSubmit = async (values): Promise<void> => {
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
        pathname: `/${baseUrl}/details/${response.data.createProgram.program.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const renderActions = (submitHandler): ReactElement => {
    return (
      <>
        <Button component={Link} to={`/${baseUrl}/list`}>
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
    'To create a new Programme, please complete all required fields on the form below and save.',
  );

  const [partners, setPartners] = useState([
    { id: uuidv4() },
    { id: uuidv4() },
    { id: uuidv4() },
  ]);

  const handleAddNewPartner = (): void => {
    setPartners([...partners, { id: uuidv4() }]);
  };

  const handleDeleteProgramPartner = (id: string): void => {
    setPartners(partners.filter((item) => item.id !== id));
  };
  return (
    <>
      {step === 0 && (
        <>
          <PageHeader title={t('Create Programme')} />
          <BaseSection title={t('Details')} description={detailsDescription}>
            <>
              <ProgramForm
                actions={(submit) => renderActions(submit)}
                onSubmit={handleSubmit}
              />
            </>
          </BaseSection>
          <ProgramPartnersSection setStep={setStep} />
        </>
      )}
      {step === 1 && (
        <>
          <PageHeader
            title={t('Add Partners')}
            handleBack={() => setStep(0)}
            breadCrumbs={[
              {
                title: t('New Programme'),
                handleClick: () => setStep(0),
              },
            ]}
          >
            <Button
              onClick={() => handleAddNewPartner()}
              variant='outlined'
              color='primary'
              endIcon={<AddIcon />}
            >
              {t('Add Partner')}
            </Button>
          </PageHeader>
          {partners.map((partner) => (
            <ProgramPartnerCard
              key={partner.id}
              partner={partner}
              handleDeleteProgramPartner={handleDeleteProgramPartner}
            />
          ))}
        </>
      )}
    </>
  );
};
