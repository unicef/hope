import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { AuthorizedUsersOnlineListEdit } from '@components/periodicDataUpdates/AuthorizedUsersOnlineListEdit';
import { useBaseUrl } from '@hooks/useBaseUrl';
import React, { ReactElement } from 'react';
import { Formik } from 'formik';
import Button from '@mui/material/Button';
import { useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from '@hooks/useSnackBar';
import { showApiErrorMessages } from '@utils/utils';
import { RestService } from '@restgenerated/services/RestService';
import { useProgramContext } from 'src/programContext';
import { useTranslation } from 'react-i18next';

const EditAuthorizedUsersOnline = (): ReactElement => {
  const [selected, setSelected] = React.useState<string[]>([]);
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { id } = useParams<{ id: string }>();

  const { mutateAsync: updateAuthorizedUsers } = useMutation({
    mutationFn: (values: { authorizedUserIds: string[] }) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsUpdateAuthorizedUsersCreate(
        {
          businessAreaSlug: businessAreaSlug,
          programSlug: programSlug,
          id: id ? Number(id) : undefined,
          requestBody: { authorizedUsers: values.authorizedUserIds },
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Authorized users updated successfully.'));
      setSelected([]);
      queryClient.invalidateQueries({
        queryKey: ['authorizedUsersOnline', businessAreaSlug, programSlug],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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
    <Formik
      initialValues={{ authorizedUserIds: [] }}
      onSubmit={async (values, { setSubmitting }) => {
        await updateAuthorizedUsers(values);
        setSubmitting(false);
      }}
    >
      {({ setFieldValue, values, handleSubmit, isSubmitting }) => (
        <form onSubmit={handleSubmit}>
          <PageHeader
            title={`${t('Edit Authorized Users')} - Template ID: ${id}`}
            breadCrumbs={breadCrumbsItems}
          >
            <Button
              variant="contained"
              color="primary"
              type="submit"
              disabled={isSubmitting || values.authorizedUserIds.length === 0}
            >
              {t('Save')}
            </Button>
          </PageHeader>
          <BaseSection>
            <AuthorizedUsersOnlineListEdit
              setFieldValue={setFieldValue}
              selected={selected}
              setSelected={setSelected}
            />
          </BaseSection>
        </form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(
  EditAuthorizedUsersOnline,
  'EditAuthorizedUsersOnline',
);
