import { Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button } from '@mui/material';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { GrievanceReassignRole } from '@restgenerated/models/GrievanceReassignRole';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { showApiErrorMessages } from '@utils/utils';

const ReassignRoleButton = styled(Button)`
  padding: 25px;
  margin-top: 25px;
  width: 100%;
  border: 1.5px solid #043e91;
  border-radius: 5px;
  color: #033f91;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 700;
  cursor: pointer;
  background: #fff;
`;

export function ReassignRoleUnique({
  individualRole,
  household,
  individual,
}: {
  individualRole: any;
  household: any;
  individual: any;
}): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams(); // This is the grievanceTicketId
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync: reassignRoleMutation, isPending: isReassigningRole } =
    useMutation({
      mutationFn: (formData: GrievanceReassignRole) =>
        RestService.restBusinessAreasGrievanceTicketsReassignRoleCreate({
          businessAreaSlug: businessArea,
          id: id,
          formData,
        }),
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: ['businessAreasGrievanceTicketsRetrieve', businessArea, id],
        });
        showMessage(t('Role Reassigned'));
      },
      onError: (error: any) => {
        const errorMessage =
          error?.body?.errors?.[0]?.message ||
          error?.body?.errors ||
          error?.message ||
          'An error occurred while reassigning role.';
        showMessage(errorMessage);
      },
    });

  return (
    <Formik
      initialValues={
        {
          // selectedHousehold: household, // Not needed if passed directly in onSubmit
          // selectedIndividual: individual, // Not needed if passed directly in onSubmit
          // role: individualRole.role, // Not needed if passed directly in onSubmit
        }
      }
      onSubmit={async () => {
        const requestBody: GrievanceReassignRole = {
          householdId: household.id, // Directly use prop
          individualId: individual.id, // Directly use prop
          role: individualRole.role, // Directly use prop
        };
        try {
          await reassignRoleMutation(requestBody);
        } catch (error) {
          showApiErrorMessages(error, showMessage);
        }
      }}
    >
      {({ submitForm }) => (
        <ReassignRoleButton
          type="submit"
          color="primary"
          onClick={submitForm}
          data-cy="button-submit"
          variant="contained"
          disabled={isReassigningRole}
        >
          {isReassigningRole
            ? t('Reassigning...')
            : t(`Reassign To Unique ${beneficiaryGroup?.memberLabel}`)}
        </ReassignRoleButton>
      )}
    </Formik>
  );
}
