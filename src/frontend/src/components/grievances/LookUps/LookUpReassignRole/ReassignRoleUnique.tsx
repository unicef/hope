import { Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  GrievanceTicketDocument,
  useReassignRoleGrievanceMutation,
} from '@generated/graphql';
import { Button } from '@mui/material';

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
  ticket,
  household,
  individual,
}): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const [mutate] = useReassignRoleGrievanceMutation();

  return (
    <Formik
      initialValues={{
        grievanceTicketId: ticket.id,
        selectedHousehold: household,
        selectedIndividual: individual,
        role: individualRole.role,
      }}
      onSubmit={async (values) => {
        try {
          await mutate({
            variables: {
              grievanceTicketId: id,
              householdId: values.selectedHousehold.id,
              individualId: values.selectedIndividual.id,
              role: values.role,
            },
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          showMessage('Role Reassigned');
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
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
        >
          {t('Reassign To Unique Individual')}
        </ReassignRoleButton>
      )}
    </Formik>
  );
}
