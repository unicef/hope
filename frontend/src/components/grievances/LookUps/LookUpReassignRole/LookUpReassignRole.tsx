import { Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../../utils/constants';
import {
  GrievanceTicketNode,
  useIndividualQuery,
} from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { LookUpButton } from '../../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';

export const LookUpReassignRole = ({
  household,
  ticket,
  individualRole,
  shouldDisableButton,
  individual,
}: {
  household?:
    | GrievanceTicketNode['household']
    | GrievanceTicketNode['individual']['householdsAndRoles'][number]['household'];
  individual: GrievanceTicketNode['individual'];
  ticket: GrievanceTicketNode;
  individualRole: { role: string; id: string };
  shouldDisableButton?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
  let roleReassignData = null;
  switch (ticket.category.toString()) {
    case GRIEVANCE_CATEGORIES.DATA_CHANGE:
      if (
        ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
      ) {
        roleReassignData =
          ticket?.deleteIndividualTicketDetails?.roleReassignData;
      } else if (
        ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
      ) {
        roleReassignData =
          ticket?.individualDataUpdateTicketDetails?.roleReassignData;
      }
      break;
    case GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING:
      roleReassignData = ticket?.systemFlaggingTicketDetails?.roleReassignData;
      break;
    case GRIEVANCE_CATEGORIES.DEDUPLICATION:
      roleReassignData =
        ticket?.needsAdjudicationTicketDetails?.roleReassignData;
      break;
    default:
      break;
  }
  const reAssigneeRole = JSON.parse(roleReassignData)[individualRole.id];

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
        selectedHousehold: individualData?.individual?.household || null,
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
              title={t('Reassign Role')}
              handleClick={() => setLookUpDialogOpen(true)}
            />
          )}
          <LookUpReassignRoleModal
            lookUpDialogOpen={lookUpDialogOpen}
            setLookUpDialogOpen={setLookUpDialogOpen}
            initialValues={values}
            onValueChange={setFieldValue}
            ticket={ticket}
            individual={individual}
            selectedIndividual={selectedIndividual}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            setSelectedIndividual={setSelectedIndividual}
            household={household}
          />
        </>
      )}
    </Formik>
  );
};
