import { Formik } from 'formik';
import React, { useState } from 'react';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { LookUpButton } from '../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';

export const LookUpReassignRole = ({
  household,
}: {
  household: GrievanceTicketQuery['grievanceTicket']['household'];
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <Formik
      initialValues={{ selectedIndividual: null, selectedHousehold: null }}
      onSubmit={(values) => console.log(values)}
    >
      {({ submitForm, setFieldValue, values }) => (
        <>
          {values.selectedHousehold || values.selectedIndividual ? (
            <LookUpReassignRoleDisplay
              setLookUpDialogOpen={setLookUpDialogOpen}
              values={values}
              onValueChange={setFieldValue}
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
            // submitForm={submitForm}
          />
        </>
      )}
    </Formik>
  );
};
