import { Formik } from 'formik';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import {
  GrievanceTicketQuery,
  useIndividualLazyQuery,
  useIndividualQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { LookUpButton } from '../../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';

interface LookUpReassignRoleProps {
  household?:
    | GrievanceTicketQuery['grievanceTicket']['household']
    | GrievanceTicketQuery['grievanceTicket']['individual']['householdsAndRoles'][number]['household'];
  individualToReassign: GrievanceTicketQuery['grievanceTicket']['individual'];
  initialSelectedIndividualId: string;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  individualRole: { role: string; id: string };
  shouldDisableButton?: boolean;
}

export function LookUpReassignRole({
  household,
  ticket,
  individualRole,
  shouldDisableButton,
  individualToReassign,
  initialSelectedIndividualId,
}: LookUpReassignRoleProps): React.ReactElement {
  const { t } = useTranslation();
  const [selectedIndividualId, setSelectedIndividualId] = useState<string>(
    initialSelectedIndividualId,
  );
  const { data: individualData, loading } = useIndividualQuery({
    variables: { id: selectedIndividualId },
  });
  console.log('initialSelectedIndividualId', selectedIndividualId);
  console.log('individualData zS', individualData?.individual?.unicefId);
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState<boolean>(false);
  const [selectedHousehold, setSelectedHousehold] =
    useState<LookUpReassignRoleProps['household']>(null);
  const [selectedIndividual, setSelectedIndividual] = useState(null);
  const [reAssigneeRole, setReAssigneeRole] = useState<{
    role;
    household;
    individual;
    new_individual;
  }>({
    household: null,
    individual: null,
    role: null,
    new_individual: null,
  });
  const [shouldUseMultiple, setShouldUseMultiple] = useState(false);
  // const [loadIndividual, { data: individualData, loading }] =
  //   useIndividualLazyQuery();

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
      case GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION:
        roleReassignData =
          ticket?.needsAdjudicationTicketDetails?.roleReassignData;
        setShouldUseMultiple(
          ticket?.needsAdjudicationTicketDetails?.selectedDuplicates?.length >
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
      setSelectedIndividualId(reAssigneeRole.new_individual);
      // loadIndividual({ variables: { id: reAssigneeRole.individual } });
    }
  }, [reAssigneeRole]);

  if (loading) return <LoadingComponent />;
  return (
    <Formik
      initialValues={{
        selectedIndividual: individualData.individual,
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
            individual={individualToReassign}
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
}
