import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { AuthorizedUsersOnline } from '@components/periodicDataUpdates/AuthorizedUsersOnline';
import { useBaseUrl } from '@hooks/useBaseUrl';
import React, { ReactElement } from 'react';
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
  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { id } = useParams<{ id: string }>();

  const { mutateAsync: updateAuthorizedUsers } = useMutation({
    mutationFn: (ids: string[]) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsUpdateAuthorizedUsersCreate(
        {
          businessAreaSlug: (selectedProgram as any)?.businessAreaSlug || '',
          programSlug: (selectedProgram as any)?.programSlug || '',
          id: id ? Number(id) : undefined,
          requestBody: { authorizedUsers: ids },
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Authorized users updated successfully.'));
      setSelected([]);
      queryClient.invalidateQueries({
        queryKey: [
          'authorizedUsersOnline',
          (selectedProgram as any)?.businessAreaSlug,
          (selectedProgram as any)?.programSlug,
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleSave = async () => {
    await updateAuthorizedUsers(selected);
  };
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
    <>
      <PageHeader
        title={`${t('Edit Authorized Users')} - Template ID: ${id}`}
        breadCrumbs={breadCrumbsItems}
      >
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={selected.length === 0}
        >
          {t('Save')}
        </Button>
      </PageHeader>
      <BaseSection>
        <AuthorizedUsersOnline
          setFieldValue={() => {}}
          selected={selected}
          setSelected={setSelected}
        />
      </BaseSection>
    </>
  );
};

export default withErrorBoundary(
  EditAuthorizedUsersOnline,
  'EditAuthorizedUsersOnline',
);
