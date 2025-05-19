import { LoadingComponent } from '@core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { Formik } from 'formik';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LookUpButton } from '../../LookUpButton';
import { LookUpReassignRoleDisplay } from './LookUpReassignRoleDisplay';
import { LookUpReassignRoleModal } from './LookUpReassignRoleModal';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

interface LookUpReassignRoleProps {
  household?:
    | GrievanceTicketDetail['household']
    | GrievanceTicketDetail['individual']['rolesInHouseholds'][number]['household'];
  individualToReassign: GrievanceTicketDetail['individual'];
  initialSelectedIndividualId: string;
  ticket: GrievanceTicketDetail;
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
}: LookUpReassignRoleProps): ReactElement {
  const { t } = useTranslation();
  const [selectedIndividualId, setSelectedIndividualId] = useState<string>(
    initialSelectedIndividualId,
  );
  const { businessArea, programId } = useBaseUrl();

  const { data: individual, isLoading: loadingIndividual } =
    useQuery<IndividualDetail>({
      queryKey: [
        'businessAreaProgramIndividual',
        businessArea,
        programId,
        selectedIndividualId,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: selectedIndividualId,
        }),
    });
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

  useEffect(() => {
    setSelectedHousehold(household);
  }, [household]);

  useEffect(() => {
    if (selectedIndividual?.household) {
      setSelectedHousehold(selectedIndividual.household);
    }
  }, [selectedIndividual]);

  useEffect(() => {
    if (individual) {
      setSelectedIndividual(individual);
    }
  }, [individual]);

  useEffect(() => {
    const category = ticket.category?.toString();
    const issueType = ticket.issueType?.toString();

    let roleReassignData = null;
    switch (category) {
      case GRIEVANCE_CATEGORIES.DATA_CHANGE:
        if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
          roleReassignData = ticket?.ticketDetails?.roleReassignData;
        } else if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
          roleReassignData = ticket?.ticketDetails?.roleReassignData;
        }
        break;
      case GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING:
        roleReassignData = ticket?.ticketDetails?.roleReassignData;
        break;
      case GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION:
        roleReassignData = ticket?.ticketDetails?.roleReassignData;
        setShouldUseMultiple(
          ticket?.ticketDetails?.selectedDuplicates?.length > 0,
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

  if (loadingIndividual) return <LoadingComponent />;
  return (
    <Formik
      initialValues={{
        selectedIndividual: individual,
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
