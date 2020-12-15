import { Formik } from 'formik';
import React, { useState } from 'react';
import {
  GrievanceTicketQuery,
  useIndividualQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { LookUpButton } from '../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';

export const LookUpReassignRole = ({
  household,
  ticket,
  individualRole,
  shouldDisableButton,
}: {
  household:
    | GrievanceTicketQuery['grievanceTicket']['household']
    | GrievanceTicketQuery['grievanceTicket']['individual']['householdsAndRoles'][number]['household'];
  ticket: GrievanceTicketQuery['grievanceTicket'];
  individualRole: { role: string; id: string };
  shouldDisableButton?: boolean;
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
  const reAssigneeRole = JSON.parse(
    ticket?.deleteIndividualTicketDetails?.roleReassignData,
  )[individualRole.id];

  const { data: individualData, loading } = useIndividualQuery({
    variables: { id: reAssigneeRole?.individual },
  });
  const [selectedHousehold, setSelectedHousehold] = useState(household || null);
  const [selectedIndividual, setSelectedIndividual] = useState(
    individualData?.individual || null,
  );

  if (loading) return <LoadingComponent />;

  return (
    <Formik
      initialValues={{
        selectedIndividual: individualData?.individual || null,
        selectedHousehold: household || null,
        role: individualRole.role,
      }}
      onSubmit={null}
    >
      {({ setFieldValue, values }) => (
        <>
          {values.selectedIndividual ? (
            <LookUpReassignRoleDisplay
              setLookUpDialogOpen={setLookUpDialogOpen}
              values={values}
              disabled={shouldDisableButton}
            />
          ) : (
            <LookUpButton
              title='Reassign Role'
              handleClick={() => setLookUpDialogOpen(true)}
            />
          )}
          <LookUpReassignRoleModal
            lookUpDialogOpen={lookUpDialogOpen}
            setLookUpDialogOpen={setLookUpDialogOpen}
            initialValues={values}
            onValueChange={setFieldValue}
            ticket={ticket}
            selectedIndividual={selectedIndividual}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            setSelectedIndividual={setSelectedIndividual}
          />
        </>
      )}
    </Formik>
  );
};
