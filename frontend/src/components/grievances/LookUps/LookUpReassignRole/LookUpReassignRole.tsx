import { Formik } from 'formik';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../../utils/constants';
import {
  GrievanceTicketQuery,
  useIndividualLazyQuery,
} from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { LookUpButton } from '../../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';

interface LookUpReassignRoleProps {
  household?:
    | GrievanceTicketQuery['grievanceTicket']['household']
    | GrievanceTicketQuery['grievanceTicket']['individual']['householdsAndRoles'][number]['household'];
  individual: GrievanceTicketQuery['grievanceTicket']['individual'];
  ticket: GrievanceTicketQuery['grievanceTicket'];
  individualRole: { role: string; id: string };
  shouldDisableButton?: boolean;
}

export const LookUpReassignRole = ({
  household,
  ticket,
  individualRole,
  shouldDisableButton,
  individual,
}: LookUpReassignRoleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState<boolean>(false);
  const [selectedHousehold, setSelectedHousehold] = useState<
    LookUpReassignRoleProps['household']
  >(null);
  const [selectedIndividual, setSelectedIndividual] = useState(null);
  const [reAssigneeRole, setReAssigneeRole] = useState<{
    role;
    household;
    individual;
  }>({
    household: null,
    individual: null,
    role: null,
  });
  const [shouldUseMultiple, setShouldUseMultiple] = useState(false);
  const [
    loadIndividual,
    { data: individualData, loading },
  ] = useIndividualLazyQuery();

  useEffect(() => {
    setSelectedHousehold(household);
  }, [household]);

  useEffect(() => {
    if (selectedIndividual?.household) {
      setSelectedHousehold(selectedIndividual.household);
    }
  }, [selectedIndividual]);

  useEffect(() => {
    if (individualData?.individual) {
      setSelectedIndividual(individualData.individual);
    }
  }, [individualData]);

  useEffect(() => {
    const category = ticket.category?.toString();
    const issueType = ticket.issueType?.toString();

    let roleReassignData = null;
    switch (category) {
      case GRIEVANCE_CATEGORIES.DATA_CHANGE:
        if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
          roleReassignData =
            ticket?.deleteIndividualTicketDetails?.roleReassignData;
        } else if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
          roleReassignData =
            ticket?.individualDataUpdateTicketDetails?.roleReassignData;
        }
        break;
      case GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING:
        roleReassignData =
          ticket?.systemFlaggingTicketDetails?.roleReassignData;
        break;
      case GRIEVANCE_CATEGORIES.DEDUPLICATION:
        roleReassignData =
          ticket?.needsAdjudicationTicketDetails?.roleReassignData;
        setShouldUseMultiple(
          ticket?.needsAdjudicationTicketDetails?.selectedIndividuals?.length >
            0,
        );
        break;
      default:
        break;
    }
    const role = JSON.parse(roleReassignData)[individualRole.id];
    if (role) {
      setReAssigneeRole(role);
    }
  }, [ticket, individualRole]);

  useEffect(() => {
    if (reAssigneeRole?.individual) {
      loadIndividual({ variables: { id: reAssigneeRole.individual } });
    }
  }, [reAssigneeRole, loadIndividual]);

  if (loading) return <LoadingComponent />;

  return (
    <Formik
      initialValues={{
        selectedIndividual,
        selectedHousehold,
        role: individualRole.role,
      }}
      onSubmit={null}
    >
      {({ setFieldValue, values }) => (
        <>
          {selectedIndividual ? (
            <LookUpReassignRoleDisplay
              setLookUpDialogOpen={setLookUpDialogOpen}
              selectedHousehold={selectedHousehold}
              selectedIndividual={selectedIndividual}
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
            shouldUseMultiple={shouldUseMultiple}
            household={household}
          />
        </>
      )}
    </Formik>
  );
};
