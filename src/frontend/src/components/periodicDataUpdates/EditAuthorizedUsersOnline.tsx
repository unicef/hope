import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { AuthorizedUsersOnline } from '@components/periodicDataUpdates/AuthorizedUsersOnline';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { useTranslation } from 'react-i18next';
import { ReactElement } from 'react';
import Button from '@mui/material/Button';

const EditAuthorizedUsersOnline = (): ReactElement => {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: beneficiaryGroup?.memberLabelPlural || t('Individuals'),
      to: `/${baseUrl}/population/individuals`,
    },
    {
      title: t('Edit Authorized Users'),
    },
  ];

  return (
    <>
      <PageHeader
        title={`${t('Edit Authorized Users')} - Template ID: 785528733`}
        breadCrumbs={breadCrumbsItems}
      >
        <Button variant="contained" color="primary">
          {t('Save')}
        </Button>
      </PageHeader>
      <BaseSection>
        <AuthorizedUsersOnline setFieldValue={() => {}} />
      </BaseSection>
    </>
  );
};

export default withErrorBoundary(
  EditAuthorizedUsersOnline,
  'EditAuthorizedUsersOnline',
);
